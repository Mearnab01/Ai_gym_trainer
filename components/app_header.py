import streamlit as st


def _render_app_header() -> None:
    st.markdown("""
        <style>
        .header-gradient {
            background: linear-gradient(130deg, #1e3c72 0%, #00FFAA 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        </style>
        
        <div class='header-gradient'>
            <div style='display: flex; align-items: center; justify-content: center; gap: 2px;'>
                <span style='font-size: 2.5rem; color: #FFD700;'>⚡</span>
                <h1 style='color: white; margin: 0;'>KINETIC AI GYM Coach</h1>
            </div>
            <h4 style='color: #e0e0e0; text-align: center; font-weight: normal; margin: 0.5rem 0 0 0;'>
                Real-time pose detection with proactive AI voice coaching
            </h4>
        </div>
    """, unsafe_allow_html=True)
    
    # Add a subtle info box
    with st.expander("How it works", expanded=False):
        st.markdown("""
        - 🎯 **Pose Detection**: Real-time body tracking using computer vision
        - 🔊 **Voice Coaching**: AI-powered feedback on your form
        - 💪 **Proactive Alerts**: Automatic corrections and tips
        """)
        
        
def render_app_header() -> None:
    return _render_app_header()