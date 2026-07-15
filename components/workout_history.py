import streamlit as st
from logger.logger import setup_logger
from services.persistence.exercise_repository import get_users_exercises
import pandas as pd

log = setup_logger()

def render_workout_history():
    try:
        st.subheader("Workout History")
        user_id = st.session_state.get("user_id", 0)

        if isinstance(user_id, int):
            history_rows = get_users_exercises(user_id)
                
            arr = [
                {
                    "Exercise": row['exercise_name'],
                    "Reps": row['reps'],
                    "Sets": row['sets'],
                    "Time (sec)": round(row['duration_sec'], 1),
                    "Date": row['created_at']
                }
                for row in history_rows
            ]

            df = pd.DataFrame(arr)
            if not df.empty:
                df["Date"] = pd.to_datetime(df["Date"]).dt.date
                agg_df = df.groupby(["Exercise", "Date"]).agg({
                    "Reps": 'sum',
                    "Sets": "sum",
                    "Time (sec)": "sum"
                }).reset_index()
                agg_df.index += 1
                st.table(agg_df, border="horizontal")
            else:
                st.info("No workout history found.") 

    except Exception as e:
        log.error(f"Error rendering workout history: {e}")
        st.error("Failed to load workout history.")