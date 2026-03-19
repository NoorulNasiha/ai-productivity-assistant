import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# -------------------- CONFIG --------------------
API = "http://localhost:5000"
st.set_page_config(page_title="AI Productivity Assistant", layout="wide")
st.title("AI Productivity Assistant")

# -------------------- DATA FETCH --------------------
@st.cache_data
def fetch_tasks():
    try:
        r = requests.get(f"{API}/get_tasks", timeout=5)
        r.raise_for_status()
        return pd.DataFrame(r.json())
    except Exception:
        return pd.DataFrame()

df = fetch_tasks()

# -------------------- TASK LIST --------------------
if df.empty:
    st.info("No tasks yet.")
else:
    st.subheader("Tasks")

    status_color = {
        "pending": "orange",
        "in progress": "blue",
        "completed": "green"
    }

    df_display = df.copy()
    df_display["status_color"] = (
        df_display["status"].map(status_color).fillna("black")
    )

    st.dataframe(
        df_display[["id", "description", "deadline", "priority", "status"]],
        use_container_width=True
    )

    # Completion metric
    completed = (df["status"] == "completed").sum()
    pct = int((completed / len(df)) * 100)
    st.metric("Completion", f"{pct}%")

    # Weekly productivity chart
    df["deadline_dt"] = pd.to_datetime(df["deadline"], errors="coerce")
    last7 = pd.Timestamp.now() - pd.Timedelta(days=7)
    comp = df[
        (df["status"] == "completed") &
        (df["deadline_dt"] >= last7)
    ]

    if not comp.empty:
        counts = (
            comp.groupby(comp["deadline_dt"].dt.date)
            .size()
            .reset_index(name="completed")
        )
        fig = px.bar(
            counts,
            x="deadline_dt",
            y="completed",
            labels={"deadline_dt": "Date"},
            title="Completed Tasks (Last 7 Days)"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No completions in the last 7 days.")

    # -------------------- UPDATE TASKS --------------------
    st.subheader("Update Tasks")

    for _, row in df.iterrows():
        with st.expander(f"Task {row['id']}: {row['description']}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Mark Completed (ID {row['id']})"):
                    requests.put(f"{API}/update_task/{row['id']}", json={"status": "completed"})
                    st.cache_data.clear()
                    st.rerun()

            with col2:
                new_priority = st.selectbox(
                    f"Set Priority (ID {row['id']})",
                    ["", "low", "medium", "high"],
                    index=0,
                    key=f"priority_{row['id']}"
                )
                if new_priority:
                    requests.put(f"{API}/update_task/{row['id']}", json={"priority": new_priority})
                    st.cache_data.clear()
                    st.rerun()

# -------------------- ADD TASK --------------------
st.subheader("Add Task via Natural Language")

text = st.text_input(
    "Describe task (e.g., 'Add meeting tomorrow at 10 AM')"
)

if st.button("Add Task"):
    if text.strip():
        r = requests.post(
            f"{API}/add_task",
            json={"text": text},
            timeout=5
        )
        if r.ok:
            st.success("Task added successfully")
            st.cache_data.clear()
            st.rerun()
        else:
            st.error(r.text)
    else:
        st.warning("Please enter a task description.")

# -------------------- EXPORTS --------------------
st.subheader("Export Tasks")

col1, col2 = st.columns(2)

with col1:
    if st.button("Download CSV"):
        r = requests.get(f"{API}/export/csv", timeout=5)
        if r.ok:
            st.download_button(
                label="Download CSV file",
                data=r.content,
                file_name="tasks.csv",
                mime="text/csv"
            )
        else:
            st.error("Failed to generate CSV")

with col2:
    if st.button("Download PDF"):
        r = requests.get(f"{API}/export/pdf", timeout=5)
        if r.ok:
            st.download_button(
                label="Download PDF file",
                data=r.content,
                file_name="tasks.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Failed to generate PDF")