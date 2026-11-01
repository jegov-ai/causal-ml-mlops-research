"""Signal isolation and preservation checks; run with unittest discovery."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'paper1_experiments' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

v = load('ablation', 'monitoring_signal_ablation_v1.py')
old = load('historical', 'integrated_causal_monitoring_v2_xai.py')

class Model:
    def __init__(self, arm, shifted=False):
        self.arm, self.shifted = arm, shifted
    def predict(self, frame):
        effect = np.where(frame.age < 35, 5. if self.shifted else 40., 15.)
        return 50 + .4 * frame.previous_spending.to_numpy() + self.arm * effect

class SignalAblation(unittest.TestCase):
    def test_each_extra_signal_is_isolated(self):
        for index, responding in (
            (9, set(v.METHODS)),
            (10, {'M2-A', 'M2-FULL'}),
            (11, {'M2-A', 'M2-FULL'}),
            (12, {'M2-B', 'M2-FULL'}),
            (13, set()), (14, set()), (15, set()), (16, set()),
        ):
            x = np.zeros((2, 17)); x[:, index] = [-20, 30]
            scores = v.monitor_scores(x, np.zeros(17), np.ones(17))
            for name in v.METHODS:
                np.testing.assert_array_equal(scores[name], [20, 30] if name in responding else [0, 0])

    def test_existing_m1_and_full_m2_scores_preserved(self):
        rng = np.random.default_rng(19)
        x, c = rng.normal(size=(12, 17)), rng.normal(size=17)
        scale = rng.uniform(.2, 3, 17)
        new, historical = v.monitor_scores(x, c, scale), old.monitor_scores(x, c, scale)
        np.testing.assert_array_equal(new['M1'], historical['M1'])
        np.testing.assert_array_equal(new['M2-FULL'], historical['M2'])

    def test_controller_gate_and_timing_preserved(self):
        baseline = (Model(0), Model(1))
        candidate = (Model(0, True), Model(1, True))
        bg = v.make_window(70000, 1, 'stable', 20)[v.FEATURES]
        anchors = v.make_window(70001, 1, 'stable', 20)[v.FEATURES]
        output = []
        for module in (old, v):
            ex = module.TwoFeatureShapley(baseline, bg)
            phi, _ = ex.explain(anchors)
            counter = [0]
            def scores(vector, center, scale):
                counter[0] += 1
                return {m: np.array([10. if counter[0] >= 7 else 0.]) for m in module.METHODS}
            with patch.object(module, 'monitor_scores', scores), patch.object(module, 'fit_models', return_value=candidate), patch.object(module, 'aipw_effect', side_effect=lambda d,m: d.true_effect.to_numpy()):
                records, summaries, _ = module.evaluate_stream(300009, 'response', 200, baseline, np.zeros(17), np.ones(17), {m: 1 for m in module.METHODS}, ex, bg, anchors, phi)
            output.append(pd.DataFrame(records))
            for run in summaries:
                self.assertLessEqual(run['reviews'], run['review_budget'])
                self.assertLessEqual(run['alerts'], 2)
            part = output[-1].query("method == 'M1' and review_budget == 2")
            self.assertTrue(part.loc[part.period == 7, 'retrain_accepted'].iloc[0])
            self.assertGreater(part.loc[part.period == 7, 'regret'].iloc[0], 0)
            self.assertEqual(part.loc[part.period == 8, 'regret'].iloc[0], 0)
        for original, new in [('M1', 'M1'), ('M2', 'M2-FULL')]:
            a = output[0].loc[output[0].method == original].drop(columns='method').reset_index(drop=True)
            b = output[1].loc[output[1].method == new].drop(columns='method').reset_index(drop=True)
            pd.testing.assert_frame_equal(a, b)

if __name__ == '__main__':
    unittest.main()
