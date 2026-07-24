"""
config.py — All tunable settings for the Smart Vision Assistant live in one place.
Tweak values here instead of hunting through the code.
"""

# ── Detection ────────────────────────────────────────────────────────────
MODEL_PATH = "yolov8n.pt"      # "n" = nano, fastest, good enough for real-time on CPU/webcam
CONFIDENCE_THRESHOLD = 0.5      # ignore detections below this confidence
PROCESS_EVERY_N_FRAMES = 2      # run detection every Nth frame (speed vs smoothness tradeoff)

# Set to None to detect ALL 80 COCO classes, or restrict to specific ones
# (useful for a "walking assistant" use case — only care about obstacles)
CLASSES_FILTER = None
# Example restricted set:
# CLASSES_FILTER = ["person", "chair", "car", "bicycle", "dog", "backpack",
#                    "couch", "bench", "door", "stairs"]

# ── Direction zones ──────────────────────────────────────────────────────
# The frame is split into 5 horizontal zones for spoken direction feedback
DIRECTION_ZONES = ["far left", "left", "center", "right", "far right"]

# ── Distance estimation ──────────────────────────────────────────────────
# "area_ratio"  -> no calibration needed, uses how much of the frame the box fills
# "pinhole"     -> more accurate real-world meters, but needs FOCAL_LENGTH_PX calibrated
#                  for your specific camera (see README.md "Calibration" section)
DISTANCE_METHOD = "area_ratio"

# Only used when DISTANCE_METHOD = "pinhole"
FOCAL_LENGTH_PX = 700
REAL_WORLD_HEIGHTS_M = {   # approximate average real-world heights, in meters
    "person": 1.7, "bicycle": 1.1, "car": 1.5, "motorcycle": 1.3,
    "bus": 3.2, "truck": 3.0, "chair": 0.9, "couch": 0.85, "bottle": 0.25,
    "cup": 0.12, "laptop": 0.25, "tv": 0.5, "dog": 0.5, "cat": 0.3,
    "backpack": 0.45, "book": 0.25, "cell phone": 0.15, "keyboard": 0.03,
    "mouse": 0.04, "bench": 0.9, "potted plant": 0.6,
}
DEFAULT_REAL_HEIGHT_M = 0.5   # fallback for classes not listed above

# Distance category thresholds for area_ratio method (box area / frame area)
AREA_RATIO_THRESHOLDS = {"very close": 0.25, "close": 0.10, "medium": 0.03}
# Distance category thresholds for pinhole method (meters)
METER_THRESHOLDS = {"very close": 1.0, "close": 2.5, "medium": 5.0}

# ── Audio feedback ───────────────────────────────────────────────────────
SPEECH_RATE = 175                  # words per minute
DANGER_COOLDOWN_SEC = 2.0          # min seconds between repeat "very close" warnings per class
SUMMARY_INTERVAL_SEC = 3.0         # how often to announce the general "closest object" summary

# ── Display ──────────────────────────────────────────────────────────────
WINDOW_NAME = "Smart Vision Assistant"
DISTANCE_COLORS = {                # BGR colors for bounding boxes by distance category
    "very close": (0, 0, 255),     # red
    "close": (0, 165, 255),        # orange
    "medium": (0, 255, 255),       # yellow
    "far": (0, 255, 0),            # green
}
