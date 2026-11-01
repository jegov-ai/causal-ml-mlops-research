"""Check unseen study allocation and fail-closed provenance; no study data generated."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'paper1_experiments/monitoring_signal_ablation_v1.py'
PROTOCOL = SCRIPT.with_name('SIGNAL_ABLATION_MAIN_PROTOCOL_v1.md')
spec = importlib.util.spec_from_file_location('main_ablation', SCRIPT)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

class MainSettings(unittest.TestCase):
    def test_study_allocation_is_disjoint_from_development(self):
        cfg, starts = v.run_settings('study')
        self.assertEqual(cfg, dict(n=1000, scale_runs=100, calibration_runs=1000, null_runs=200, test_runs=100))
        self.assertEqual(starts, dict(scale=310000, calibration=320000, null=330000, evaluation=340000))
        purposes = dict(scale='scale_runs', calibration='calibration_runs', null='null_runs', evaluation='test_runs')
        main = [set(range(starts[k], starts[k]+cfg[count])) for k,count in purposes.items()]
        self.assertEqual(sum(map(len, main)), len(set.union(*main)))
        for mode in ('smoke', 'pilot'):
            c,s = v.run_settings(mode)
            development = set().union(*(set(range(s[k],s[k]+c[count])) for k,count in purposes.items()))
            self.assertFalse(development & set.union(*main))
        with self.assertRaises(ValueError):
            v.run_settings('unknown')

    def test_main_requires_committed_source_and_intact_protocol(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); folder = root/'paper1_experiments'; folder.mkdir()
            script = folder/SCRIPT.name; protocol = folder/PROTOCOL.name
            shutil.copyfile(SCRIPT,script); shutil.copyfile(PROTOCOL,protocol)
            def git(*args):
                return subprocess.check_output(['git',*args],cwd=root,stderr=subprocess.STDOUT,text=True)
            git('init'); git('add','.')
            git('-c','user.name=Test','-c','user.email=test@example.invalid','-c','commit.gpgsign=false','commit','-m','test snapshot')
            with patch.object(v,'__file__',str(script)):
                data = v.study_provenance()
                self.assertEqual(data['git_commit'],git('rev-parse','HEAD').strip())
                script.write_bytes(script.read_bytes()+b'\n# uncommitted change\n')
                with self.assertRaisesRegex(RuntimeError,'Tracked Git changes'):
                    v.study_provenance()
                protocol.write_bytes(protocol.read_bytes()+b'\nchanged\n')
                with self.assertRaisesRegex(RuntimeError,'protocol missing or modified'):
                    v.study_provenance()

if __name__ == '__main__':
    unittest.main()
