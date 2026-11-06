"""Initial-model/onset sensitivity. Engineering smoke/development only."""
import argparse
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split

BASE_PATH = Path(__file__).with_name("monitoring_signal_ablation_v1.py")
spec = importlib.util.spec_from_file_location("sensitivity_frozen_base", BASE_PATH)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
FEATURES, PERIODS, COST = base.FEATURES, base.PERIODS, base.COST
SCENARIOS, REVIEW_BUDGETS = base.SCENARIOS, base.REVIEW_BUDGETS
METHODS = ("M0", "M1", "M2-FULL", "PERIODIC")
INITIAL_SEEDS, ONSETS = (42,1042,2042), (4,7,10)
CALENDARS = {2:(4,8),4:(3,6,9,12),8:(1,3,4,6,7,9,10,12)}
FROZEN = {
 "monitoring_signal_ablation_v1.py":"47a5d523ea995b6a7697759f0217c3e7342513b4585de476f44e2adcaede000f",
 "integrated_causal_monitoring_v2_xai.py":"0cec23bce14c8c865678cf0ed152bf85ee2f4c4a1d87922f21a19448eb528fca",
 "monitoring_schedule_comparison_v1.py":"ebcf8962e8776f5c850e4d0cc20f7885513cdc1a2c5ba017e6f0a04a8dae768c"}
PROTOCOL_HASH = "a722024333bb7b84116bf6b727f8d105c391a80b641687241730be975b1e8ea2"
fit_models, outcomes, policy = base.fit_models, base.outcomes, base.policy
aipw_effect, decision_metrics = base.aipw_effect, base.decision_metrics
monitor_vector = base.monitor_vector


def initial_data(seed):
    rng = np.random.default_rng(seed)
    age = rng.integers(18,66,size=1000)
    spending = np.clip(rng.normal(200,60,1000),0,None)
    treatment = rng.binomial(1,.5,1000)
    effect = np.where(age<35,40.,15.)
    noise = rng.normal(0,20,1000)
    return pd.DataFrame(dict(age=age, previous_spending=spending, discount=treatment,
        purchase_amount=50+.4*spending+noise+treatment*effect,
        propensity=.5,true_effect=effect))


def make_window(seed,period,scenario,n,onset=7):
    if onset not in ONSETS:
        raise ValueError("Unsupported onset")
    if scenario not in SCENARIOS or n<20 or not 1<=period<=PERIODS:
        raise ValueError("Invalid window configuration")
    rng=np.random.default_rng(np.random.SeedSequence([seed,period]))
    shifted=period>=onset
    share=.65 if scenario=="covariate" and shifted else base.YOUNG_SHARE
    young=rng.random(n)<share
    age=np.where(young,rng.integers(18,35,n),rng.integers(35,66,n))
    spending=np.clip(rng.normal(200,60,n),0,None)
    propensity=np.full(n,.5)
    if scenario=="assignment" and shifted:propensity=np.where(young,.2,.8)
    treatment=(rng.random(n)<propensity).astype(int)
    effect=np.where(young,40.,15.)
    if shifted and scenario=="response":effect=np.where(young,5.,15.)
    if shifted and scenario=="opposing":
        older=15.+35.*base.YOUNG_SHARE/(1.-base.YOUNG_SHARE)
        effect=np.where(young,5.,older)
    outcome=50+.4*spending+rng.normal(0,20,n)+treatment*effect
    return pd.DataFrame(dict(age=age,previous_spending=spending,discount=treatment,
        purchase_amount=outcome,propensity=propensity,true_effect=effect))


def monitor_scores(vectors,center,scale):
    z=np.abs((vectors-center)/scale)
    return {"M0":z[:,:9].max(axis=1),"M1":z[:,:10].max(axis=1),
            "M2-FULL":z[:,:13].max(axis=1),"PERIODIC":np.zeros(len(vectors))}


