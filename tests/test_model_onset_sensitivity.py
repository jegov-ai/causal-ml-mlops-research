"""Engineering checks. All generated windows use development fixture seed 409999."""
import importlib.util
from pathlib import Path
import tempfile
import shutil
import subprocess
import json
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'paper1_experiments'/file)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
v=module('sensitivity','model_onset_sensitivity_v1.py')
old=module('old_schedule','monitoring_schedule_comparison_v1.py')

class Model:
    def __init__(self,arm,shifted=False):self.arm,self.shifted=arm,shifted
    def predict(self,x):
        effect=np.where(x.age<35,5. if self.shifted else 40.,15.)
        return 50+.4*x.previous_spending.to_numpy()+self.arm*effect


def simulate(target,onset=7,truth_mutation=False):
    baseline=(Model(0),Model(1));candidate=(Model(0,True),Model(1,True))
    bg=v.make_window(409999,1,'stable',20)[v.FEATURES]
    ex=v.base.TwoFeatureShapley(baseline,bg);phi,_=ex.explain(bg)
    calls=[0]
    def scores(vector,center,scale):
        calls[0]+=1
        return {m:np.array([0. if m=='PERIODIC' or calls[0]<onset else 10.]) for m in target.METHODS}
    kwargs={'onset':onset} if target is v else {}
    generator=target.make_window
    def draw(*args,**kw):
        frame=generator(*args,**kw)
        if truth_mutation:frame.true_effect=-9999.
        return frame
    # Actual observed-data AIPW is retained for the truth-leak test.
    with patch.object(target,'monitor_scores',scores),patch.object(target,'fit_models',return_value=candidate),patch.object(target,'make_window',draw):
        return target.evaluate_stream(409999,'response',200,baseline,np.zeros(17),np.ones(17),
            {m:1. for m in target.METHODS},ex,bg,bg,phi,**kwargs)

