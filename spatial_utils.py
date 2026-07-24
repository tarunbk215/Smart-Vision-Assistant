"""
spatial_utils.py — Turns a raw bounding box into human-meaningful spatial info:
  - which direction (left/center/right zone) the object is in
  - how far away it roughly is (category, and optionally meters)
"""

import config


def get_direction(bbox, frame_width):
    """Map a bounding box's horizontal center to one of 5 direction zones."""
    x1, _, x2, _ = bbox
    center_x = (x1 + x2) / 2
    ratio = center_x / frame_width

    zones = config.DIRECTION_ZONES  # ["far left","left","center","right","far right"]
    zone_index = min(int(ratio * len(zones)), len(zones) - 1)
    return zones[zone_index]


def _category_from_area_ratio(ratio):
    t = config.AREA_RATIO_THRESHOLDS
    if ratio >= t["very close"]:
        return "very close"
    if ratio >= t["close"]:
        return "close"
    if ratio >= t["medium"]:
        return "medium"
    return "far"


def _category_from_meters(distance_m):
    t = config.METER_THRESHOLDS
    if distance_m < t["very close"]:
        return "very close"
    if distance_m < t["close"]:
        return "close"
    if distance_m < t["medium"]:
        return "medium"
    return "far"


def estimate_distance(bbox, class_name, frame_width, frame_height):
    """
    Returns (distance_m_or_None, category_str).

    area_ratio method: no calibration needed, works out of the box.
    pinhole method: gives an approximate real-world distance in meters,
                    but needs FOCAL_LENGTH_PX calibrated for your camera.
    """
    x1, y1, x2, y2 = bbox
    box_w, box_h = max(x2 - x1, 1), max(y2 - y1, 1)

    if config.DISTANCE_METHOD == "pinhole":
        real_height = config.REAL_WORLD_HEIGHTS_M.get(class_name, config.DEFAULT_REAL_HEIGHT_M)
        distance_m = (real_height * config.FOCAL_LENGTH_PX) / box_h
        return distance_m, _category_from_meters(distance_m)

    # default: area_ratio
    frame_area = frame_width * frame_height
    box_area = box_w * box_h
    ratio = box_area / frame_area
    return None, _category_from_area_ratio(ratio)
