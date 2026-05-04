import streamlit as st
from services.config.workout_config import EXERCISE_OPTIONS

def _render_workout_planner():
    plan_exercise = st.selectbox("Select Exercise", options=EXERCISE_OPTIONS, key="plan_exercise")
    plan_sets = st.number_input("Sets", min_value=1, max_value=50, key="plan_sets", step=1)
    plan_reps = st.number_input("Reps", min_value=1, max_value=100, key="plan_reps", step=1)
    st.divider()
    
    
    start_session_button = st.button("Start Workout Session", width=300, key="start_workout", icon=":material/fitness_center:")
    
    
    if start_session_button:
        st.session_state['workout_started'] = True
        st.session_state['exercise_type'] = plan_exercise
        st.session_state['target_sets'] = int(plan_sets)
        st.session_state['reps_per_set'] = int(plan_reps)
        
        st.session_state['reps'] = 0
        st.rerun()
        
        
        
def render_workout_planner():
    st.header("Plan Your Workout")
    _render_workout_planner()