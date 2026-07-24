# Smart Vision Assistant

Live object detection with spoken **direction** and **distance** feedback —
point your webcam at the world and it tells you what's around you and where.

Built as an assistive-navigation style project (could genuinely help a
visually impaired user, or serve as a robotics obstacle-awareness module).

## How it works

```
Webcam → YOLOv8 (detection) → direction/distance calc → speech scheduler → pyttsx3 (audio)
                                        ↓
                                 on-screen overlay (OpenCV)
```

1. **detector.py** — runs YOLOv8n on each frame, returns bounding boxes + class names.
2. **spatial_utils.py** — turns each box into a direction ("left"/"center"/"right"/etc.)
   and a distance category ("very close"/"close"/"medium"/"far").
3. **audio_feedback.py** — a background thread speaks text without freezing the video.
4. **main.py** — ties it together: draws the overlay, and decides *when* to speak
   (immediate priority warnings for close obstacles, periodic summaries otherwise).

## Setup

```bash
pip install -r requirements.txt
```

On Linux, `pyttsx3` needs the `espeak` engine installed:
```bash
sudo apt install espeak
```

Run it:
```bash
python main.py
```

Controls (video window must be focused):
- `q` — quit
- `m` — mute / unmute audio

The first run will auto-download the YOLOv8n weights (~6MB).

## Features

- **Real-time detection** across all 80 COCO object classes (or restrict to a
  custom list in `config.py`, e.g. just obstacles for a walking assistant).
- **Direction awareness** — 5-zone horizontal mapping (far left → far right).
- **Distance estimation** — two selectable methods in `config.py`:
  - `area_ratio` (default): no setup needed, uses how much of the frame the object fills.
  - `pinhole`: gives approximate real-world meters, needs a one-time camera calibration.
- **Smart audio scheduling**, not a firehose of noise:
  - "Very close" objects trigger immediate, priority spoken warnings (interrupts other speech).
  - Everything else gets a calm periodic summary of the single closest object (every ~3s).
  - Per-class cooldowns stop the same warning from repeating every frame.
- **Color-coded live overlay** (red = very close → green = far) plus an FPS counter.
- Fully offline — no internet/API calls needed after the initial model download.

## Calibrating the "pinhole" distance method (optional, for real meters)

1. Place a known object (e.g. yourself, ~1.7m tall) at a known distance, say 2 meters, from the camera.
2. Run the app, note the bounding box pixel height for that object.
3. Compute: `FOCAL_LENGTH_PX = (pixel_height * distance_m) / real_height_m`
4. Put that value into `config.py`.

## Ideas to extend this further

- **Stereo audio panning** — pan the beep/voice left/right in the stereo field to
  match the object's direction, instead of just saying "left"/"right".
- **Object tracking** (e.g. simple centroid tracker or DeepSORT) so the same
  physical object isn't re-announced as if it were new every summary cycle.
- **Depth model** (e.g. MiDaS) instead of the height heuristic, for much more
  accurate distance without calibration.
- **Voice commands** ("what's in front of me?", "mute") using `speech_recognition`.
- **Mobile port** — TensorFlow Lite + Android/iOS for a pocketable version.
- **Danger-zone haptics** — pair with a phone/wearable for vibration alerts
  in noisy environments where audio isn't reliable.
- **Session logging** — save a timeline of detections for later review/analytics.

## Project structure

```
smart-vision-assistant/
├── main.py              # entry point — capture loop, overlay, scheduling
├── detector.py           # YOLOv8 wrapper
├── spatial_utils.py       # direction + distance math
├── audio_feedback.py       # threaded text-to-speech
├── config.py               # all tunable settings
├── requirements.txt
└── README.md
```