def evaluate_stream(seed, scenario, n, baseline, center, scale, thresholds,
                    explainer, background, anchors, baseline_phi, onset=7):
    if onset not in ONSETS:
        raise ValueError("Unsupported onset")
    states = {(method, budget): {
        "model": baseline, "alerts": 0, "started": False,
        "reviews": 0, "accepted": 0, "first_detection": None,
    } for method in METHODS for budget in REVIEW_BUDGETS}
    records = []
    benchmarks = []
    for period in range(1, PERIODS + 1):
        data = make_window(seed, period, scenario, n, onset=onset)
        vector = monitor_vector(data, baseline, explainer)
        scores = monitor_scores(vector[None, :], center, scale)
        prediction_cache = {}

        def cached_outcomes(models):
            key = id(models)
            if key not in prediction_cache:
                prediction_cache[key] = outcomes(models, data)
            return prediction_cache[key]

        baseline_mu0, baseline_mu1 = cached_outcomes(baseline)
        # All incumbent decisions are scored before current outcomes are used.
        for name, action in (
            ("treat_all", np.ones(n, dtype=bool)),
            ("treat_none", np.zeros(n, dtype=bool)),
            ("frozen_tlearner", (baseline_mu1 - baseline_mu0) > COST),
        ):
            benchmarks.append(dict(seed=seed, scenario=scenario, period=period,
                                   benchmark=name, **decision_metrics(data, action)))
        pending_records = []
        for (method, budget), st in states.items():
            mu0, mu1 = cached_outcomes(st["model"])
            action = (mu1 - mu0) > COST
            cate_error = float(np.mean(
                ((mu1 - mu0) - data.true_effect.to_numpy()) ** 2
            ) ** .5)
            score = float(scores[method][0])
            issue = method != "PERIODIC" and score > thresholds[method] and st["alerts"] < 2
            if issue:
                st["alerts"] += 1
                st["started"] = True
                if (scenario != "stable" and period >= onset
                        and st["first_detection"] is None):
                    st["first_detection"] = period
            review = (period in CALENDARS[budget] if method == "PERIODIC"
                      else st["started"] and st["reviews"] < budget)
            row = dict(
                seed=seed, scenario=scenario, period=period,
                method=method, review_budget=budget,
                score=score, threshold=thresholds[method],
                alert_issued=bool(issue), review_performed=bool(review),
                retrain_accepted=False, gate_mean=np.nan, gate_lower=np.nan,
                cate_rmse=cate_error, **decision_metrics(data, action),
            )
            pending_records.append((row, st))
        # A common candidate and common holdout are shared across all arms.
        # Cache avoids repeated actual fitting; per-arm reviews are still counted.
        if any(row["review_performed"] for row, _ in pending_records):
            strata = (data.age.lt(35).astype(int) * 2 + data.discount)
            training, gate = train_test_split(
                data, test_size=.30, stratify=strata,
                random_state=seed + period,
            )
            candidate = fit_models(training, seed + period)
            candidate_action = policy(candidate, gate)
            # Baseline nuisance models are independent of this gate dataset.
            net_pseudo = aipw_effect(gate, baseline) - COST
            gate_cache = {}
            for row, st in pending_records:
                if not row["review_performed"]:
                    continue
                st["reviews"] += 1
                key = id(st["model"])
                if key not in gate_cache:
                    gate_cache[key] = policy(st["model"], gate)
                incumbent_action = gate_cache[key]
                gain = (candidate_action.astype(float)
                        - incumbent_action.astype(float)) * net_pseudo
                mean = float(gain.mean())
                lower = mean - 1.96 * float(gain.std(ddof=1)) / np.sqrt(len(gain))
                row.update(gate_mean=mean, gate_lower=lower)
                if lower > 0:
                    st["model"] = candidate
                    st["accepted"] += 1
                    row["retrain_accepted"] = True
        records.extend(row for row, _ in pending_records)
    rows = pd.DataFrame(records)
    summaries = []
    for (method, budget), st in states.items():
        part = rows[(rows.method == method) & (rows.review_budget == budget)]
        post = part.loc[part.period >= onset]
        detection = st["first_detection"]
        summaries.append(dict(
            seed=seed, scenario=scenario, method=method, review_budget=budget,
            alerts=st["alerts"], any_alert=int(st["alerts"] > 0),
            reviews=st["reviews"], accepted_retrains=st["accepted"],
            prechange_regret=part.loc[part.period < onset, "regret"].sum(),
            postchange_regret=post.regret.sum(),
            postchange_regret_per_window=post.regret.mean(),
            post_windows=len(post),
            mean_cate_rmse=post.cate_rmse.mean(),
            harmful_treatment_rate=post.harmful_treatment_rate.mean(),
            change_detected=(int(detection is not None)
                             if scenario != "stable" and method != "PERIODIC" else np.nan),
            detection_delay=(detection - onset if detection is not None else np.nan),
        ))
    for collection in (records,summaries,benchmarks):
        for row in collection: row["onset"]=onset
    return records, summaries, benchmarks


