"""Engineering checks; no unseen main evaluation streams are generated."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('spacing',ROOT/'paper1_experiments/monitoring_review_spacing_v1.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

class Model:
    def __init__(self,arm,shifted=False):self.arm,self.shifted=arm,shifted
    def predict(self,x):
        effect=np.where(x.age<35,5. if self.shifted else 40.,15.)
        return 50+.4*x.previous_spending.to_numpy()+self.arm*effect

def simulate(module,active):
    baseline=(Model(0),Model(1));candidate=(Model(0,True),Model(1,True))
    bg=module.make_window(360099,1,'stable',20)[module.FEATURES]
    ex=v.base.TwoFeatureShapley(baseline,bg);phi,_=ex.explain(bg);counter=[0]
    def scores(vector,center,scale):
        counter[0]+=1
        return {m:np.array([10. if active(counter[0]) else 0.]) for m in module.METHODS}
    with patch.object(module,'monitor_scores',scores),patch.object(module,'fit_models',return_value=candidate),patch.object(module,'aipw_effect',side_effect=lambda d,m:d.true_effect.to_numpy()):
        rows,runs,_=module.evaluate_stream(360099,'response',200,baseline,np.zeros(17),np.ones(17),{m:1. for m in module.METHODS},ex,bg,bg,phi)
    return pd.DataFrame(rows),runs

class ReviewSpacing(unittest.TestCase):
    def test_spacing_preserves_later_review_and_next_window_timing(self):
        frame,runs=simulate(v,lambda period:period>=5)
        consecutive=frame.query("method=='M1-CONSEC' and review_budget==2")
        spaced=frame.query("method=='M1-SPACED' and review_budget==2")
        self.assertEqual(consecutive.loc[consecutive.review_performed,'period'].tolist(),[5,6])
        self.assertEqual(spaced.loc[spaced.review_performed,'period'].tolist(),[5,7])
        self.assertTrue(spaced.loc[spaced.period==7,'retrain_accepted'].iloc[0])
        self.assertGreater(spaced.loc[spaced.period==7,'regret'].iloc[0],0)
        self.assertEqual(spaced.loc[spaced.period==8,'regret'].iloc[0],0)
        for run in runs:
            self.assertLessEqual(run['reviews'],run['review_budget'])
            self.assertLessEqual(run['alerts'],2)
        for _,part in frame.loc[frame.method.str.endswith('SPACED')].groupby(['method','review_budget']):
            dates=part.loc[part.review_performed,'period'].to_numpy()
            self.assertTrue((np.diff(dates)>=2).all())

    def test_low_current_score_preserves_unused_capacity(self):
        frame,_=simulate(v,lambda period:period==5)
        for method in ['M1-SPACED','FULL-SPACED']:
            for cap in [2,4,8]:
                part=frame.query('method==@method and review_budget==@cap')
                self.assertEqual(part.loc[part.review_performed,'period'].tolist(),[5])

    def test_consecutive_controller_reproduces_frozen_baseline(self):
        original,_=simulate(v.base,lambda period:period>=5)
        current,_=simulate(v,lambda period:period>=5)
        for old,new in [('M1','M1-CONSEC'),('M2-FULL','FULL-CONSEC')]:
            a=original.loc[original.method==old].drop(columns='method').reset_index(drop=True)
            b=current.loc[current.method==new].drop(columns='method').reset_index(drop=True)
            pd.testing.assert_frame_equal(a,b)

    def test_frozen_score_mapping_is_identical_between_controllers(self):
        x=np.random.default_rng(23).normal(size=(12,17))
        old=v.base.monitor_scores(x,np.zeros(17),np.ones(17))
        current=v.monitor_scores(x,np.zeros(17),np.ones(17))
        for method in v.METHODS:
            np.testing.assert_array_equal(current[method],old[v.SCORE_METHOD[method]])

if __name__=='__main__':unittest.main()
