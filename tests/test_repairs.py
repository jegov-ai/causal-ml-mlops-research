"""Regression checks. Run from project root: python -m unittest discover -s tests -v"""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('latest', ROOT/'paper1_experiments/integrated_causal_monitoring_v2_xai.py')
v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)

class ExactModel:
    def __init__(self, arm, shifted=False): self.arm, self.shifted = arm, shifted
    def predict(self, frame):
        effect = np.where(frame.age < 35, 5. if self.shifted else 40., 15.)
        return 50 + .4 * frame.previous_spending.to_numpy() + self.arm * effect

class Repairs(unittest.TestCase):
    def test_original_generator_reproduces_saved_customers(self):
        saved=pd.read_csv(ROOT/'customers.csv')
        pd.testing.assert_frame_equal(v.original_data()[saved.columns], saved, check_exact=False, atol=1e-10)
    def test_declared_age_effects_and_shift(self):
        for scenario in v.SCENARIOS:
            for period in (1,7):
                d=v.make_window(42,period,scenario,1000)
                np.testing.assert_array_equal(d.true_effect,v.oracle_effect_for_audit(d,period,scenario))
        d=v.make_window(42,7,'response',1000)
        self.assertTrue((d.loc[d.age<35,'true_effect']==5).all())
    def test_opposing_population_ate(self):
        q=v.YOUNG_SHARE
        self.assertAlmostEqual(q*40+(1-q)*15,q*5+(1-q)*(15+35*q/(1-q)))
    def test_invalid_scenario_rejected(self):
        with self.assertRaises(ValueError): v.make_window(1,7,'respnose',100)
    def test_invalid_propensity_rejected(self):
        d=v.make_window(1,1,'stable',100);d.propensity=0.
        with self.assertRaises(ValueError):v.aipw_effect(d,(ExactModel(0),ExactModel(1)))
    def test_shapley_known_function(self):
        d=v.make_window(1,1,'stable',40);models=(ExactModel(0),ExactModel(1))
        e=v.TwoFeatureShapley(models,d)
        phi,error=e.explain(d)
        np.testing.assert_allclose(phi[:,0],d.true_effect-d.true_effect.mean(),atol=1e-10)
        np.testing.assert_allclose(phi[:,1],0,atol=1e-10);self.assertLess(error,1e-8)
    def test_oracle_decision_regret(self):
        d=v.make_window(1,7,'response',100)
        self.assertAlmostEqual(v.decision_metrics(d,d.true_effect.to_numpy()>v.COST)['regret'],0)
    def test_truth_not_used_for_training_or_monitor(self):
        d=v.make_window(1,1,'stable',100);other=d.copy();other.true_effect=-9999
        a=v.fit_models(d,12);b=v.fit_models(other,12)
        np.testing.assert_array_equal(v.estimated_effect(a,d),v.estimated_effect(b,d))
        e=v.TwoFeatureShapley(a,d.iloc[:4])
        np.testing.assert_allclose(v.monitor_vector(d,a,e),v.monitor_vector(other,a,e))
    def test_update_affects_next_period_and_caps(self):
        baseline=(ExactModel(0),ExactModel(1));candidate=(ExactModel(0,True),ExactModel(1,True))
        bg=v.make_window(70000,1,'stable',20)[v.FEATURES];anchors=v.make_window(70001,1,'stable',20)[v.FEATURES]
        ex=v.TwoFeatureShapley(baseline,bg);phi,_=ex.explain(anchors)
        # Infinite thresholds until the mocked score turns on at shift onset.
        def score(vector,center,scale):
            score.counter+=1
            return {m:np.array([10. if score.counter>=7 else 0.]) for m in v.METHODS}
        score.counter=0
        with patch.object(v,'monitor_scores',score),patch.object(v,'fit_models',return_value=candidate),patch.object(v,'aipw_effect',side_effect=lambda d,m:d.true_effect.to_numpy()):
            records,runs,_=v.evaluate_stream(99,'response',200,baseline,np.zeros(17),np.ones(17),{m:1 for m in v.METHODS},ex,bg,anchors,phi)
        d=pd.DataFrame(records)
        first=d[(d.method=='M0') & (d.review_budget==2)]
        self.assertTrue(first.loc[first.period==7,'retrain_accepted'].iloc[0])
        self.assertGreater(first.loc[first.period==7,'regret'].iloc[0],0)
        self.assertEqual(first.loc[first.period==8,'regret'].iloc[0],0)
        self.assertTrue(all(r['reviews']<=r['review_budget'] and r['alerts']<=2 for r in runs))
    def test_fail_closed_validation(self):
        with tempfile.TemporaryDirectory() as t:
            folder=Path(t);shutil.copy(ROOT/'validate_data.py',folder)
            good=v.original_data().drop(columns='propensity')
            for kind in ('missing','infinity','wrong_truth','one_arm','fractional_age','empty'):
                bad=good.copy()
                if kind=='missing':bad=bad.drop(columns='age')
                if kind=='infinity':bad.loc[0,'purchase_amount']=np.inf
                if kind=='wrong_truth':bad.loc[0,'true_effect']=5
                if kind=='one_arm':bad.discount=0
                if kind=='fractional_age':bad['age']=bad.age.astype(float);bad.loc[0,'age']=25.5
                if kind=='empty':bad=bad.iloc[:0]
                bad.to_csv(folder/'customers.csv',index=False)
                r=subprocess.run([sys.executable,str(folder/'validate_data.py')],capture_output=True)
                self.assertNotEqual(r.returncode,0,kind)
    def test_pipeline_stops_on_validation_failure(self):
        with tempfile.TemporaryDirectory() as t:
            folder=Path(t);shutil.copy(ROOT/'run_pipeline.py',folder)
            (folder/'generate_data.py').write_text('pass\n')
            (folder/'validate_data.py').write_text('raise SystemExit(1)\n')
            (folder/'train_causal_model.py').write_text('from pathlib import Path\nPath("SHOULD_NOT_EXIST").touch()\n')
            r=subprocess.run([sys.executable,str(folder/'run_pipeline.py')],cwd=folder.parent,capture_output=True)
            self.assertNotEqual(r.returncode,0);self.assertFalse((folder/'SHOULD_NOT_EXIST').exists())
    def test_early_false_alert_does_not_hide_later_detection(self):
        with tempfile.TemporaryDirectory() as t:
            folder=Path(t);(folder/'paper1_experiments').mkdir()
            pd.DataFrame({'period':[1,2,3], 'group':['A']*3,'true_effect':[20,-10,-10],'estimated_effect':[-1,1,-5]}).to_csv(folder/'paper1_experiments/effects_over_time.csv',index=False)
            r=subprocess.run([sys.executable,str(ROOT/'paper1_experiments/evaluate_detection.py')],cwd=folder,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertIn('first_postharm_detection',r.stdout)
            # Parse the printed table, where first alert=1, first harm=2, detection=3, delay=1.
            vals=r.stdout.strip().splitlines()[-1].split()
            self.assertEqual(vals[1:5],['2','1','3','1'])
    def test_legacy_stable_detection_is_not_applicable(self):
        import contextlib, io
        for name in ('monitoring_validation_v1', 'monitoring_validation_v1_diagnostic', 'monitoring_validation_v2_followup'):
            spec=importlib.util.spec_from_file_location(name,ROOT/'paper1_experiments'/(name+'.py'))
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            self.assertIn('repaired',module.OUT.name)
            with tempfile.TemporaryDirectory() as t:
                module.OUT=Path(t);module.TEST_RUNS=1;module.CALIBRATION_RUNS=2
                def stream(seed,scenario):
                    return np.zeros((12,7)),np.tile([20.,15.],(12,1)),np.ones((12,2)),np.tile([20.,15.],(12,1))
                with patch.object(module,'stream',stream), contextlib.redirect_stdout(io.StringIO()):module.main()
                runs=pd.read_csv(module.OUT/'runs.csv')
                self.assertTrue(runs.loc[runs.scenario=='stable','change_detected'].isna().all(),name)
                if name!='monitoring_validation_v1':self.assertTrue((module.OUT/'period_log.csv').exists())

    def test_repaired_proxy_has_nonzero_group_contrast(self):
        # Execute definitions only, avoiding the historical script's top-level experiment.
        import ast
        tree=ast.parse((ROOT/'paper1_experiments/m2_explanation_stability_v1.py').read_text())
        defs=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[])
        namespace={'np':np,'pd':pd,'FEATURES':['age','spending','group_A']}
        exec(compile(defs,'proxy','exec'),namespace)
        anchors=pd.DataFrame({'age':[30,40],'spending':[100,100],'group_A':[0,1]})
        class Model:
            def __init__(self,arm):self.arm=arm
            def predict(self,x):return np.ones(len(x))*40+self.arm*np.where(x.group_A==1,20,15)
        values=namespace['explanation']((Model(1),Model(0)),anchors)
        self.assertEqual(values[2],5)

if __name__=='__main__':unittest.main()
