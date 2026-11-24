"""Match independently annotated sustained scene entries to alert onset frames."""
import argparse, json
from pathlib import Path
import pandas as pd

def evaluate(labels, events, tolerance=5):
    gt=pd.read_csv(labels); pred=pd.read_csv(events)
    if tolerance<0: raise ValueError('Tolerance must be nonnegative')
    required=['start_frame','end_frame','reviewer','review_date']
    if not set(required)<=set(gt): raise ValueError('Missing event label columns')
    if gt[required].isna().any().any(): raise ValueError('Incomplete event labels')
    intervals=sorted((int(a),int(b)) for a,b in zip(gt.start_frame,gt.end_frame))
    if any(a<0 or b-a<4 for a,b in intervals) or any(b>=c for (_,b),(c,_) in zip(intervals,intervals[1:])): raise ValueError('Intervals must be disjoint and last at least five frames')
    frames=sorted(int(f) for f in pred.frame); used=set(); matches=[]
    for a,b in intervals:
        eligible=[(abs(f-(a+4)),i,f) for i,f in enumerate(frames) if i not in used and a<=f<=min(b,a+4+tolerance)]
        if eligible:
            _,i,f=min(eligible);used.add(i);matches.append({'start_frame':a,'end_frame':b,'alert_frame':f,'delay_frames':f-a})
    tp=len(matches);fp=len(frames)-tp;fn=len(intervals)-tp
    return dict(TP=tp,FP=fp,FN=fn,recall=tp/len(intervals) if intervals else None,precision=tp/len(frames) if frames else None,tolerance_frames=tolerance,matches=matches)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('labels');p.add_argument('events');p.add_argument('--out',required=True);p.add_argument('--tolerance',type=int,default=5);a=p.parse_args();r=evaluate(a.labels,a.events,a.tolerance);out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