def run_settings(mode):
    if mode=="smoke":
        return dict(n=200,scale_runs=3,calibration_runs=5,null_runs=3,test_runs=1),dict(scale=410010,calibration=410100,null=410200,evaluation=410300)
    if mode=="development":
        return dict(n=1000,scale_runs=10,calibration_runs=40,null_runs=20,test_runs=3),dict(scale=420010,calibration=420100,null=420200,evaluation=420300)
    raise ValueError("Only engineering smoke/development modes exist")


def seed_sets(mode):
    config,starts=run_settings(mode)
    return {name:set(range(starts[name],starts[name]+config[count])) for name,count in
        [("scale","scale_runs"),("calibration","calibration_runs"),("null","null_runs"),("evaluation","test_runs")]}


def configurations(config,starts):
    for initial_seed in INITIAL_SEEDS:
        for scenario in SCENARIOS:
            for onset in ((7,) if scenario=="stable" else ONSETS):
                for seed in range(starts["evaluation"],starts["evaluation"]+config["test_runs"]):
                    yield initial_seed,scenario,onset,seed


def scan_seeds(root,planned):
    count=0
    for path in root.rglob("*.csv"):
        if any(part in (".git",".venv","venv","__pycache__") for part in path.parts):continue
        columns=pd.read_csv(path,nrows=0).columns
        selected=[c for c in ("seed","stream_seed") if c in columns]
        if not selected:continue
        count+=1
        with pd.read_csv(path,usecols=selected,chunksize=100000) as reader:
            for chunk in reader:
                for col in selected:
                    values=pd.to_numeric(chunk[col],errors="raise").dropna()
                    if values.isin(planned).any():
                        raise RuntimeError(f"Proposed stream seed already recorded: {path}")
    return count


def preflight(mode,reference):
    root=Path(__file__).resolve().parents[1]
    for name,digest in FROZEN.items():
        if hashlib.sha256(BASE_PATH.with_name(name).read_bytes()).hexdigest()!=digest:
            raise RuntimeError(f"Frozen historical source changed: {name}")
    protocol=BASE_PATH.with_name("MODEL_ONSET_SENSITIVITY_DEVELOPMENT_PROTOCOL_v1.md")
    if hashlib.sha256(protocol.read_text(encoding="utf-8").encode("utf-8")).hexdigest()!=PROTOCOL_HASH:
        raise RuntimeError("Development protocol changed")
    tracked=[Path(__file__).resolve(),protocol,root/"tests/test_model_onset_sensitivity.py"]
    for path in tracked:
        subprocess.check_call(["git","ls-files","--error-unmatch",path.relative_to(root).as_posix()],cwd=root,stdout=subprocess.DEVNULL)
    if subprocess.check_output(["git","status","--porcelain","--untracked-files=no"],cwd=root,text=True).strip():
        raise RuntimeError("Tracked changes exist; commit intended files first")
    versions=dict(numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__)
    if mode=="development":
        ref=json.loads((reference/"manifest.json").read_text())
        if ref.get("mode")!="study" or ref.get("script_sha256")!=FROZEN[BASE_PATH.name]:
            raise RuntimeError("Invalid historical reference")
        if json.loads((reference/"checkpoint.json").read_text())["status"]!="complete":raise RuntimeError("Incomplete reference")
        for k,value in versions.items():
            if ref[k]!=value:raise RuntimeError(f"{k} differs from historical environment")
    sets=seed_sets(mode)
    if sum(map(len,sets.values()))!=len(set.union(*sets.values())):raise RuntimeError("Seed roles overlap")
    checked=scan_seeds(root,set.union(*sets.values()))
    return dict(git_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip(),
        versions=versions,python=sys.version,platform=platform.platform(),seed_csv_files_checked=checked,
        protocol_sha256=PROTOCOL_HASH,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        frozen_hashes=FROZEN)


