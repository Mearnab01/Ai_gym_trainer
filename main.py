import os
import time
import pandas as pd
import streamlit as st
import logging


from components.workout_planner import render_workout_planner
from components.activate_workout_session import render_active_workout_session
from components.workout_metrices import render_workout_metrics

from services.auth.login_wall import render_login_wall
from services.ui.style_loader import inject_local_font, load_css
from services.state.session_default import initial_session_defaults
# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ],
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)

# ─── CONSTANTS ────────────────────────────────────────────────────────
 
STATIC_DIR  = os.path.join(os.getcwd(), "static")
CSS_FILE    = os.path.join(STATIC_DIR, "style.css")
FONT_FILE   = os.path.join(STATIC_DIR, "AdobeClean.otf")
FONT_NAME   = "AdobeClean"
 
# RTC_CONFIG  = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}

def _bootstrap_page() -> None:
    """Page config + assets. Must run before any other st call."""
    st.set_page_config(
        page_title="Kinetic — AI Gym Coach",
        page_icon="⚡",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    try:
        inject_local_font(FONT_FILE, FONT_NAME)
        load_css(CSS_FILE)
        log.info("Page loaded with custom styles and fonts.")
    except Exception as e:
        log.error(f"Error loading styles/fonts: {e}")


def main():
    _bootstrap_page()
    
    if not render_login_wall():
        return
    initial_session_defaults()
    
    workout_started = st.session_state.get("workout_started", False)
    
    with st.sidebar:
        
        if st.session_state['username']:
            st.markdown(f"Logged in as: **{st.session_state['username']}**")
    
        st.divider()
        
        if not workout_started:
            render_workout_planner()
        else:
            render_active_workout_session()
            
        if workout_started:
            st.divider()
            render_workout_metrics()
    
    
    
    
if __name__ == "__main__":
    main()