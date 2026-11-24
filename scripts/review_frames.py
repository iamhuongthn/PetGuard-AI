"""Create a blind review pack from original footage, never annotated output."""
import argparse, json
from pathlib import Path
import cv2
import pandas as pd
import numpy as np
from src.zone import resize_frame
from src.provenance import sha256_file

def prepare(run, video, out, labels=None):
    run, video, out = map(Path, (run, video, out))
    cfg=json.loads((run/'zone_config.json').read_text())
    if video.name != cfg['video_name']:
        raise ValueError('Original filename must match the run configuration')
    digest=sha256_file(video)
    if cfg.get('source_sha256') and digest != cfg['source_sha256']:
        raise ValueError('Original video hash differs from run')
    pred=pd.read_csv(run/'frame_predictions.csv')
    ids=pd.read_csv(labels).frame_id.tolist() if labels else pred.frame.iloc[np.linspace(0,len(pred)-1,min(50,len(pred)),dtype=int)].tolist()
    if len(set(ids))!=len(ids) or not set(ids)<=set(pred.frame): raise ValueError('Invalid frame IDs')
    out.mkdir(parents=True,exist_ok=True)
    cap=cv2.VideoCapture(str(video)); rows=[]
    try:
        for i in ids:
            cap.set(cv2.CAP_PROP_POS_FRAMES,int(i)); ok, frame=cap.read()
            if not ok: raise ValueError(f'Cannot decode frame {i}')
            frame=resize_frame(frame,cfg['size'][0])
            if list(frame.shape[1::-1])!=cfg['size']: raise ValueError('Frame dimensions differ')
            cv2.polylines(frame,[np.array(cfg['polygon'],np.int32)],True,(0,0,255),2)
            name=f'frame_{i:05d}.jpg'
            if not cv2.imwrite(str(out/name),frame): raise IOError(name)
            rows.append(dict(sample_id=f'{run.name}_{i:05d}',source='real_video',video_id=run.name,frame_id=i,scenario=cfg['zone_mode'],pet_count_ground_truth='',expected_zone_status='',zone_mode=cfg['zone_mode'],notes='',reviewer='',review_date='',label_basis='original_video_polygon_only',source_sha256=digest))
    finally: cap.release()
    pd.DataFrame(rows).to_csv(out/'blind_labels.csv',index=False)
    (out/'review_manifest.json').write_text(json.dumps({'run_id':run.name,'source_sha256':digest,'source_name':video.name,'polygon':cfg['polygon'],'hash_matches_original_run':bool(cfg.get('source_sha256'))},indent=2))
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run');p.add_argument('video');p.add_argument('--out',required=True);p.add_argument('--labels');a=p.parse_args();print(prepare(a.run,a.video,a.out,a.labels))
