import streamlit as st
from logger.logger import setup_logger
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from services.ui.style_loader import inject_webrtc_styles

log = setup_logger()
RTC_CONFIG  = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}

def _render_workout_stream():
    inject_webrtc_styles()
    context = webrtc_streamer(
        key = "exercise-analysis",
        mode = WebRtcMode.SENDRECV,
        video_processor_factory = None,
        rtc_configuration = RTC_CONFIG,
        media_stream_constraints = {
            "video": True, 
            "audio": False
        },
        async_processing = True
    )
    
    
    
def render_workout_stream():
    try:
        _render_workout_stream()
    except Exception as e:
        log.error(f"Error in workout stream: {e}")
        st.error("Unable to load workout stream.")