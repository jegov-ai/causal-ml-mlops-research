import importlib.util,json,tempfile,unittest,zipfile
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('validation',ROOT/'paper1_experiments/gate_validation_v1.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class GateValidation(unittest.TestCase):
    def test_archive_seed_collision_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'reproducibility/archives').mkdir(parents=True)
            with zipfile.ZipFile(p/'reproducibility/archives/run.zip','w') as z:z.writestr('periods.csv','seed,value\n500000,1\n')
            with self.assertRaises(RuntimeError):v.scan_seeds(p,{500000})
            self.assertEqual(v.scan_seeds(p,{500001}),1)
    def test_malformed_seed_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'periods.csv').write_text('seed\n500000.5\n')
            with self.assertRaises(RuntimeError):v.scan_seeds(p,{500000})
    def test_primary_averages_within_seeds_and_keeps_benchmarks(self):
        rows=[];bench=[]
        for seed in [500000,500001]:
            for scenario in ['stable','response','opposing']:
                for period in [7,8]:
                    for budget in [2,4]:
                        for variant in ['frozen','refreshed']:
                            rows.append(dict(initial_seed=42,scenario=scenario,onset=7,seed=seed,method='M1',review_budget=budget,gate_variant=variant,period=period,regret=(3 if variant=='frozen' else (2 if seed==500000 else 4)),harmful_treatment_rate=0.,retrain_accepted=False))
                    for name in ['treat_all','treat_none','frozen_tlearner']:
                        bench.append(dict(initial_seed=42,scenario=scenario,onset=7,seed=seed,period=period,benchmark=name,regret=1.))
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);v.paired_analysis(pd.DataFrame(rows),pd.DataFrame(bench),p,'validation')
            primary=pd.read_csv(p/'primary_seed_differences.csv')
            self.assertEqual(len(primary),2);self.assertEqual(primary.equal_grid_mean_difference.tolist(),[-1.,1.])
            a=json.loads((p/'analysis.json').read_text());self.assertEqual(a['primary_mean_difference'],0.)
            self.assertEqual(a['independent_seeds'],2)
            self.assertEqual(len(pd.read_csv(p/'fixed_policy_comparisons.csv')),72)
if __name__=='__main__':unittest.main()
