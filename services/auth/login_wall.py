import streamlit as st
from services.persistence.exercise_repository import get_or_create_user

def render_login_wall():
    if st.session_state.get("user_id") is not None:
        return True
    
    
    st.markdown("""
        <div style="text-align: center; padding: 30px 10px 10px 10px;">
            <div style="font-size: 64px; margin-bottom: 5px;">⚡</div>
            <h1 style="color: #e0e0e0; margin: 0 0 16px 0; font-size: 48px; font-weight: 600;">Welcome to Kinetic!</h1>
            <p style="color: #b0b0b0; font-size: 18px; max-width: 500px; margin: 0 auto 40px auto; line-height: 1.5;">
                Please enter your <strong style="color: #4CAF50;">username</strong> to start training.<br>
            </p>
        </div>
    """, unsafe_allow_html=True)

    # ── Form ───────────────────────────────────────────────
    
    left, center, right = st.columns([1, 4, 1])
    with center:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Username",
                placeholder="e.g. arnab_1028",
                label_visibility="visible",
            )    
            submitted = st.form_submit_button("Start Training", width="stretch")
        

    # ── Validation & auth ──────────────────────────────────
    if submitted:
        username = username.strip()
        
        if not username:
            st.error("Enter your username first!!")
            return False
        
        if len(username) < 2:
            st.error("Username must be at least 3 characters.")
            return False
        
        user = get_or_create_user(username)
        if not user:
            st.error("Failed to create or retrieve user.")
            return False

        # create user
        st.session_state["user_id"] = user["id"]
        st.session_state["username"] = user["username"]

        st.rerun()
        
    return False
            