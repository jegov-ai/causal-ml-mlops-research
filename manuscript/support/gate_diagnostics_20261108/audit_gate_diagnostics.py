from pathlib import Path
import pandas as pd,numpy as np,json,hashlib
root=Path('gate_replay_audit');d=pd.read_csv(root/'review_diagnostics.csv');p=pd.read_csv(root/'reproduced_period_log.csv');o=pd.read_csv('sensitivity_audit/run_20261106_102857_143041/period_log.csv')
keys=['initial_seed','seed','scenario','onset','period','method','review_budget']
pd.testing.assert_frame_equal(p.set_index(keys).sort_index()[o.set_index(keys).columns],o.set_index(keys).sort_index(),check_dtype=False,check_exact=False,atol=1e-12,rtol=1e-12)
assert not d.duplicated(keys).any()
r=p[p.review_performed].copy()
j=d.merge(r,on=keys,validate='one_to_one',suffixes=('_d','_p'))
assert len(j)==len(r)==len(d)==5310
assert (j.accepted==j.retrain_accepted).all()
assert np.allclose(j.gate_mean_d,j.gate_mean_p,atol=1e-12,rtol=1e-12)
assert np.allclose(j.gate_lower_d,j.gate_lower_p,atol=1e-12,rtol=1e-12)
assert (d.accepted==(d.gate_lower>0)).all()
assert d.next_window_benefit.isna().equals(d.period.eq(12))
assert (d.next_window_available==d.period.lt(12)).all()
for col in ['gate_mean','gate_lower','true_gate_benefit']:
 assert np.isfinite(d[col]).all()
def label(s):return np.where(s>1e-10,'helpful',np.where(s< -1e-10,'harmful','tied'))
d['gate_class']=label(d.true_gate_benefit)
d['next_class']=np.where(d.next_window_available,label(d.next_window_benefit),'unavailable')
counts=d.groupby(['method','accepted','next_class']).size().unstack(fill_value=0)
print('NEXT WINDOW\n',counts.to_string())
print('GATE SAMPLE\n',d.groupby(['method','accepted','gate_class']).size().unstack(fill_value=0).to_string())
print('M1 by scenario\n',d[d.method=='M1'].groupby(['scenario','accepted','next_class']).size().unstack(fill_value=0).to_string())
print('gate helpful next harmful',len(d[(d.gate_class=='helpful')&(d.next_class=='harmful')]))
print('gate harmful next helpful',len(d[(d.gate_class=='harmful')&(d.next_class=='helpful')]))
for m in ['M1','PERIODIC']:
 print(m,'examples',d[(d.method==m)&d.accepted&(d.next_class=='harmful')].head(2).to_dict('records'))
counts.to_csv(root/'next_window_classification_counts.csv')
d.groupby(['method','accepted','gate_class']).size().unstack(fill_value=0).to_csv(root/'gate_sample_classification_counts.csv')
d[d.method=='M1'].groupby(['scenario','accepted','next_class']).size().unstack(fill_value=0).to_csv(root/'m1_scenario_counts.csv')
checks=dict(period_rows=len(p),diagnostic_rows=len(d),all_original_period_fields_reconcile=True,one_diagnostic_per_review=True,unique_keys=True,acceptance_and_gate_reconcile=True,final_window_missingness_correct=True,all_gate_values_finite=True,classification_tolerance=1e-10,runtime_minutes=1335.9908675001934/60,limitation='No raw per-customer diagnostic predictions saved; true benefit is not independently reconstructed from actions.')
(root/'audit_checks.json').write_text(json.dumps(checks,indent=2))
