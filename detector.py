"""
detector.py — Thin wrapper around a YOLOv8 model so the rest of the app
doesn't need to know anything about the underlying ML library.
"""

from ultralytics import YOLO
import config


class ObjectDetector:
    def __init__(self, model_path=None, conf_threshold=None, classes_filter=None):
        self.model = YOLO(model_path or config.MODEL_PATH)
        self.conf_threshold = conf_threshold or config.CONFIDENCE_THRESHOLD
        self.classes_filter = classes_filter if classes_filter is not None else config.CLASSES_FILTER

    def detect(self, frame):
        """
        Runs detection on a single BGR frame (numpy array).
        Returns a list of dicts: {class_name, confidence, bbox=(x1,y1,x2,y2)}
        """
        results = self.model(frame, verbose=False, conf=self.conf_threshold)[0]

        detections = []
        for box in results.boxes:
            class_id = int(box.cls[0])
            class_name = self.model.names[class_id]

            if self.classes_filter and class_name not in self.classes_filter:
                continue

            confidence = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            detections.append({
                "class_name": class_name,
                "confidence": confidence,
                "bbox": (x1, y1, x2, y2),
            })
        return detections
