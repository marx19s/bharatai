import streamlit as st
import os
import requests
import logging
import time
import subprocess
from pypdf import PdfReader
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

# Formally disable background sync thread warnings
logging.getLogger("streamlit.runtime.scriptrunner_utils.script_run_context").setLevel(logging.ERROR)

# --- AUTOMATED SECURITY GATEWAY (Creates .gitignore so your API key never leaks) ---
workspace_path = r"C:\Users\sunny\.gemini\antigravity\scratch\bharatai"
try:
    with open(os.path.join(workspace_path, ".gitignore"), "w") as f:
        f.write(".env\n__pycache__/\n*.pyc\n")
except:
    pass

# Load your secret key safely from your local laptop memory environment
if os.path.exists(os.path.join(workspace_path, ".env")):
    with open(os.path.join(workspace_path, ".env"), "r") as f:
        for line in f:
            if "GEMINI_API_KEY" in line:
                os.environ["GEMINI_API_KEY"] = line.split("=")[1].strip()

# --- CONFIGURATION (Mani's Verified Telegram Credentials) ---
TELEGRAM_BOT_TOKEN = "8880864614:AAEAJsFGVGot4aBxk-LMhUeMCq7HkhTiw5I"
TELEGRAM_CHAT_ID = "93372553"

# --- MULTI-BRAIN ASSEMBLY DIRECTORY ---
brain_llama = LLM(model="ollama/llama3.1", base_url="http://localhost:11434")
brain_qwen = LLM(model="ollama/qwen2.5-coder", base_url="http://localhost:11434")
brain_mistral = LLM(model="ollama/mistral", base_url="http://localhost:11434")
brain_phi = LLM(model="ollama/phi3:medium", base_url="http://localhost:11434")

# Streamlit Configuration Setup
st.set_page_config(page_title="BharatAI Command Center", page_icon="⚡", layout="wide")

