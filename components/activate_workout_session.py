import streamlit as st


def _render_active_workout_session():
    exercise = st.session_state.get("exercise_type")
    sets = st.session_state.get("target_sets")
    reps = st.session_state.get("reps_per_set")
    
    st.info(f"**{exercise}** -- {sets} Sets / {reps} Reps")
    
    end_session_button = st.button("End Workout Session", width=300, key="end_session_button", icon=":material/stop_circle:")
    
    if end_session_button:
        st.session_state['workout_started'] = False
        st.rerun()
    
     
    
def render_active_workout_session():
    st.header("Active Workout Session")
    _render_active_workout_session()
    