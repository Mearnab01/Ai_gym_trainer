import streamlit as st
def render_workout_empty_state():
    st.markdown("""
        <div style="text-align: center; padding: 50px 30px; margin: 30px 0; border: 2px solid #3a3a3a; border-radius: 16px; background-color: #1e1e1e;">
            <h3 style="margin: 0 0 10px 0; font-weight: 600; color: #e0e0e0;">No active workout</h3>
            <p style="font-size: 15px; color: #b0b0b0; line-height: 1.5;">
                Select your exercise type, sets, and reps from the sidebar<br>
                then click <span style="background: #00FFAA; color: #1e1e1e; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600;"> Start Workout Session</span>
            </p>
            <div style="margin-top: 25px; font-size: 13px; color: #888; display: flex; justify-content: center; gap: 20px;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 4L14.5 9.5L20.5 10L16 14L17.5 20L12 17L6.5 20L8 14L3.5 10L9.5 9.5L12 4Z" fill="#FF9800" stroke="#FF9800" stroke-width="1"/>
                    </svg>
                    <span>Push-ups</span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2V7M12 2L9 5M12 2L15 5" stroke="#FF9800" stroke-width="1.5"/>
                        <path d="M5 12H19M5 12L8 15M5 12L8 9" stroke="#FF9800" stroke-width="1.5"/>
                        <rect x="3" y="15" width="18" height="5" rx="1" fill="#2e2e2e" stroke="#FF9800" stroke-width="1"/>
                    </svg>
                    <span>Squats</span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="4" y="10" width="16" height="8" rx="1" fill="#2e2e2e" stroke="#FF9800" stroke-width="1"/>
                        <circle cx="9" cy="14" r="1.5" fill="#FF9800"/>
                        <circle cx="15" cy="14" r="1.5" fill="#FF9800"/>
                        <line x1="6" y1="6" x2="8" y2="10" stroke="#FF9800" stroke-width="1"/>
                        <line x1="18" y1="6" x2="16" y2="10" stroke="#FF9800" stroke-width="1"/>
                    </svg>
                    <span>Lunges</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)