class ModelOnsetSensitivity(unittest.TestCase):
    def test_historical_initial_data_and_generator_preserved(self):
        pd.testing.assert_frame_equal(v.initial_data(42),v.base.original_data())
        for scenario in v.SCENARIOS:
            for period in [1,6,7,12]:
                pd.testing.assert_frame_equal(v.make_window(409999,period,scenario,200,onset=7),v.base.make_window(409999,period,scenario,200))
        self.assertFalse(v.initial_data(42).equals(v.initial_data(1042)))

    def test_onset_only_changes_declared_trajectory(self):
        for onset in v.ONSETS:
            before=v.make_window(409999,onset-1,'response',200,onset)
            after=v.make_window(409999,onset,'response',200,onset)
            self.assertTrue((before.loc[before.age<35,'true_effect']==40).all())
            self.assertTrue((after.loc[after.age<35,'true_effect']==5).all())
        early=v.make_window(409999,5,'response',200,4);late=v.make_window(409999,5,'response',200,7)
        pd.testing.assert_frame_equal(early[['age','previous_spending','discount','propensity']],late[['age','previous_spending','discount','propensity']])
        for onset in v.ONSETS:
            pd.testing.assert_frame_equal(v.make_window(409999,9,'stable',200,onset),v.make_window(409999,9,'stable',200,7))
        with self.assertRaises(ValueError):v.make_window(409999,7,'stable',200,6)

    def test_no_duplicate_stable_replication_and_seed_roles_disjoint(self):
        for mode,expected in [('smoke',39),('development',117)]:
            config,starts=v.run_settings(mode);cells=list(v.configurations(config,starts))
            self.assertEqual(len(cells),expected);self.assertEqual(len(set(cells)),expected)
            stable=[x for x in cells if x[1]=='stable']
            self.assertTrue(all(x[2]==7 for x in stable))
            self.assertEqual(len(stable),3*config['test_runs'])
            sets=v.seed_sets(mode);self.assertEqual(sum(map(len,sets.values())),len(set.union(*sets.values())))
        self.assertFalse(set.union(*v.seed_sets('smoke').values()) & set.union(*v.seed_sets('development').values()))
        with self.assertRaises(ValueError):v.run_settings('study')

    def test_scores_isolate_signals(self):
        x=np.zeros((1,17));center=np.zeros(17);scale=np.ones(17)
        x[0,10]=9.;scores=v.monitor_scores(x,center,scale)
        self.assertEqual(scores['M0'][0],0);self.assertEqual(scores['M1'][0],0);self.assertEqual(scores['M2-FULL'][0],9)
        x[0,9]=7.;scores=v.monitor_scores(x,center,scale)
        self.assertEqual(scores['M0'][0],0);self.assertEqual(scores['M1'][0],7)
        self.assertEqual(scores['PERIODIC'][0],0)

    def test_controller_reproduces_frozen_schedule_at_onset7(self):
        oldrows,oldruns,oldbench=simulate(old);rows,runs,bench=simulate(v)
        a=pd.DataFrame(oldrows);b=pd.DataFrame(rows)
        columns=[c for c in b.columns if c!='onset']
        for method in ['M1','M2-FULL','PERIODIC']:
            pd.testing.assert_frame_equal(a[a.method==method][columns].reset_index(drop=True),b[b.method==method][columns].reset_index(drop=True))
        pd.testing.assert_frame_equal(pd.DataFrame(oldbench),pd.DataFrame(bench).drop(columns='onset'))

    def test_truth_cannot_change_controller_or_gate(self):
        one=pd.DataFrame(simulate(v,truth_mutation=False)[0]);two=pd.DataFrame(simulate(v,truth_mutation=True)[0])
        columns=['score','alert_issued','review_performed','retrain_accepted','gate_mean','gate_lower','treatment_rate']
        pd.testing.assert_frame_equal(one[columns],two[columns])
        self.assertFalse(one.regret.equals(two.regret))
        # Unmocked monitor vector is also truth-independent.
        data=v.make_window(409999,7,'response',100);other=data.copy();other.true_effect=-9999
        models=(Model(0),Model(1));ex=v.base.TwoFeatureShapley(models,data.iloc[:4])
        np.testing.assert_array_equal(v.monitor_vector(data,models,ex),v.monitor_vector(other,models,ex))

    def test_benchmarks_oracle_loss_and_next_window_timing(self):
        d=v.make_window(409999,7,'stable',200)
        self.assertEqual(v.decision_metrics(d,np.ones(len(d),dtype=bool))['regret'],0)
        changed=v.make_window(409999,4,'response',200,4)
        expected=np.mean(changed.age.lt(35))*5
        self.assertAlmostEqual(v.decision_metrics(changed,np.ones(len(changed),dtype=bool))['regret'],expected)
        # Strong exact pseudo-outcomes are a unit-test fixture only.
        with patch.object(v,'aipw_effect',side_effect=lambda data,models:data.true_effect.to_numpy()):
            frame=pd.DataFrame(simulate(v,onset=4)[0])
        part=frame.query("method=='M1' and review_budget==2")
        self.assertEqual(part.loc[part.review_performed,'period'].tolist(),[4,5])
        self.assertTrue(part.loc[part.period==4,'retrain_accepted'].iloc[0])
        self.assertGreater(part.loc[part.period==4,'regret'].iloc[0],0)
        self.assertEqual(part.loc[part.period==5,'regret'].iloc[0],0)
        for cap in v.REVIEW_BUDGETS:
            periodic=frame.query("method=='PERIODIC' and review_budget==@cap")
            self.assertEqual(periodic.loc[periodic.review_performed,'period'].tolist(),list(v.CALENDARS[cap]))

    def test_per_initial_calibration_does_not_reuse_centers(self):
        config=dict(n=20,scale_runs=3,calibration_runs=5,null_runs=3)
        starts=dict(scale=100,calibration=200,null=300)
        def vectors(seed,n,model,explainer):return np.tile(np.arange(17,dtype=float)+model+seed%7,(12,1))
        with patch.object(v,'stream_vectors',vectors):
            a=v.calibrate(config,starts,0,None);b=v.calibrate(config,starts,10,None)
        np.testing.assert_allclose(b[0]-a[0],10)
        self.assertEqual(len(a[4]),3*3);self.assertEqual(len(a[3]['M0']),5)
        _,scale=v.scale_statistics(np.zeros((36,17)))
        np.testing.assert_array_equal(scale,np.full(17,1e-8))

    def test_seed_scan_fails_on_recorded_or_malformed_seed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);pd.DataFrame({'seed':[420300]}).to_csv(p/'existing.csv',index=False)
            with self.assertRaisesRegex(RuntimeError,'already recorded'):v.scan_seeds(p,{420300})
            pd.DataFrame({'seed':['bad']}).to_csv(p/'existing.csv',index=False)
            with self.assertRaises(ValueError):v.scan_seeds(p,{420300})
            pd.DataFrame({'seed':[42]}).to_csv(p/'existing.csv',index=False)
            self.assertEqual(v.scan_seeds(p,{420300}),1)

    def test_preflight_requires_committed_intact_source_and_versions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);folder=root/'paper1_experiments';folder.mkdir();(root/'tests').mkdir()
            names=[*v.FROZEN,'model_onset_sensitivity_v1.py','MODEL_ONSET_SENSITIVITY_DEVELOPMENT_PROTOCOL_v1.md']
            for name in names:shutil.copyfile(ROOT/'paper1_experiments'/name,folder/name)
            shutil.copyfile(Path(__file__),root/'tests/test_model_onset_sensitivity.py')
            def git(*args):
                return subprocess.check_output(['git',*args],cwd=root,stderr=subprocess.STDOUT,text=True)
            git('init');git('add','.')
            git('-c','user.name=Engineering','-c','user.email=test@example.invalid','-c','commit.gpgsign=false','commit','-m','fixture')
            with patch.object(v,'__file__',str(folder/'model_onset_sensitivity_v1.py')),patch.object(v,'BASE_PATH',folder/'monitoring_signal_ablation_v1.py'):
                result=v.preflight('smoke',root/'reference')
                self.assertEqual(result['git_commit'],git('rev-parse','HEAD').strip())
                script=folder/'model_onset_sensitivity_v1.py';original=script.read_bytes();script.write_bytes(original+b'\n# dirty\n')
                with self.assertRaisesRegex(RuntimeError,'Tracked changes'):v.preflight('smoke',root/'reference')
                script.write_bytes(original)
                ref=root/'reference';ref.mkdir()
                (ref/'manifest.json').write_text(json.dumps(dict(mode='study',script_sha256=v.FROZEN['monitoring_signal_ablation_v1.py'],numpy='different',pandas='different',sklearn='different')))
                (ref/'checkpoint.json').write_text(json.dumps(dict(status='complete')))
                with self.assertRaisesRegex(RuntimeError,'differs'):v.preflight('development',ref)
                protocol=folder/'MODEL_ONSET_SENSITIVITY_DEVELOPMENT_PROTOCOL_v1.md';protocol.write_text(protocol.read_text()+'changed')
                with self.assertRaisesRegex(RuntimeError,'protocol changed'):v.preflight('smoke',ref)

if __name__=='__main__':unittest.main()