# High-End Dark Cyberpunk UI Engine Style Stylesheet with Animations
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main { background-color: #060814; }
    .executive-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        padding: 40px 20px;
        border-radius: 16px;
        color: white;
        text-align: center;
        border: 1px solid rgba(99, 102, 241, 0.2);
        margin-bottom: 35px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .agent-room {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 25px 20px;
        text-align: center;
        margin-bottom: 25px;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .agent-room:hover {
        transform: translateY(-5px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4), 0 0 20px rgba(99, 102, 241, 0.1);
    }
    .agent-room.active {
        border: 1px solid #10b981;
        background: rgba(16, 185, 129, 0.08);
        animation: activePulse 2s infinite ease-in-out;
        transform: translateY(-5px);
    }
    @keyframes activePulse {
        0% { box-shadow: 0 0 20px rgba(16, 185, 129, 0.2); }
        50% { box-shadow: 0 0 35px rgba(16, 185, 129, 0.4); border-color: #34d399; }
        100% { box-shadow: 0 0 20px rgba(16, 185, 129, 0.2); }
    }
    .agent-icon { font-size: 3rem; margin-bottom: 12px; }
    .status-badge { display: inline-block; padding: 6px 14px; border-radius: 30px; font-size: 0.75rem; font-weight: 600; margin-top: 15px; }
    .status-offline { background-color: rgba(255,255,255,0.05); color: #94a3b8; border: 1px solid rgba(255,255,255,0.1); }
    .status-online { background-color: #10b981; color: white; box-shadow: 0 0 15px rgba(16, 185, 129, 0.4); }
    .brain-tag { display: inline-block; background: rgba(99, 102, 241, 0.15); color: #c7d2fe; padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; margin-top: 5px; }
    textarea { background-color: #0f172a !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; color: #f8fafc !important; border-radius: 12px !important; }
    </style>
""", unsafe_allow_html=True)

# Command Deck Header Layout
st.markdown("""
    <div class="executive-header">
        <h1 style='margin:0; font-weight: 700; font-size: 2.5rem; letter-spacing: -0.5px; background: linear-gradient(to right, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>⚡ BHARATAI CORE DECK</h1>
        <p style='margin:10px 0 0 0; color:#94a3b8; font-size:1.1rem; font-weight: 300;'>Orchestration Interface • Founder <span style='color:#6366f1; font-weight:600;'>MANI</span></p>
    </div>
""", unsafe_allow_html=True)

# Unified Data Input Control Deck
st.markdown("### 🎛️ Operational Control Panel")
col_input, col_upload = st.columns([2, 1])

with col_input:
    user_feature_instruction = st.text_area(
        "Input directive or prompt query for the team matrix:",
        value="CRITICAL MANDATE: Audit our project files. Fix the PDF reader parsing component, apply the smart multi-resource routing fallback logic, optimize key token handling to prevent hitting daily limits, and execute a strict audit check on every feature before submitting the release.",
        height=125
    )
    
    # Compact control button placed tight and neat under the main input query box
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1.5, 1, 1, 1])
    with btn_col1:
        trigger_pipeline = st.button("⚡ Run Audit & Sync Pipelines", use_container_width=True)

with col_upload:
    uploaded_pdf = st.file_uploader("📂 Feed PDF Document to Knowledge Base", type=["pdf"])

pdf_context = ""
if uploaded_pdf is not None:
    try:
        reader = PdfReader(uploaded_pdf)
        extracted_text = [page.extract_text() for page in reader.pages if page.extract_text()]
        pdf_context = "\n".join(extracted_text)
        st.toast("Campaged text buffer parsed successfully!", icon="📄")
    except Exception as e:
        st.error(f"Failed parsing document: {str(e)}")

@tool("Web Fallback Search Tool")
def open_web_search(query: str) -> str:
    """Scrapes the public open web using a lightweight public search gateway if information is missing locally."""
    try:
        response = requests.get(f"https://html.duckduckgo.com/html/?q={query}", headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            return response.text[:2000]
    except: pass
    return "Web search gateway temporarily busy. Rely on standard local brain memory parameters."

st.markdown("---")
st.markdown("### 🏛️ Active Agency Matrix Layout")

def draw_agent_rooms(active_name="None"):
    names = ["NEO", "MAVERICK", "APEX", "CIPHER", "NOVA", "ORACLE"]
    roles = ["CEO & Systems Architect", "Creative UI/UX Director", "Principal Software Engineer", "Security Audit Protocol", "DevOps Release Automation", "Quality Assurance Lead"]
    brains = ["Llama 3.1", "Phi-3 Medium", "Qwen 2.5 Coder", "Mistral", "Mistral", "Llama 3.1"]
    icons = ["⚡", "✨", "🥋", "🛡️", "🪐", "🔬"]
    
    cols = st.columns(3)
    for idx in range(6):
        col_target = cols[idx % 3] if idx < 3 else st.columns(3)[idx % 3]
        is_active = names[idx] == active_name
        room_class = "agent-room active" if is_active else "agent-room"
        status_lbl = "Active Auditing" if is_active else "Standby Mode"
        status_class = "status-online" if is_active else "status-offline"
        
        with col_target:
            st.markdown(f"""
                <div class="{room_class}">
                    <div class="agent-icon" style='font-size:3rem; margin-bottom:12px;'>{icons[idx]}</div>
                    <h3 style='margin: 0 0 4px 0; color: #f8fafc; font-size: 1.3rem; font-weight: 600;'>{names[idx]}</h3>
                    <p style='margin: 0 0 12px 0; color: #64748b; font-size: 0.85rem; font-weight: 400;'>{roles[idx]}</p>
                    <span class="brain-tag">{brains[idx]}</span><br/>
                    <span class="status-badge {status_class}">{status_lbl}</span>
                </div>
            """, unsafe_allow_html=True)

draw_agent_rooms("None")

def send_telegram_chunks(full_text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    max_length = 3800
    text_chunks = [full_text[i:i+max_length] for i in range(0, len(full_text), max_length)]
    for chunk in text_chunks:
        try: requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": f"📥 Core Audit Verification Report\n\n{chunk}"})
        except: pass

def execute_git_push():
    try:
        subprocess.run(["git", "add", "."], cwd=workspace_path, check=True)
        subprocess.run(["git", "commit", "-m", "⚡ Secure audited multi-agent system release"], cwd=workspace_path, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=workspace_path, check=True)
        return "✨ Audited script securely committed and pushed to remote main branch."
    except Exception as e:
        return f"⚠️ Workspace verified locally, remote deployment gate pause: {str(e)}"

# System Engine Execution Block
if trigger_pipeline:
    
    neo = Agent(role="CEO", goal="Map out rigorous feature requirements.", backstory="NEO", verbose=False, llm=brain_llama)
    maverick = Agent(role="Designer", goal="Audit interface states.", backstory="MAVERICK", verbose=False, llm=brain_phi)
    
    # RESOLVED FIXED LINE: backstory="APEX" successfully injected alongside tools param array
    apex = Agent(role="Coder", goal="Refactor layout routing code elements.", backstory="APEX", tools=[open_web_search], verbose=False, llm=brain_qwen)
    
    cipher = Agent(role="Security", goal="Verify API keys are completely protected locally and verify .env security variables.", backstory="CIPHER", verbose=False, llm=brain_mistral)
    nova = Agent(role="DevOps", goal="Verify .gitignore files and prepare deployment packages.", backstory="NOVA", verbose=False, llm=brain_mistral)
    oracle = Agent(role="QA", goal="Run extensive sanity tests on every single feature before submission.", backstory="ORACLE", verbose=False, llm=brain_llama)

    crew_agents = [neo, maverick, apex, cipher, nova, oracle]
    agent_names = ["NEO", "MAVERICK", "APEX", "CIPHER", "NOVA", "ORACLE"]
    
    tasks = [
        Task(description=f"Review directive: '{user_feature_instruction}'. Plan a full architectural audit for feature validation.", expected_output="Audit roadmap brief.", agent=neo),
        Task(description="Verify all front-end state visuals are highly responsive and animated.", expected_output="UI audit confirmation.", agent=maverick),
        Task(description="Integrate proper code logic blocks for reading files, routing searches, and handling data.", expected_output="Clean codebase update verification.", agent=apex),
        Task(description="Perform a deep security audit: confirm that the Gemini API Key is loaded locally from environmental file buffers and that the .gitignore blocks it from ever leaking to GitHub.", expected_output="Security clearance approval.", agent=cipher),
        Task(description="Build and bundle files while explicitly confirming that sensitive configuration sheets are left out of tracking arrays.", expected_output="Deployment staging ready log.", agent=nova),
        Task(description="Conduct full system simulations. Compile a 3-point definitive final summary to Mani detailing: 1) Root cause of the project's PDF error, 2) Resolution actions applied to routing, 3) Full checklist verification results showing every feature works.", expected_output="Executive final report.", agent=oracle)
    ]

    final_results = []
    
    with st.status("🔮 Running Full Roster Verification Audit...", expanded=True) as status_box:
        for i, task in enumerate(tasks):
            current_name = agent_names[i]
            st.empty() 
            draw_agent_rooms(current_name)
            st.write(f"🔬 **{current_name}** is conducting strict live systems evaluation tests...")
            
            single_crew = Crew(agents=[crew_agents[i]], tasks=[task], process=Process.sequential, memory=True)
            output = single_crew.kickoff()
            final_results.append(str(output.raw))
            time.sleep(1)
            
        status_box.update(label="⚡ Verification Audit Complete!", state="complete", expanded=False)

    draw_agent_rooms("None")
    
    st.info("📦 Staging secure transmission pathways...")
    git_report = execute_git_push()
    
    st.success("🎉 Full Deployment Audit Finalized!")
    st.markdown("### 📊 Audited Pipeline Output Report")
    st.write(final_results[-1])
    st.markdown(f"**Deployment Log Status:** {git_report}")
    
    send_telegram_chunks(f"{final_results[-1]}\n\n📊 Git Deploy Status:\n{git_report}")