def stream_vectors(seed,n,baseline,explainer):
    return np.asarray([monitor_vector(make_window(seed,p,"stable",n),baseline,explainer) for p in range(1,PERIODS+1)])


def scale_statistics(vectors):
    return vectors.mean(axis=0),np.maximum(vectors.std(axis=0,ddof=1),1e-8)


def calibrate(config,starts,baseline,explainer):
    values=np.concatenate([stream_vectors(seed,config["n"],baseline,explainer)
        for seed in range(starts["scale"],starts["scale"]+config["scale_runs"])])
    center,scale=scale_statistics(values)
    maxima={m:[] for m in METHODS if m!="PERIODIC"}
    for seed in range(starts["calibration"],starts["calibration"]+config["calibration_runs"]):
        scores=monitor_scores(stream_vectors(seed,config["n"],baseline,explainer),center,scale)
        for method in maxima:maxima[method].append(float(scores[method].max()))
    thresholds={m:float(np.quantile(v,.95,method="higher")) for m,v in maxima.items()}
    thresholds["PERIODIC"]=0.
    null=[]
    for seed in range(starts["null"],starts["null"]+config["null_runs"]):
        scores=monitor_scores(stream_vectors(seed,config["n"],baseline,explainer),center,scale)
        for method in maxima:null.append(dict(seed=seed,method=method,any_alert=int(np.any(scores[method]>thresholds[method]))))
    return center,scale,thresholds,maxima,null


def paired_contrasts(runs,benchmarks):
    keys=["initial_seed","scenario","onset","seed"]
    b=benchmarks.loc[benchmarks.period>=benchmarks.onset].groupby(keys+["benchmark"]).regret.agg(["sum","mean"]).reset_index()
    result=[]
    for row in runs.to_dict("records"):
        matches=b
        for key in keys:matches=matches[matches[key]==row[key]]
        for other in matches.to_dict("records"):
            result.append({**{k:row[k] for k in keys},"review_budget":row["review_budget"],
                "comparison":row["method"]+" minus "+other["benchmark"],
                "cumulative_difference":row["postchange_regret"]-other["sum"],
                "per_window_difference":row["postchange_regret_per_window"]-other["mean"]})
    pairs=[("M2-FULL","M1"),("M1","M0"),("M0","PERIODIC"),("M1","PERIODIC"),("M2-FULL","PERIODIC")]
    for key,g in runs.groupby(keys+["review_budget"]):
        by=g.set_index("method")
        for left,right in pairs:
            result.append({**dict(zip(keys+["review_budget"],key)),"comparison":left+" minus "+right,
                "cumulative_difference":by.loc[left,"postchange_regret"]-by.loc[right,"postchange_regret"],
                "per_window_difference":by.loc[left,"postchange_regret_per_window"]-by.loc[right,"postchange_regret_per_window"]})
    return pd.DataFrame(result)


