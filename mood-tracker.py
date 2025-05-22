import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# 🔄 Auto-refresh every 30 seconds
st_autorefresh(interval=30000, key="refresh")

# ---------------- Google Sheets Setup ---------------- #
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
gcp_credentials = dict(st.secrets["gcp_service_account"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(gcp_credentials, scope)
client = gspread.authorize(creds)
sheet = client.open("Mood Tracker").sheet1

# ---------------- Streamlit App ---------------- #
st.markdown("## Mood of the Queue")
st.markdown("---")

# Mood logging
st.subheader("📝 Log a Mood")

mood = st.radio("What's the vibe?", ["😊 Happy", "😠 Frustrating", "😕 Confusing", "😐 Neutral", "🎉 Satisfied"])
note = st.text_input("Optional Note")

if st.button("Submit"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mood_emoji = mood.split()[0]
    sheet.append_row([timestamp, mood_emoji, note])
    st.success(f"✅ Mood {mood} logged!")

# ---------------- Mood Visualization ---------------- #
st.markdown("---")
st.subheader("📊 Mood Summary")

# Date filtering
selected_date = st.date_input("Filter by date", value=pd.to_datetime("today").date())

# Load data from sheet
data = pd.DataFrame(sheet.get_all_records())

if not data.empty:
    try:
        data['Timestamp'] = pd.to_datetime(data['Timestamp'])
        filtered_data = data[data['Timestamp'].dt.date == selected_date]

        if 'Mood' in filtered_data.columns and not filtered_data.empty:
            mood_counts = filtered_data['Mood'].value_counts().reset_index()
            mood_counts.columns = ['Mood', 'Count']
            fig = px.bar(mood_counts, x='Mood', y='Count', title=f"Mood Count on {selected_date}")
            st.plotly_chart(fig)
        else:
            st.info("No mood data for selected date.")
    except Exception as e:
        st.error(f"Error reading data: {e}")
else:
    st.warning("Sheet is empty. Log some moods!")

# ---------------- Recent Logs ---------------- #
st.markdown("---")
st.subheader("📃 Recent Mood Logs")
if not data.empty:
    st.dataframe(data.sort_values("Timestamp", ascending=False).head(5))
