"""
main.py — Smart Vision Assistant

Live object detection with spoken direction + distance feedback.
Run:  python main.py
Controls (while the video window is focused):
    q  -> quit
    m  -> mute / unmute audio
    
"""

import time
import cv2

import config
from detector import ObjectDetector
from audio_feedback import SpeechEngine
from spatial_utils import get_direction, estimate_distance


class AnnouncementManager:
    """
    Decides WHEN to speak, so the app doesn't narrate every single frame.
    - Danger ("very close") objects get near-immediate priority alerts,
      throttled per class so they don't repeat every frame.
    - Otherwise, every SUMMARY_INTERVAL_SEC we announce the single closest
      object currently in view.
    """

    def __init__(self, speech: SpeechEngine):
        self.speech = speech
        self.last_danger_time = {}   # class_name -> timestamp
        self.last_summary_time = 0.0

    def process(self, detections):
        now = time.time()

        # 1) Danger alerts (highest priority, can interrupt anything)
        for det in detections:
            if det["distance_category"] == "very close":
                cls = det["class_name"]
                last = self.last_danger_time.get(cls, 0)
                if now - last >= config.DANGER_COOLDOWN_SEC:
                    self.speech.speak(
                        f"Warning. {cls} very close, {det['direction']}.",
                        priority=True,
                    )
                    self.last_danger_time[cls] = now

        # 2) Periodic summary of the closest non-danger object
        if now - self.last_summary_time >= config.SUMMARY_INTERVAL_SEC:
            candidates = [d for d in detections if d["distance_category"] != "very close"]
            if candidates:
                closest = min(candidates, key=lambda d: _distance_sort_key(d))
                self.speech.speak(
                    f"{closest['class_name']} {closest['distance_category']}, {closest['direction']}."
                )
            self.last_summary_time = now


def _distance_sort_key(det):
    # Smaller value = closer. Prefer real meters if available, else rank by category.
    if det["distance_m"] is not None:
        return det["distance_m"]
    order = {"very close": 0, "close": 1, "medium": 2, "far": 3}
    return order.get(det["distance_category"], 4)


def draw_overlay(frame, detections, muted):
    h, w = frame.shape[:2]

    # direction zone guide lines
    for i in range(1, len(config.DIRECTION_ZONES)):
        x = int(w * i / len(config.DIRECTION_ZONES))
        cv2.line(frame, (x, 0), (x, h), (60, 60, 60), 1)

    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        color = config.DISTANCE_COLORS.get(det["distance_category"], (255, 255, 255))
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        dist_txt = f"{det['distance_m']:.1f}m" if det["distance_m"] is not None else det["distance_category"]
        label = f"{det['class_name']} | {det['direction']} | {dist_txt}"
        cv2.putText(frame, label, (x1, max(y1 - 8, 15)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    status = "MUTED" if muted else "AUDIO ON"
    cv2.putText(frame, f"{status}  (q: quit, m: mute)", (10, h - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)


def main():
    detector = ObjectDetector()
    speech = SpeechEngine()
    announcer = AnnouncementManager(speech)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam. Check camera index / permissions.")

    frame_count = 0
    last_detections = []
    prev_time = time.time()

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            h, w = frame.shape[:2]
            frame_count += 1

            if frame_count % config.PROCESS_EVERY_N_FRAMES == 0:
                raw_detections = detector.detect(frame)
                enriched = []
                for det in raw_detections:
                    direction = get_direction(det["bbox"], w)
                    distance_m, category = estimate_distance(det["bbox"], det["class_name"], w, h)
                    det["direction"] = direction
                    det["distance_m"] = distance_m
                    det["distance_category"] = category
                    enriched.append(det)
                last_detections = enriched
                announcer.process(last_detections)

            draw_overlay(frame, last_detections, speech.muted)

            # FPS counter
            now = time.time()
            fps = 1.0 / max(now - prev_time, 1e-6)
            prev_time = now
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            cv2.imshow(config.WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("m"):
                speech.toggle_mute()

    finally:
        cap.release()
        cv2.destroyAllWindows()
        speech.shutdown()


if __name__ == "__main__":
    main()
