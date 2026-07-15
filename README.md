# Kinetic — AI Gym Coach

> Real-time computer vision rep counter and form coach. No wearables, no sensors — just your webcam, MediaPipe pose estimation, and joint-angle math.

---

## What it does

Kinetic watches you exercise through your webcam (via WebRTC), tracks 33 body landmarks in real time with MediaPipe's Pose Landmarker, and runs each frame through an exercise-specific detector that computes joint angles to count reps and flag bad form — sagging hips on a push-up, insufficient squat depth, swinging on a curl — as it happens, not after the set.

Five exercises are supported out of the box: **Squats, Push-ups, Biceps Curls, Shoulder Press, Lunges** — each with its own form-check logic, not a generic angle threshold copy-pasted five times.

---

## Architecture

```
Browser (webcam feed)
        │  streamlit-webrtc
        ▼
VideoProcessorClass.recv(frame)
        │
        ├─► MediaPipe PoseLandmarker.detect_for_video()  → 33 landmarks
        │
        ├─► Skeleton overlay drawn on frame (segment-colored)
        │
        ├─► Active ExerciseDetector.process(landmarks)
        │        │
        │        ├─ calculate_angle() — vector dot-product → joint angle
        │        ├─ visibility gating — ignores occluded joints
        │        └─ stage machine — "down"/"up" → rep counted on transition
        │
        ├─► AngleSmoother — exponential moving average (α=0.35) on angles
        │
        └─► Overlay metrics on frame → SQLite (session persistence)
```

---

## The rep-counting logic

Every exercise detector inherits from an abstract `BaseExercise` and implements a state machine over a single joint angle. Squats, for example:

```
knee_angle < 100°  →  stage = "down"
knee_angle ≥ 160° AND stage == "down"  →  stage = "up", reps += 1
```

The rep only counts on the **down → up transition**, not just crossing a threshold — so a partial squat that never gets low enough, or jittery noise around the threshold, doesn't inflate the count.

Each exercise tracks different joints and different failure modes:

| Exercise | Primary angle tracked | Form check |
|---|---|---|
| Squats | Knee angle (hip-knee-ankle) | Depth status: good depth vs. too high |
| Push-ups | Elbow angle | Body alignment (hip sag detection via shoulder/hip/ankle y-position) |
| Biceps Curls | Elbow angle | Swing status (shoulder stability during the curl) |
| Shoulder Press | Elbow extension | Extension completeness + back arch |
| Lunges | Front knee angle | Balance status |

**Left/right side is chosen dynamically per frame** — whichever side has higher MediaPipe visibility confidence is used for angle calculation, so the detector doesn't break when you turn slightly or one side is partially out of frame.

---

## Why an angle smoother

Raw joint angles from pose estimation are noisy frame-to-frame — a MediaPipe misdetection of even a few pixels swings a knee angle by several degrees, enough to falsely flip the down/up stage and miscount reps.

`AngleSmoother` applies an exponential moving average per angle key:

```python
smoothed = ALPHA * raw + (1 - ALPHA) * previous_smoothed   # ALPHA = 0.35
```

This is a deliberate tradeoff: low enough alpha to kill single-frame jitter, high enough to not introduce noticeable lag on a real repetition. Resets on exercise switch so a stale smoothed value from squats doesn't bleed into push-up angles.

---

## Why MediaPipe Pose Landmarker over building a custom pose model

Training a pose estimation model from scratch is a multi-month research problem on its own — MediaPipe's Pose Landmarker is a production-grade, pretrained solution (BlazePose-based) that runs fast enough for real-time video on CPU. The actual engineering value in this project is the **downstream logic**: turning 33 raw (x, y, visibility) points into a rep count and a form judgment, which is where the exercise-specific detector classes live.

## Why per-exercise detector classes instead of one generic threshold checker

A single "angle < X = rep" function can't express that push-ups need hip-sag detection while squats need depth checking. The abstract `BaseExercise` gives every detector shared math (`calculate_angle`, `get_point`) while `process()` is exercise-specific — new exercises are added by writing one focused class, not branching a monolith.

---

## Persistence & Auth

- **Lightweight username-only login** — no password, just `get_or_create_user()` against a local SQLite `users` table. Appropriate for a personal fitness tool, not a multi-tenant SaaS product.
- **Session logging** — reps/sets/time per exercise per day are upserted into an `exercises` table (`UPDATE ... WHERE user_id AND exercise_name AND Date('created_at') = Date('now')`), so multiple sets of the same exercise in one session accumulate instead of overwriting.
- **`@st.cache_resource`** on the DB connection — avoids re-opening a SQLite connection on every Streamlit rerun (Streamlit reruns the whole script on each interaction).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Live video | streamlit-webrtc (WebRTC in-browser) |
| Pose estimation | MediaPipe Pose Landmarker (Tasks API) |
| CV / frame processing | OpenCV, NumPy |
| Form logic | Custom joint-angle detectors (pure Python/math) |
| Persistence | SQLite |
| Planned coaching layer | Groq (LLM feedback), gTTS (voice) — scaffolded, not yet wired in |

---

## Project Structure

```
Ai_gym_trainer/
├── main.py                              # page bootstrap, layout, auth gate
├── core/
│   └── base_exercise.py                 # abstract detector — angle math, contract
├── detectors/
│   ├── squat.py
│   ├── pushup.py
│   ├── biceps_curl.py
│   ├── shoulder_press.py
│   ├── lunges.py
│   ├── plank.py
│   └── deadlift.py
├── services/
│   ├── cv_implementation/
│   │   ├── exercise_video_processor.py  # WebRTC video processor — the real-time loop
│   │   └── frame_processor.py           # AngleSmoother (EMA)
│   ├── config/
│   │   └── workout_config.py            # exercise list, skeleton segment/colour config
│   ├── auth/
│   │   └── login_wall.py                # username-only auth
│   ├── persistence/
│   │   └── exercise_repository.py       # SQLite schema + queries
│   ├── state/
│   │   └── session_default.py           # Streamlit session_state defaults
│   ├── ui/
│   │   └── style_loader.py              # custom font + CSS injection
│   └── coaching/                        # Groq LLM + TTS voice coaching (in progress)
├── components/                          # Streamlit UI components (header, planner, metrics, history)
├── ml_models/
│   └── pose_landmarker_full.task        # MediaPipe pretrained weights
├── visual_understanding/                # reference pose images per exercise
└── requirements.txt
```

---

## Setup

```bash
git clone https://github.com/Mearnab01/Ai_gym_trainer.git
cd Ai_gym_trainer
pip install -r requirements.txt
streamlit run main.py
```

Open `http://localhost:8501`, enter a username, pick an exercise, and start the webcam session.

---

## Honest Status

The `services/coaching/` module (Groq LLM feedback + gTTS voice coaching) is scaffolded but the implementation files are currently empty — it's the planned next layer on top of the working rep-counting core, not a finished feature. Worth knowing before demoing it live.

---

## Author

**Arnab Nath** — [GitHub](https://github.com/Mearnab01)

---

