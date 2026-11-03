from pathlib import Path
import json
import time
import cv2
import numpy as np
import pandas as pd
from .detector import PetDetector
from .zone import resize_frame,is_violation
from .temporal import TemporalConfirm
from .event_logger import write_events

def process_video(input_path, output_path, event_csv, polygon,
                  weights='yolov8s.pt', target_width=960,
                  confidence=0.35, imgsz=960, mode='floor',
                  overlap_threshold=0.2, confirm_frames=5):
    cap=cv2.VideoCapture(str(input_path))
    if not cap.isOpened():raise ValueError(f'Cannot open video: {input_path}')
    fps=float(cap.get(cv2.CAP_PROP_FPS))
    if fps<=0:fps=25.0
    detector=PetDetector(weights, confidence, imgsz)
    state=TemporalConfirm(confirm_frames)
    output_path=Path(output_path);output_path.parent.mkdir(parents=True,exist_ok=True)
    writer=None; frame_idx=0;events=[];predictions=[];timings=[]
    wall_start=time.perf_counter()
    zone=np.asarray(polygon,dtype=np.int32)
    try:
        while True:
            ok,original=cap.read()
            if not ok:break
            frame=resize_frame(original,target_width)
            h,w=frame.shape[:2]
            if writer is None:
                writer=cv2.VideoWriter(str(output_path),cv2.VideoWriter_fourcc(*'mp4v'),fps,(w,h))
                if not writer.isOpened():raise RuntimeError('VideoWriter failed to open')
            start=time.perf_counter()
            detections=detector.detect(frame)
            checked=[]
            for d in detections:
                flagged=is_violation(d['bbox'],polygon,frame.shape,mode,overlap_threshold)
                checked.append({**d,'in_zone':bool(flagged)})
            candidates=[d for d in checked if d['in_zone']]
            active,new_event=state.update(bool(candidates))
            if new_event:
                pick=max(candidates,key=lambda x:x['confidence'])
                events.append({'source':Path(input_path).name,'frame':frame_idx,
                               'video_seconds':round(frame_idx/fps,3),'pet_class':pick['class'],
                               'confidence':round(pick['confidence'],4),'event':'VIOLATION'})
            timings.append((time.perf_counter()-start)*1000)
            # Persist box-level predictions for object matching and false-positive analysis.
            predictions.append({
                'frame': frame_idx,
                'seconds': round(frame_idx/fps, 3),
                'pet_count': len(checked),
                'detections': json.dumps(checked),
                'candidate_violation': bool(candidates),
                'confirmed_violation': bool(active),
                'new_event': bool(new_event),
                'processing_ms': round(timings[-1], 3),
            })
            cv2.polylines(frame,[zone],True,(0,0,255),2)
            cv2.putText(frame,'RESTRICTED ZONE',(int(zone[:,0].min()), max(22,int(zone[:,1].min())-8)),
                        cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
            for d in checked:
                x1,y1,x2,y2=d['bbox']
                color=(0,0,255) if d['in_zone'] else (0,200,0)
                cv2.rectangle(frame,(x1,y1),(x2,y2),color,2)
                cv2.putText(frame,f"{d['class']} {d['confidence']:.2f}",(x1,max(20,y1-7)),
                            cv2.FONT_HERSHEY_SIMPLEX,0.65,color,2)
            status='CONFIRMED VIOLATION' if active else ('PENDING' if candidates else 'SAFE / NO PET')
            cv2.putText(frame,status,(15,34),cv2.FONT_HERSHEY_SIMPLEX,0.85,
                        (0,0,255) if active else (0,220,0),2)
            writer.write(frame)
            frame_idx+=1
    finally:
        cap.release()
        if writer is not None:writer.release()
    write_events(events,event_csv)
    pred_path=Path(event_csv).with_name('frame_predictions.csv')
    pd.DataFrame(predictions).to_csv(pred_path,index=False)
    elapsed = time.perf_counter() - wall_start
    mean_ms = float(np.mean(timings)) if timings else None
    # Mean/P95 exclude decoding and encoding; throughput includes the full run.
    return {
        'frames': frame_idx, 'events': len(events),
        'avg_ms': round(mean_ms, 2) if mean_ms is not None else None,
        'p95_ms': round(float(np.percentile(timings, 95)), 2) if timings else None,
        'processing_fps': round(1000 / mean_ms, 2) if mean_ms and mean_ms > 0 else None,
        'wall_seconds': round(elapsed, 2),
        'end_to_end_fps': round(frame_idx / elapsed, 2) if elapsed > 0 else None,
        'output': str(output_path), 'csv': str(event_csv),
        'predictions_csv': str(pred_path),
    }
