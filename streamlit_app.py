import streamlit as st
import subprocess
import threading
import time
import requests
import re
import os

st.set_page_config(page_title="Nodus Cafe", layout="wide")

@st.cache_resource
def start_server_and_tunnel():
    # Start Flask server
    os.environ["WERKZEUG_RUN_MAIN"] = "true"
    flask_process = subprocess.Popen(["python", "run.py"])
    
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
    # Embed the original app
    st.components.v1.iframe(public_url, width=1200, height=800, scrolling=True)
else:
    st.error("Failed to start localtunnel. Check logs.")
