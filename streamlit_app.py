import streamlit as st
import subprocess
import threading
import time
import requests
import re
import os
import sys

st.set_page_config(page_title="Nodus Cafe", layout="wide")

@st.cache_resource
def start_server_and_tunnel():
    # Start Flask server
    flask_process = subprocess.Popen([sys.executable, "run.py"])
    
    # Wait for Flask to start
    time.sleep(3)
    
    # Start localtunnel
    lt_process = subprocess.Popen(
        ["npx", "-y", "localtunnel", "--port", "5000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    public_url = None
    for _ in range(10):
        line = lt_process.stdout.readline()
        if "your url is:" in line:
            public_url = line.split("your url is:")[1].strip()
            break
        time.sleep(1)
        
    return flask_process, lt_process, public_url

with st.spinner("Starting Nodus Cafe Backend & Tunneling..."):
    flask_proc, lt_proc, public_url = start_server_and_tunnel()

if public_url:
    st.success(f"Backend running at: {public_url}")
    
    # SQLite Database Integration for Streamlit Backend
    with st.expander("🛠️ SQLite Database Viewer (Streamlit Backend)"):
        import sqlite3
        import pandas as pd
        
        db_path = os.path.join("instance", "nodus_cafe.db")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
            
            if not tables.empty:
                selected_table = st.selectbox("Select Table to View:", tables['name'])
                if selected_table:
                    df = pd.read_sql_query(f"SELECT * FROM {selected_table} LIMIT 100", conn)
                    st.dataframe(df, use_container_width=True)
            conn.close()
        else:
            st.warning("SQLite DB not found yet. Flask is probably still initializing it.")

    # Embed the original app
    st.components.v1.iframe(public_url, width=1200, height=800, scrolling=True)
else:
    st.error("Failed to start localtunnel. Check logs.")
