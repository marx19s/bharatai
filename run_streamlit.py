import subprocess
import sys
import os

print("Starting Streamlit process...")
env = os.environ.copy()
env["PYTHONUNBUFFERED"] = "1"

# Run streamlit command and capture output
try:
    cmd = [
        r"C:\Users\sunny\.gemini\antigravity\scratch\bharatai\bharatai\.venv\Scripts\python.exe",
        "-m", "streamlit", "run", "app.py", "--server.port", "8501"
    ]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=r"C:\Users\sunny\.gemini\antigravity\scratch\bharatai\bharatai",
        env=env
    )
    
    # Wait for a few seconds to see if it runs or crashes
    try:
        stdout, stderr = process.communicate(timeout=6)
        print(f"Process exited with code: {process.returncode}")
        with open("run_streamlit.log", "w", encoding="utf-8") as f:
            f.write(f"EXIT CODE: {process.returncode}\n")
            f.write(f"STDOUT:\n{stdout}\n")
            f.write(f"STDERR:\n{stderr}\n")
    except subprocess.TimeoutExpired:
        print("Process is still running after 6 seconds (Success!). Detaching...")
        # Since it is still running, let it run in background and write current state
        with open("run_streamlit.log", "w", encoding="utf-8") as f:
            f.write("STATUS: STILL RUNNING\n")
except Exception as e:
    print(f"Error starting process: {e}")
    with open("run_streamlit.log", "w", encoding="utf-8") as f:
        f.write(f"EXCEPTION: {e}\n")
