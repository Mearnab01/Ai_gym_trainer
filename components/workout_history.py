import streamlit as st
from logger.logger import setup_logger

log = setup_logger()

def _render_workout_history():
    st.subheader("Workout History")
    st.write("Here you can view your past workout sessions and performance metrics.")
    
    
def render_workout_history():
    try:
        _render_workout_history()
    except Exception as e:
        log.error(f"Error rendering workout history: {e}")
        st.error("Failed to load workout history.")