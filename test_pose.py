import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

model_path = r"C:\Users\Arnab 2001\Desktop\prime_projects\AI_gym_trainer\ml_models\pose_landmarker_full.task"

base_options = python.BaseOptions(
    model_asset_path=model_path
)

options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.IMAGE
)

detector = vision.PoseLandmarker.create_from_options(options)

print("WORKING ✅")