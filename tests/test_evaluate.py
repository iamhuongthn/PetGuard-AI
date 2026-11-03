from src.evaluate import match_detections, detection_metrics, evaluate_zones
import pandas as pd

def test_match():
    gt = [{"class":"dog","bbox":[0,0,100,100]}]
    pred = [{"class":"dog","bbox":[0,0,100,100]},
            {"class":"dog","bbox":[150,150,200,200]}]
    assert match_detections(gt, pred) == {"TP":1,"FN":0,"FP":1}

def test_zone_metrics(tmp_path):
    f=tmp_path/"labels.csv"
    pd.DataFrame({
        "expected_zone_status":["SAFE","SAFE","VIOLATION","VIOLATION"],
        "predicted_zone_status":["SAFE","VIOLATION","VIOLATION","SAFE"]
    }).to_csv(f,index=False)
    m=evaluate_zones(f)
    assert (m["TP"],m["TN"],m["FP"],m["FN"])==(1,1,1,1)
    assert m["zone_accuracy"]==0.5
