import time
import streamlit as st
from services.config.workout_config import METRICS_FIELDS
from services.persistence.exercise_repository import add_exercise


# ─── Core Sync Function ─────────────────────────────────────────────────────────
def sync_metrics_update(context):
    latest_metrics = _get_latest_metrics(context)
    if not latest_metrics:
        return
    
    exercise = st.session_state.get("exercise_type")
    if not exercise:
        return
    
    _sync_metrics_to_session(exercise, latest_metrics)
    
    progress = _update_workout_progress()
    
    _handle_set_completion(exercise, latest_metrics, progress)
    _handle_workout_completion(exercise, latest_metrics, progress)
    _handle_pose_feedback(exercise, latest_metrics)
    _handle_ongoing_feedback(exercise, latest_metrics)
    

# ─── Metrics Fetching ─────────────────────────────────────────────────────
def _get_latest_metrics(context):
    if (
        not context
        or not hasattr(context, "state")
        or not context.state.playing
    ):
        return None
    
    processor = getattr(context, "video_processor", None)
    
    if not processor:
        return None
    
    exercise = st.session_state.get("exercise_type")
    
    if not exercise:
        return None 
    
    processor.set_exercise(exercise)
    return processor.get_latest_metrics()


# ─── Session State Sync ──────────────────────────────────────────────────────
def _sync_metrics_to_session(exercise, latest_metrics):
    reps = latest_metrics.get("reps", 0)
    if reps is None:
        reps = 0
        
    st.session_state.reps = reps
    fields = METRICS_FIELDS.get(exercise)
    
    if not fields:
        return
    
    for key, default in fields.items():
        st.session_state[key] = latest_metrics.get(
            key, default
        )


# ─── Workout Progress Logic ──────────────────────────────────────────────────
def _update_workout_progress():
    reps = st.session_state.get("reps", 0)

    reps_per_set = st.session_state.get(
        "reps_per_set",
        0
    )
    target_sets = st.session_state.get(
        "target_sets", 0 
    )

    if reps_per_set > 0 and target_sets > 0:
        sets_completed = reps // reps_per_set
        current_set_reps = reps % reps_per_set
        
        workout_completed = (
            sets_completed >= target_sets
        )
        
    else:
        sets_completed = 0
        current_set_reps = 0
        workout_completed = False
        
    st.session_state.sets_completed = sets_completed

    st.session_state.current_set_reps = (
        current_set_reps
    )

    st.session_state.workout_completed = (
        workout_completed
    )

    return {
        "sets_completed": sets_completed,
        "current_set_reps": current_set_reps,
        "workout_completed": workout_completed,
    }
    
    
# ─── Set Completion ──────────────────────────────────────────────────────────
def _handle_set_completion(exercise, latest_metrics, progress):
    sets_completed = progress["sets_completed"]
    last_saved_sets = st.session_state.get(
        "last_saved_sets_completed", 0
    )
    if sets_completed <= last_saved_sets:
        return
    
    reps_per_set = st.session_state.get(
        "reps_per_set", 0
    )
    if reps_per_set <= 0:
        return
    
    newly_completed = (
        sets_completed - last_saved_sets
    )
    
    now_ts = time.time()
    started_at = st.session_state.get(
        "set_cycle_started_at", now_ts
    )
    
    time_taken = now_ts - started_at
    user_id = st.session_state.get("user_id")
    
    print("NOW:", now_ts)
    print("START:", started_at)
    print("TIME TAKEN:", time_taken)
    
    add_exercise(
        user_id,
        exercise,
        newly_completed * reps_per_set,
        newly_completed,
        time_taken
    )
    # trigger voice event for set completion
    
    st.session_state.set_cycle_started_at = now_ts

    st.session_state.last_saved_sets_completed = (
        sets_completed
    )


# ─── Workout Completion ──────────────────────────────────────────────────────
def _handle_workout_completion(exercise, latest_metrics, progress):
    if not progress["workout_completed"]:
        return

    already_notified = st.session_state.get(
        "last_notified_workout_complete",
        False
    )

    if already_notified:
        return

    st.session_state.last_notified_workout_complete = True
    
    # trigger voice event for workout completion


# ─── Pose Detection Feedback ─────────────────────────────────────────────────
def _handle_pose_feedback(exercise, latest_metrics):
    pose_detected = latest_metrics.get(
        "pose_detected",
        True
    )
    
    if pose_detected:
        return

    # trigger voice event for pose correction


# ── Realtime Form Coaching ────────────────────────────────────────────────────
def _handle_ongoing_feedback( exercise, latest_metrics ):
    pass

# ─── Voice Pipeline Helper ────────────────────────────────────────────────────
def _trigger_voice_event(event, exercise, metrics):
    pass


