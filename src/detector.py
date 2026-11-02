from ultralytics import YOLO

class PetDetector:
    def __init__(self, weights='yolov8s.pt', confidence=0.35, imgsz=960):
        self.model = YOLO(weights)
        self.confidence = float(confidence)
        self.imgsz = int(imgsz)

    def detect(self, image):
        result = self.model.predict(image, imgsz=self.imgsz,
                                    conf=self.confidence, classes=[15,16],
                                    verbose=False)[0]
        detections = []
        for b in result.boxes:
            cid=int(b.cls[0]);name=result.names[cid]
            detections.append({'class':name,'confidence':float(b.conf[0]),
                               'bbox':tuple(map(int,b.xyxy[0].cpu().tolist()))})
        return detections