def audit_outputs(periods,runs,benchmarks,expected):
    keys=["initial_seed","scenario","onset","seed","method","review_budget"]
    if len(runs)!=expected*len(METHODS)*len(REVIEW_BUDGETS) or len(periods)!=len(runs)*PERIODS:
        raise RuntimeError("Incomplete factor coverage")
    if periods.duplicated(keys+["period"]).any() or runs.duplicated(keys).any():raise RuntimeError("Duplicate output keys")
    if not periods.groupby(keys).size().eq(PERIODS).all():raise RuntimeError("Incomplete windows")
    if not (runs.reviews<=runs.review_budget).all() or not (runs.alerts<=2).all():raise RuntimeError("Exceeded resource cap")
    summed=periods.loc[periods.period>=periods.onset].groupby(keys).regret.sum()
    if not np.allclose(summed.reindex(runs.set_index(keys).index),runs.postchange_regret):raise RuntimeError("Regret aggregation mismatch")
    if len(benchmarks)!=expected*PERIODS*3:raise RuntimeError("Incomplete benchmark coverage")
    for _,part in periods.groupby(keys):
        part=part.sort_values("period");issued=0;started=False;reviews=0
        for row in part.itertuples():
            issue=row.method!="PERIODIC" and row.score>row.threshold and issued<2
            if issue:issued+=1;started=True
            review=(row.period in CALENDARS[row.review_budget]) if row.method=="PERIODIC" else started and reviews<row.review_budget
            if issue!=row.alert_issued or review!=row.review_performed:raise RuntimeError("Controller schedule mismatch")
            if review:reviews+=1
            if row.retrain_accepted and (not review or not row.gate_lower>0):raise RuntimeError("Invalid accepted update")
    return dict(complete_factor_counts=True,unique_keys=True,windows=True,caps=True,
        period_to_run_regret=True,benchmark_coverage=True,controller_schedules=True,recorded_gate_acceptance=True)


