"""Compare frame labels with saved spatial predictions and disclose provenance."""
import argparse, json, math
from pathlib import Path
import pandas as pd
from src.evaluate import evaluate_zones

def fmt(v): return f'{v:.2%}' if math.isfinite(v) else 'N/A'

def evaluate(path,out,run=None):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    df=pd.read_csv(path)
    required={'sample_id','expected_zone_status'}
    if not required.issubset(df): raise ValueError('Missing label columns')
    if df.sample_id.isna().any() or df.sample_id.duplicated().any(): raise ValueError('Sample IDs must be unique')
    if run:
        run=Path(run); pred=pd.read_csv(run/'frame_predictions.csv')
        if not df.video_id.eq(run.name).all() or df.frame_id.duplicated().any(): raise ValueError('Run or frame IDs do not match')
        mapped=df.frame_id.map(pred.set_index('frame').candidate_violation.map({True:'VIOLATION',False:'SAFE'}))
        if mapped.isna().any(): raise ValueError('Missing saved prediction')
        if 'predicted_zone_status' in df and not df.predicted_zone_status.eq(mapped).all(): raise ValueError('Submitted predictions differ from saved run')
        df['predicted_zone_status']=mapped
    provenance='Provisional labels; independent review not established.'
    if 'source' in df and df.source.eq('synthetic_injected_detections').all(): provenance='Synthetic geometry fixture; no real detector accuracy.'
    elif run and all(c in df for c in ['reviewer','review_date','label_basis','source_sha256']):
        if df[['reviewer','review_date','source_sha256']].fillna('').astype(str).apply(lambda x:x.str.strip().ne('')).all().all() and df.label_basis.eq('original_video_polygon_only').all():
            cfg=json.loads((run/'zone_config.json').read_text()); digest=cfg.get('source_sha256')
            if df.source_sha256.nunique()!=1 or (digest and not df.source_sha256.eq(digest).all()): raise ValueError('Source hash mismatch')
            provenance='Reviewer attested original footage review; '+('source hash matches run.' if digest else 'historical run has no source hash; identity not independently established.')
    merged=out/'evaluated_labels.csv';df.to_csv(merged,index=False)
    metrics=evaluate_zones(merged,out/'zone_evaluation.csv')
    a=df.expected_zone_status.str.strip().str.upper();p=df.predicted_zone_status.str.strip().str.upper()
    matrix=pd.crosstab(a,p).reindex(index=['SAFE','VIOLATION'],columns=['SAFE','VIOLATION'],fill_value=0);matrix.index.name='Actual';matrix.to_csv(out/'zone_confusion_matrix.csv')
    wrong=df[a!=p];wrong.to_csv(out/'zone_failure_cases.csv',index=False)
    (out/'zone_evaluation_summary.md').write_text(f'# Spatial decision evaluation\n\n{provenance}\n\nSamples: {len(df)}. SAFE: {metrics["TN"]+metrics["FP"]}. VIOLATION: {metrics["TP"]+metrics["FN"]}.\n\nAgreement: {fmt(metrics["zone_accuracy"])}. False violation rate: {fmt(metrics["false_violation_rate"])}. Violation recall: {fmt(metrics["violation_recall"])}.\n\nConfusion matrix: TN {metrics["TN"]}, FP {metrics["FP"]}, FN {metrics["FN"]}, TP {metrics["TP"]}.\n\nDisagreements: {len(wrong)}. See `zone_failure_cases.csv`. Sampled frames are correlated; this is not event accuracy.\n')
    print(json.dumps({k:(None if isinstance(v,float) and not math.isfinite(v) else v) for k,v in metrics.items()},indent=2));return metrics

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('labels_csv');a.add_argument('--out',default='results/metrics');a.add_argument('--run');args=a.parse_args();evaluate(args.labels_csv,args.out,args.run)
