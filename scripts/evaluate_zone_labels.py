"""Evaluate human-verified held-out SAFE/VIOLATION labels. Never fabricate labels."""
import argparse,json
from pathlib import Path
import pandas as pd
from src.evaluate import evaluate_zones

def evaluate(path,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    df=pd.read_csv(path)
    required={'sample_id','expected_zone_status','predicted_zone_status'}
    if not required.issubset(df.columns):raise ValueError('Missing required columns: '+str(required-set(df.columns)))
    if df.sample_id.isna().any() or df.sample_id.duplicated().any():raise ValueError('Every sample_id must be unique and nonblank')
    metrics=evaluate_zones(path,out/'zone_evaluation.csv')
    labels=['SAFE','VIOLATION']
    matrix=pd.crosstab(df.expected_zone_status.str.strip().str.upper(),df.predicted_zone_status.str.strip().str.upper()).reindex(index=labels,columns=labels,fill_value=0)
    matrix.index.name='Actual';matrix.columns.name='Predicted';matrix.to_csv(out/'zone_confusion_matrix.csv')
    wrong=df[df.expected_zone_status.str.strip().str.upper()!=df.predicted_zone_status.str.strip().str.upper()]
    wrong.to_csv(out/'zone_failure_cases.csv',index=False)
    (out/'zone_evaluation_summary.md').write_text('# PetGuard Zone Evaluation (human-labeled)\n\n'+f"Samples: {metrics['samples']}\n\nAccuracy: {metrics['zone_accuracy']:.2%}\n\nFalse violation rate: {metrics['false_violation_rate']:.2%}\n\nViolation recall: {metrics['violation_recall']:.2%}\n\nConfusion matrix (rows actual, columns predicted):\n\n"+matrix.to_markdown()+f'\n\nFailure cases: {len(wrong)}. See zone_failure_cases.csv.\n')
    print(json.dumps(metrics,indent=2));return metrics

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('labels_csv');a.add_argument('--out',default='results/metrics');args=a.parse_args();evaluate(args.labels_csv,args.out)
