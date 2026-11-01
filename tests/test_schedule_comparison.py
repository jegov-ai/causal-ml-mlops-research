"""Check calendar and shared-gate timing without running fresh evaluation streams."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('schedule',ROOT/'paper1_experiments/monitoring_schedule_comparison_v1.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

class Model:
    def __init__(self,arm,shifted=False):self.arm,self.shifted=arm,shifted
    def predict(self,x):
        effect=np.where(x.age<35,5. if self.shifted else 40.,15.)
        return 50+.4*x.previous_spending.to_numpy()+self.arm*effect

class ScheduleComparison(unittest.TestCase):
    def test_fixed_calendar_is_the_prespecified_draft(self):
        self.assertEqual(v.CALENDARS,{2:(4,8),4:(3,6,9,12),8:(1,3,4,6,7,9,10,12)})
        for cap,dates in v.CALENDARS.items():
            self.assertEqual(len(dates),cap)
            self.assertEqual(tuple(sorted(set(dates))),dates)
        x=np.random.default_rng(7).normal(size=(12,17))
        scores=v.monitor_scores(x,np.zeros(17),np.ones(17))
        old=v.base.monitor_scores(x,np.zeros(17),np.ones(17))
        for method in v.base.METHODS:
            np.testing.assert_array_equal(scores[method],old[method])
        np.testing.assert_array_equal(scores['PERIODIC'],np.zeros(12))

    def test_calendar_ignores_alerts_and_updates_next_window(self):
        baseline=(Model(0),Model(1));candidate=(Model(0,True),Model(1,True))
        bg=v.make_window(360009,1,'stable',20)[v.FEATURES]
        ex=v.base.TwoFeatureShapley(baseline,bg);phi,_=ex.explain(bg)
        with patch.object(v,'fit_models',return_value=candidate),patch.object(v,'aipw_effect',side_effect=lambda d,m:d.true_effect.to_numpy()):
            records,runs,_=v.evaluate_stream(360009,'response',200,baseline,np.zeros(17),np.ones(17),{m:np.inf for m in v.METHODS},ex,bg,bg,phi)
        frame=pd.DataFrame(records)
        for cap,dates in v.CALENDARS.items():
            part=frame.query("method=='PERIODIC' and review_budget==@cap")
            self.assertEqual(tuple(part.loc[part.review_performed,'period']),dates)
            self.assertFalse(part.alert_issued.any())
        part=frame.query("method=='PERIODIC' and review_budget==2")
        self.assertTrue(part.loc[part.period==8,'retrain_accepted'].iloc[0])
        self.assertGreater(part.loc[part.period==8,'regret'].iloc[0],0)
        self.assertEqual(part.loc[part.period==9,'regret'].iloc[0],0)
        for run in runs:
            self.assertLessEqual(run['reviews'],run['review_budget'])
            if run['method']=='PERIODIC':
                self.assertTrue(np.isnan(run['change_detected']))
                self.assertTrue(np.isnan(run['detection_delay']))
            else:self.assertEqual(run['reviews'],0)

if __name__=='__main__':unittest.main()
