import streamlit as st

def render_login_wall():
    if st.session_state.get("user_id") is not None:
        return True
    
    
    st.title("Welcome to Kinetic! ⚡")
    st.markdown("""
    Please enter your **username** to start training. Your workout data will be saved under this username, so choose wisely! 😉 
    """)

    # ── Form ───────────────────────────────────────────────
    
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
        
        # TODO: 1 
        # create user
        st.session_state["username"] = username
        st.session_state["user_id"] = "1"
        
        st.rerun()
        
    return False
            