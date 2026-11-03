import cv2
import numpy as np

def resize_frame(frame, width=960):
    h,w=frame.shape[:2]
    return cv2.resize(frame,(int(width),round(h*width/w)))

def point_inside(bbox, polygon):
    """Floor region: test bottom-center of pet box in image coordinates."""
    x1,y1,x2,y2=bbox
    p=((x1+x2)/2,y2)
    return cv2.pointPolygonTest(np.asarray(polygon,dtype=np.int32),p,False)>=0

def overlap_fraction(bbox, polygon, shape):
    """Furniture region: 2D pet-box overlap, not physical occupancy proof."""
    h,w=shape[:2]
    x1,y1,x2,y2=map(int,bbox)
    x1=max(0,min(w,x1));x2=max(0,min(w,x2));y1=max(0,min(h,y1));y2=max(0,min(h,y2))
    if x2<=x1 or y2<=y1:return 0.0
    mask=np.zeros((h,w),dtype=np.uint8)
    cv2.fillPoly(mask,[np.asarray(polygon,np.int32)],1)
    return float(mask[y1:y2,x1:x2].mean())

def is_violation(bbox, polygon, shape, mode='floor', overlap_threshold=0.2):
    if mode=='floor':return point_inside(bbox,polygon)
    if mode=='overlap':return overlap_fraction(bbox,polygon,shape)>=overlap_threshold
    raise ValueError('mode must be floor or overlap')
