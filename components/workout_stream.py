import streamlit as st
from logger.logger import setup_logger

log = setup_logger()

def _render_workout_stream():
    st.subheader("Live Workout Stream")
    
    
    
def render_workout_stream():
    try:
        _render_workout_stream()
    except Exception as e:
        log.error(f"Error in workout stream: {e}")
        st.error("Unable to load workout stream.")