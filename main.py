import os
import time
import pandas as pd
import streamlit as st
from logger.logger import setup_logger

from components.app_header import render_app_header
from components.coach_feedback import render_coach_feedback
from components.coach_feedback import render_coach_feedback
from components.workout_empty_state import render_workout_empty_state
from components.workout_history import render_workout_history
from components.workout_stream import render_workout_stream
from components.workout_stream import render_workout_stream
from components.app_header import render_app_header


from components.workout_planner import render_workout_planner
from components.activate_workout_session import render_active_workout_session
from components.workout_metrices import render_workout_metrics

from services.auth.login_wall import render_login_wall
from services.ui.style_loader import inject_local_font, load_css
from services.state.session_default import initial_session_defaults
from services.persistence.exercise_repository import init_db


# ── Logging ───────────────────────────────────────────────────────────────────
log = setup_logger()

# ─── CONSTANTS ────────────────────────────────────────────────────────
 
STATIC_DIR  = os.path.join(os.getcwd(), "static")
CSS_FILE    = os.path.join(STATIC_DIR, "style.css")
FONT_FILE   = os.path.join(STATIC_DIR, "AdobeClean.otf")
FONT_NAME   = "AdobeClean"

# ── Bootstrap ────────────────────────────────────────────
def _bootstrap_page() -> None:
    """Page config + assets. Must run before any other st call."""
    st.set_page_config(
        page_title="Kinetic — AI Gym Coach",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_local_font(FONT_FILE, FONT_NAME)
    load_css(CSS_FILE)


# ── Left Sidebar ──────────────────────────────────────────────
def render_left_sidebar(workout_started: bool) -> None:
    with st.sidebar:
        if not workout_started:
            render_workout_planner()
        else:
            render_active_workout_session()
        
        st.divider()
        if st.session_state['username']:
            st.markdown(f"Logged in as: **{st.session_state['username']}**")

            if st.button(
                "Logout",
                type="secondary",
                icon=":material/logout:",
                width="stretch"
            ):
                st.session_state.clear()
                st.rerun()

            
            
# ── Main Content + Right Sidebar ──────────────────────────────
def render_main_content(workout_started: bool) -> None:
    
    
    main_content, right_space = st.columns([6, 2.3], gap="medium")

    with main_content:
        render_app_header()
        render_coach_feedback()
        if not workout_started:
            render_workout_empty_state()
        else:
            render_workout_stream()
         
        st.divider()
        render_workout_history()
        
    with right_space:
        if workout_started:
           render_workout_metrics()
                
# ── Main App Flow ─────────────────────────────────────────
def main():
    try:
        init_db()
        _bootstrap_page()
    except Exception as e:
        log.error(f"Error during bootstrap: {e}")
        st.error("An error occurred !!")
        return
    
    # ── Auth
    if not render_login_wall():
        return
    # ── Session init
    initial_session_defaults()
    
    
    workout_started = st.session_state.get('workout_started', False)
    
    # 1. Workout Planner or Active Session
    render_left_sidebar(workout_started)
    
    # 2. Main content area
    render_main_content(workout_started)
    
    
if __name__ == "__main__":
    main()