def write_json(path,value):
    temporary=path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(value,indent=2,allow_nan=False),encoding="utf-8")
    os.replace(temporary,path)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode",choices=("smoke","development"),default="smoke")
    parser.add_argument("--preflight-only",action="store_true")
    parser.add_argument("--reference",type=Path,default=BASE_PATH.parent/"monitoring_signal_ablation_v1_study/run_20261102_012152")
    args=parser.parse_args()
    provenance=preflight(args.mode,args.reference)
    print("PREFLIGHT PASSED:",provenance,flush=True)
    if args.preflight_only:
        print("No evaluation data generated.");return
    config,starts=run_settings(args.mode)
    output=BASE_PATH.parent/("model_onset_sensitivity_v1_"+args.mode)/("run_"+datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    output.mkdir(parents=True,exist_ok=False)
    (output/"script_snapshot.py").write_bytes(Path(__file__).read_bytes())
    protocol=BASE_PATH.with_name("MODEL_ONSET_SENSITIVITY_DEVELOPMENT_PROTOCOL_v1.md")
    (output/"protocol_snapshot.md").write_bytes(protocol.read_bytes())
    for name in FROZEN:(output/(name+".snapshot")).write_bytes(BASE_PATH.with_name(name).read_bytes())
    manifest={**provenance,"mode":args.mode,"configuration":config,"starts":starts,
        "initial_seeds":list(INITIAL_SEEDS),"onsets":list(ONSETS),"calendars":CALENDARS,
        "created_utc":datetime.now(timezone.utc).isoformat(),"status":"running",
        "scope":"Engineering development only; no inferential study or independent-fit population claim.",
        "pairing":"Same stream seeds across initial fits and onsets; stable evaluated once at onset marker7.",
        "xai":"Frozen live summaries computed but excluded from scores; incumbent explanation audits omitted."}
    write_json(output/"launch.json",manifest);write_json(output/"checkpoint.json",dict(status="running",completed_configurations=0))
    print("OUTPUT:",output.resolve(),flush=True)
    started=time.perf_counter();times=[];records=[];run_records=[];bench_records=[]
    configurations_list=list(configurations(config,starts));done=0
    for initial_seed in INITIAL_SEEDS:
        phase=time.perf_counter()
        train,test=train_test_split(initial_data(initial_seed),test_size=.2,random_state=42)
        baseline=fit_models(train,initial_seed)
        background=pd.concat([train.loc[train.age<35,FEATURES].sample(n=8,random_state=123),
            train.loc[train.age>=35,FEATURES].sample(n=8,random_state=456)],ignore_index=True)
        explainer=base.TwoFeatureShapley(baseline,background)
        background.to_csv(output/f"background_{initial_seed}.csv",index=False)
        write_json(output/f"initial_model_{initial_seed}.json",dict(train_n=len(train),test_n=len(test),
            initial_seed=initial_seed,**decision_metrics(test,policy(baseline,test))))
        setup=time.perf_counter()-phase;phase=time.perf_counter()
        center,scale,thresholds,maxima,null=calibrate(config,starts,baseline,explainer)
        pd.DataFrame(dict(signal=base.SIGNAL_NAMES,center=center,scale=scale)).to_csv(output/f"calibration_{initial_seed}.csv",index=False)
        write_json(output/f"thresholds_{initial_seed}.json",thresholds)
        write_json(output/f"calibration_maxima_{initial_seed}.json",maxima)
        for row in null:row["initial_seed"]=initial_seed
        pd.DataFrame(null).to_csv(output/f"heldout_null_{initial_seed}.csv",index=False)
        calibration=time.perf_counter()-phase;phase=time.perf_counter()
        for fit,scenario,onset,seed in configurations_list:
            if fit!=initial_seed:continue
            rows,runs,benchmarks=evaluate_stream(seed,scenario,config["n"],baseline,center,scale,thresholds,
                explainer,None,None,None,onset=onset)
            for collection in (rows,runs,benchmarks):
                for row in collection:row["initial_seed"]=initial_seed
            records.extend(rows);run_records.extend(runs);bench_records.extend(benchmarks);done+=1
            # Preserve complete partial outputs before marking a checkpoint complete.
            pd.DataFrame(records).to_csv(output/"period_log.csv",index=False)
            pd.DataFrame(run_records).to_csv(output/"run_results.csv",index=False)
            pd.DataFrame(bench_records).to_csv(output/"benchmarks.csv",index=False)
            write_json(output/"checkpoint.json",dict(status="running",completed_configurations=done,total_configurations=len(configurations_list)))
            print(f"Completed {done}/{len(configurations_list)}: fit={fit} {scenario} onset={onset} seed={seed}",flush=True)
        times.append(dict(initial_seed=initial_seed,setup_seconds=setup,calibration_seconds=calibration,evaluation_seconds=time.perf_counter()-phase))
    periods=pd.DataFrame(records);runs=pd.DataFrame(run_records);benchmarks=pd.DataFrame(bench_records)
    checks=audit_outputs(periods,runs,benchmarks,len(configurations_list))
    paired_contrasts(runs,benchmarks).to_csv(output/"paired_development_contrasts.csv",index=False)
    groups=["initial_seed","scenario","onset","method","review_budget"]
    runs.groupby(groups).agg(seeds=("seed","nunique"),mean_loss_per_window=("postchange_regret_per_window","mean"),
        mean_cumulative_loss=("postchange_regret","mean"),mean_reviews=("reviews","mean"),
        mean_alerts=("alerts","mean"),mean_accepted_updates=("accepted_retrains","mean")).reset_index().to_csv(output/"summary.csv",index=False)
    write_json(output/"audit_checks.json",checks)
    manifest.update(status="complete",elapsed_seconds=time.perf_counter()-started,phase_times=times,
        stream_configurations=len(configurations_list),period_rows=len(periods),run_rows=len(runs),benchmark_rows=len(benchmarks))
    write_json(output/"manifest.json",manifest)
    write_json(output/"checkpoint.json",dict(status="complete",manifest="manifest.json"))
    print("COMPLETE:",output.resolve());print("Elapsed minutes:",round(manifest["elapsed_seconds"]/60,2))


if __name__=="__main__":main()
