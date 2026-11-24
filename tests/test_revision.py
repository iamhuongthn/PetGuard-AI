import csv, json
import cv2
import numpy as np
import pandas as pd
import pytest
from src.main import process_video
from scripts.evaluate_events import evaluate
from scripts.evaluate_zone_labels import evaluate as zones
from scripts.review_frames import prepare

def test_video_pipeline(tmp_path):
    video=tmp_path/'input.mp4'; writer=cv2.VideoWriter(str(video),cv2.VideoWriter_fourcc(*'mp4v'),25,(320,240))
    assert writer.isOpened()
    for _ in range(12): writer.write(np.zeros((240,320,3),np.uint8))
    writer.release()
    class Mock:
        def __init__(self,*args): self.i=0
        def detect(self,frame):
            i=self.i;self.i+=1
            return [{'class':'dog' if i<3 else 'cat','confidence':.9,'bbox':(20,20,60,60)}] if i<5 else []
    run=tmp_path/'run';run.mkdir()
    result=process_video(video,run/'annotated.mp4',run/'events.csv',[(0,0),(100,0),(100,100),(0,100)],target_width=320,detector_factory=Mock)
    assert result['frames']==12 and result['events']==1
    p=pd.read_csv(run/'frame_predictions.csv'); assert p.alert_state.iloc[4]=='ACTIVE' and p.spatial_status.iloc[5]=='SAFE' and p.alert_state.iloc[5]=='ACTIVE' and p.alert_state.iloc[9]=='INACTIVE'
    assert pd.read_csv(run/'events.csv').frame.tolist()==[4]
    (run/'zone_config.json').write_text(json.dumps({'video_name':video.name,'size':[320,240],'polygon':[[0,0],[100,0],[100,100],[0,100]],'zone_mode':'floor'}))
    pack=prepare(run,video,tmp_path/'review'); labels=pd.read_csv(pack/'blind_labels.csv');assert 'predicted_zone_status' not in labels and labels.expected_zone_status.isna().all()
    labels['expected_zone_status']=['VIOLATION']*5+['SAFE']*7; labels.to_csv(pack/'blind_labels.csv',index=False)
    assert zones(pack/'blind_labels.csv',tmp_path/'metrics',run)['zone_accuracy']==1
    labels['predicted_zone_status']='SAFE';labels.to_csv(pack/'blind_labels.csv',index=False)
    with pytest.raises(ValueError): zones(pack/'blind_labels.csv',tmp_path/'metrics',run)

def test_event_matching(tmp_path):
    a=tmp_path/'a.csv'; b=tmp_path/'b.csv'
    pd.DataFrame({'start_frame':[10,40],'end_frame':[25,55],'reviewer':['test']*2,'review_date':['test']*2}).to_csv(a,index=False)
    pd.DataFrame({'frame':[14,30]}).to_csv(b,index=False)
    r=evaluate(a,b);assert (r['TP'],r['FP'],r['FN'])==(1,1,1)
