from pathlib import Path
import pandas as pd,numpy as np,json,hashlib
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--run',required=True,type=Path);parser.add_argument('--reference',required=True,type=Path);args=parser.parse_args()
r=args.run;p=pd.read_csv(r/'period_log.csv');d=pd.read_csv(r/'review_diagnostics.csv');saved=pd.read_csv(r/'paired_development_differences.csv');o=pd.read_csv(args.reference/'period_log.csv')
k=['initial_seed','scenario','onset','seed','method','review_budget'];pk=k+['period']
assert len(p)==33696 and len(d)==10620 and len(saved)==1404
assert not p.duplicated(pk+['gate_variant']).any()
a=p[p.gate_variant=='frozen'].drop(columns='gate_variant');pd.testing.assert_frame_equal(a.set_index(pk).sort_index()[o.set_index(pk).columns],o.set_index(pk).sort_index(),check_dtype=False,check_exact=False,atol=1e-12,rtol=1e-12)
b=p[p.gate_variant=='refreshed'];cols=['score','threshold','alert_issued','review_performed'];pd.testing.assert_frame_equal(a.set_index(pk).sort_index()[cols],b.set_index(pk).sort_index()[cols],check_dtype=False,check_exact=False,atol=1e-12,rtol=1e-12)
assert (p.retrain_accepted==(p.gate_lower>0)).all()
j=d.merge(p[p.review_performed],on=pk+['gate_variant'],suffixes=('_d','_p'),validate='one_to_one')
assert len(j)==len(d)
assert (j.accepted==j.retrain_accepted).all()
for c in ['gate_mean','gate_lower']:np.testing.assert_allclose(j[c+'_d'],j[c+'_p'],rtol=1e-12,atol=1e-12)
assert d.next_window_benefit.isna().equals(d.period.eq(12))
assert (d.next_window_available==d.period.lt(12)).all()
post=p[p.period>=p.onset];tot=post.groupby(k+['gate_variant']).agg(cumulative_loss=('regret','sum'),mean_window_loss=('regret','mean'),postchange_accepted_updates=('retrain_accepted','sum')).reset_index()
pd.testing.assert_frame_equal(tot.set_index(k+['gate_variant']).sort_index(),pd.read_csv(r/'run_outcomes.csv').set_index(k+['gate_variant']).sort_index(),check_dtype=False,check_exact=False,rtol=1e-12,atol=1e-12)
f=tot[tot.gate_variant=='frozen'].drop(columns='gate_variant');u=tot[tot.gate_variant=='refreshed'].drop(columns='gate_variant');paired=u.merge(f,on=k,suffixes=('_refreshed','_frozen'),validate='one_to_one')
for c in ['cumulative_loss','mean_window_loss','postchange_accepted_updates']:paired[c+'_difference']=paired[c+'_refreshed']-paired[c+'_frozen']
pd.testing.assert_frame_equal(paired.set_index(k).sort_index()[saved.set_index(k).columns],saved.set_index(k).sort_index(),check_dtype=False,check_exact=False,atol=1e-12,rtol=1e-12)
def cls(s):return np.where(s< -1e-10,'lower',np.where(s>1e-10,'higher','tied'))
paired['direction']=cls(paired.mean_window_loss_difference)
print('SEED RECORDS',paired.groupby(['method','direction']).size().unstack(fill_value=0).to_string())
cell=paired.groupby(['initial_seed','scenario','onset','method','review_budget']).agg(mean_difference=('mean_window_loss_difference','mean'),cumulative_difference=('cumulative_loss_difference','mean')).reset_index();cell['direction']=cls(cell.mean_difference)
print('CELLS',cell.groupby(['method','direction']).size().unstack(fill_value=0).to_string())
print('M1\n',cell[cell.method=='M1'].groupby(['scenario','onset']).agg(mean_window_difference=('mean_difference','mean'),min_cell=('mean_difference','min'),max_cell=('mean_difference','max')).to_string())
d['next_class']=np.where(d.next_window_available,np.where(d.next_window_benefit>1e-10,'helpful',np.where(d.next_window_benefit< -1e-10,'harmful','tied')),'unavailable')
print('ACCEPTED\n',d[d.accepted].groupby(['gate_variant','method','next_class']).size().unstack(fill_value=0).to_string())
print('M1 REJECTED\n',d[(d.method=='M1')&~d.accepted].groupby(['gate_variant','next_class']).size().unstack(fill_value=0).to_string())
print('M1 worst\n',paired[paired.method=='M1'].sort_values('mean_window_loss_difference',ascending=False).head(3).to_string(index=False))
# Every method-budget horizon and policy regret nonnegative; no duplicate stable onset views.
assert np.isfinite(p.regret).all() and (p.regret>=-1e-12).all()
assert p.groupby(k+['gate_variant']).size().eq(12).all()
assert set(p[p.scenario=='stable'].onset)=={7}
counts=d[d.accepted].groupby(['gate_variant','method','next_class']).size().unstack(fill_value=0)
cell.to_csv(r/'cell_mean_differences.csv',index=False);counts.to_csv(r/'accepted_update_diagnostics.csv')
paired.to_csv(r/'recomputed_paired_differences.csv',index=False)
checks={'period_rows':len(p),'diagnostic_rows':len(d),'paired_rows':len(paired),'complete_12_window_histories':True,'frozen_periods_reconcile':True,'monitoring_and_reviews_matched':True,'all_paired_differences_recomputed':True,'all_diagnostics_match_reviews_and_gates':True,'last_window_missingness_correct':True,'finite_nonnegative_regret':True,'classification_tolerance':1e-10,'runtime_minutes':2647.996981400065/60,'limitations':'Three exposed stream seeds; repeated dependent cells. No individual diagnostic action reconstruction.'}
(r/'independent_audit_checks.json').write_text(json.dumps(checks,indent=2))
