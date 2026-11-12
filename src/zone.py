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


def validate_polygon(points, frame_size=None, min_area=100):
    """Reject degenerate, self-crossing and out-of-frame simple polygons."""
    pts = np.asarray(points, dtype=np.float64)
    if pts.ndim != 2 or pts.shape[1] != 2 or len(pts) < 3 or not np.isfinite(pts).all():
        raise ValueError("Draw at least three finite polygon corners.")
    if len(set(map(tuple, pts))) != len(pts):
        raise ValueError("Polygon contains repeated corners.")
    if frame_size is not None:
        w, h = frame_size
        if np.any(pts[:, 0] < 0) or np.any(pts[:, 0] >= w) or np.any(pts[:, 1] < 0) or np.any(pts[:, 1] >= h):
            raise ValueError("Polygon corners must be inside the video frame.")
    def orient(a,b,c):
        return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def onseg(a,b,c):
        return min(a[0],b[0]) <= c[0] <= max(a[0],b[0]) and min(a[1],b[1]) <= c[1] <= max(a[1],b[1])
    def intersects(a,b,c,d):
        o1,o2,o3,o4=orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)
        if (o1>0 and o2<0 or o1<0 and o2>0) and (o3>0 and o4<0 or o3<0 and o4>0): return True
        return any(abs(o)<1e-9 and onseg(x,y,z) for o,x,y,z in ((o1,a,b,c),(o2,a,b,d),(o3,c,d,a),(o4,c,d,b)))
    n=len(pts)
    for i in range(n):
        for j in range(i+1,n):
            if j==i+1 or (i==0 and j==n-1): continue
            if intersects(pts[i],pts[(i+1)%n],pts[j],pts[(j+1)%n]):
                raise ValueError("Polygon edges cross. Redraw a simple, non-crossing zone.")
    area=abs(float(cv2.contourArea(pts.astype(np.float32))))
    if area < min_area: raise ValueError("Restricted area is too small.")
    return True
