"""Engineering checks for the development gate comparison."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
runner=load('refreshed_runner',ROOT/'paper1_experiments/refreshed_gate_development_v1.py')
base=load('sensitivity_for_gate_tests',ROOT/'paper1_experiments/model_onset_sensitivity_v1.py')

class Model:
    def __init__(self,arm,effect):self.arm,self.effect=arm,effect
    def predict(self,x):return 50+.4*x.previous_spending.to_numpy()+self.arm*np.where(x.age<35,self.effect,15.)
class Explainer:
    def live_summary(self,data):return np.zeros(4)

class RefreshedGateDevelopment(unittest.TestCase):
    def setUp(self):
        self.baseline=(Model(0,40),Model(1,40))
        self.candidate=(Model(0,5),Model(1,5))
    def evaluate(self,variant,callback=lambda *args:None):
        evaluator=runner.instrument(base,callback,variant)
        return evaluator(420300,'response',200,self.baseline,np.zeros(17),np.ones(17),
            {m:-1 for m in base.METHODS},Explainer(),None,None,None,onset=7)
    def test_only_gate_outcome_model_switches(self):
        for variant,expected in [('frozen',self.baseline),('refreshed',self.candidate)]:
            used=[]
            def pseudo(data,models):used.append(models);return np.zeros(len(data))
            with patch.object(base,'fit_models',return_value=self.candidate),patch.object(base,'aipw_effect',side_effect=pseudo):
                rows,_,_=self.evaluate(variant)
            self.assertTrue(used)
            self.assertTrue(all(m is expected for m in used))
            self.assertTrue(all(r['retrain_accepted']==(r['gate_lower']>0) for r in rows))
    def test_truth_cannot_change_gate_decisions(self):
        original=base.make_window
        def corrupted(*args,**kwargs):
            data=original(*args,**kwargs);data.true_effect=-9999.;return data
        with patch.object(base,'fit_models',return_value=self.candidate):
            a=pd.DataFrame(self.evaluate('refreshed')[0])
            with patch.object(base,'make_window',side_effect=corrupted):
                b=pd.DataFrame(self.evaluate('refreshed')[0])
        fields=['score','alert_issued','review_performed','retrain_accepted','gate_mean','gate_lower','treatment_rate']
        pd.testing.assert_frame_equal(a[fields],b[fields])
    def test_truth_only_callback_does_not_change_results(self):
        calls=[]
        with patch.object(base,'fit_models',return_value=self.candidate):
            a=pd.DataFrame(self.evaluate('refreshed')[0])
            b=pd.DataFrame(self.evaluate('refreshed',lambda *args:calls.append(len(args[3])))[0])
        self.assertTrue(calls);pd.testing.assert_frame_equal(a,b)
    def test_original_function_not_mutated_and_unknown_variant_rejected(self):
        original=base.evaluate_stream
        runner.instrument(base,lambda *args:None,'refreshed')
        self.assertIs(base.evaluate_stream,original)
        with self.assertRaises(ValueError):runner.instrument(base,lambda *args:None,'invalid')

if __name__=='__main__':unittest.main()
