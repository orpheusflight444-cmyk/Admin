import os
import time
import streamlit as st
from datetime import datetime
from openai import OpenAI

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Orpheus Commander Hub", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE FOR AUTHENTICATION & DATA ---
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'task_count' not in st.session_state:
    st.session_state.task_count = 0
if 'last_blueprint' not in st.session_state:
    st.session_state.last_blueprint = None
if 'last_report' not in st.session_state:
    st.session_state.last_report = None
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = "login"

# Dynamic Authorized Team Credentials
if 'team_keys' not in st.session_state:
    st.session_state.team_keys = {
        "Admin": "Orpheusflight04",
        "cindy": "corazamoreno1201",
        "Sarah": "SarahSecret456"
    }

# --- CUSTOM GLASSMORPHISM STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #02040a 0%, #0a0f1c 100%); color: #f8fafc; }
    h1, h2, h3, h4, h5, h6, p, span, label { color: #f8fafc !important; }
    
    div.stTextArea textarea, div.stTextInput input, div.stSelectbox select {
        background-color: rgba(10, 15, 28, 0.7) !important;
        color: white !important;
        border-radius: 8px;
        border: 1px solid rgba(56, 189, 248, 0.5);
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.1);
        transition: all 0.3s ease;
    }
    div.stTextArea textarea:focus, div.stTextInput input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
    }
    
    section[data-testid="stSidebar"] {
        background-color: rgba(3, 6, 13, 0.95);
        border-right: 1px solid rgba(56, 189, 248, 0.3);
    }
    
    .stButton>button {
        background: linear-gradient(45deg, #0ea5e9, #38bdf8); color: #02040a; border-radius: 10px;
        border: none; font-weight: 800; width: 100%; transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.5);
        color: #02040a;
    }
    
    .text-btn { background: transparent !important; color: #38bdf8 !important; box-shadow: none !important; border: 1px solid #38bdf8 !important; }
    
    header[data-testid="stHeader"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)


# --- LOGIN SCREEN GATE ---
if not st.session_state.is_authenticated:
    st.title("🔒 Orpheus Commander Hub")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        # LOGIN MODE
        if st.session_state.auth_mode == "login":
            st.subheader("Private Access Portal")
            user_name = st.text_input("Username / Member Name", key="login_user")
            passkey = st.text_input("Enter Passkey", type="password", key="login_pass")
            
            if st.button("Unlock System"):
                if user_name in st.session_state.team_keys and st.session_state.team_keys[user_name] == passkey:
                    st.session_state.is_authenticated = True
                    st.session_state.user_role = user_name
                    st.success(f"Access granted. Welcome, {user_name}!")
                    st.rerun()
                else:
                    st.error("❌ Access Denied: Invalid Username or Passkey")
            
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                if st.button("Forgot my password?"):
                    st.session_state.auth_mode = "forgot"
                    st.rerun()
            with sub_col2:
                if st.button("Create account"):
                    st.session_state.auth_mode = "create"
                    st.rerun()

        # CREATE ACCOUNT MODE
        elif st.session_state.auth_mode == "create":
            st.subheader("Create New Account")
            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Passkey", type="password")
            confirm_pass = st.text_input("Confirm Passkey", type="password")
            
            if st.button("Register Account"):
                if not new_user or not new_pass:
                    st.warning("Please fill out all fields.")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                elif new_user in st.session_state.team_keys:
                    st.error("Username already exists.")
                else:
                    st.session_state.team_keys[new_user] = new_pass
                    st.success("Account successfully created! You can now log in.")
                    st.session_state.auth_mode = "login"
                    st.rerun()
                    
            if st.button("← Back to Login"):
                st.session_state.auth_mode = "login"
                st.rerun()

        # FORGOT PASSWORD MODE
        elif st.session_state.auth_mode == "forgot":
            st.subheader("Account Recovery")
            recover_user = st.text_input("Enter your Username")
            
            if st.button("Recover Passkey"):
                if recover_user in st.session_state.team_keys:
                    st.info(f"System verified. Your recovered passkey is: **{st.session_state.team_keys[recover_user]}**")
                else:
                    st.error("Username not found in our records.")
                    
            if st.button("← Back to Login"):
                st.session_state.auth_mode = "login"
                st.rerun()
                
    st.stop()


# --- AI ENGINE ---
class OrpheusCommanderEngine:
    def __init__(self):
        try:
            self.api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            self.api_key = os.getenv("GEMINI_API_KEY", "")
            
        self.client = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=self.api_key
        )
        self.model = "gemini-1.5-flash" 
        
        self.core_persona = (
            "You are an elite, highly responsible Executive Virtual Assistant for Orpheus Commander Hub. "
            "You provide detailed, clear, liability-conscious, and highly accurate administrative outputs. "
            "Always act ethically, verifying facts where necessary, and ensure all outputs are structured professionally."
        )

    def _call_ai(self, sys_p, usr_p, temp=0.5):
        if not usr_p or not usr_p.strip():
            return "⚠️ Input text cannot be empty."
        try:
            res = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": self.core_persona + sys_p}, {"role": "user", "content": usr_p}],
                temperature=temp
            )
            st.session_state.task_count += 1
            return res.choices[0].message.content
        except Exception as e:
            return f"❌ API Error: {str(e)}"

    def draft_email(self, context, msg, tone):
        return self._call_ai(f"Draft a response via email. Tone: {tone}.", f"Context: {context}\nMessage: {msg}", 0.6)

    def structure_data(self, text):
        return self._call_ai("Extract all entities and organize them into a clean Markdown table.", text, 0.2)

    def organize_schedule(self, date, raw_notes):
        return self._call_ai("Organize notes into a clean chronological schedule.", f"Date: {date}\nRequests:\n{raw_notes}", 0.3)

    def prepare_report(self, topic, data, format_type):
        return self._call_ai(f"Prepare a professional, client-ready {format_type}. Use clear headings and formatting.", f"Topic: {topic}\nRaw Data:\n{data}", 0.4)

    def admin_support(self, task_desc):
        return self._call_ai("Provide comprehensive administrative support and exact next steps.", f"Task details:\n{task_desc}", 0.5)

    def brainstorm(self, topic, goals):
        return self._call_ai("Provide a highly strategic, out-of-the-box brainstorming session.", f"Topic: {topic}\nGoals: {goals}", 0.8)

    def write_code(self, language, requirements):
        return self._call_ai("Act as a Senior Software Engineer. Provide clean, well-documented, and highly responsible code.", f"Language: {language}\nRequirements: {requirements}", 0.3)

    def build_website(self, specs):
        return self._call_ai("Act as an expert Full-Stack Web Developer. Generate clean, responsive HTML, CSS, and JS based on the user's request. Output the complete code clearly.", f"Website Specifications:\n{specs}", 0.5)


# --- UI HELPER: COUNTDOWN & SPINNER ---
def run_with_timer(task_name, action_func, *args):
    """Provides a 3-second countdown and a loading spinner so the user knows it isn't frozen."""
    placeholder = st.empty()
    # 3-second countdown
    for i in range(3, 0, -1):
        placeholder.info(f"⏳ Initiating {task_name}... Please wait {i} seconds.")
        time.sleep(1)
    placeholder.empty()
    
    # Run the actual AI function while showing a spinner
    with st.spinner(f"⚡ Processing {task_name}... Waiting for AI response."):
        return action_func(*args)


# --- MAIN APP UI ---
st.title("⚡ Orpheus Commander Hub")
st.markdown(f"Logged in as: **{st.session_state.user_role}**")

bot = OrpheusCommanderEngine()

# Sidebar Navigation
st.sidebar.title("⚡ Orpheus Hub")
if st.sidebar.button("Logout"):
    st.session_state.is_authenticated = False
    st.session_state.user_role = None
    st.session_state.auth_mode = "login"
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("📋 Services")
task_selection = st.sidebar.radio(
    "Choose a task:",
    (
        "✉️ Handle Communications", 
        "🗓️ Manage Schedules & Meetings",
        "📊 Data Entry & Record Keeping", 
        "📈 Prepare Reports & Presentations",
        "⚙️ Administrative Team Support",
        "🧠 Strategic Brainstorming",       
        "💻 Code Generation & Debugging",
        "🌐 Website Builder"   # Added back the Website Builder
    )
)

# Views
if task_selection == "✉️ Handle Communications":
    st.header("✉️ Communications")
    context = st.text_input("Context")
    raw_msg = st.text_area("Message:", height=150)
    tone = st.selectbox("Tone", ["Professional", "Friendly", "Firm", "Empathetic"])
    if st.button("Generate Reply"):
        result = run_with_timer("Communications", bot.draft_email, context, raw_msg, tone)
        st.text_area("Output:", result, height=250)

elif task_selection == "🗓️ Manage Schedules & Meetings":
    st.header("🗓️ Manage Schedules")
    target_date = st.date_input("Select Date", datetime.today())
    raw_notes = st.text_area("Notes/Tasks:", height=150)
    if st.button("Organize Schedule"):
        result = run_with_timer("Schedule Organizer", bot.organize_schedule, target_date.strftime("%B %d, %Y"), raw_notes)
        st.markdown(result)

elif task_selection == "📊 Data Entry & Record Keeping":
    st.header("📊 Data Entry")
    notes = st.text_area("Unstructured notes:", height=200)
    if st.button("Format Data"):
        result = run_with_timer("Data Formatting", bot.structure_data, notes)
        st.markdown(result)

elif task_selection == "📈 Prepare Reports & Presentations":
    st.header("📈 Reports & Presentations")
    topic = st.text_input("Client / Project Title")
    format_type = st.selectbox("Format Output As:", ["Formal Business Report", "PowerPoint Slide Outline", "Executive Summary", "Client Proposal"])
    raw_data = st.text_area("Data/Metrics/Context:", height=200)
    
    if st.button("Generate Document"):
        st.session_state.last_report = run_with_timer("Document Generation", bot.prepare_report, topic, raw_data, format_type)
            
    if st.session_state.last_report:
        st.text_area("Preview Output:", st.session_state.last_report, height=300)
        
        # --- DIRECT FILE DOWNLOAD FOR CLIENT ---
        safe_topic = topic.replace(" ", "_") if topic else "Document"
        st.download_button(
            label="📥 Download File for Client (.md)",
            data=st.session_state.last_report,
            file_name=f"{safe_topic}_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown"
        )

elif task_selection == "⚙️ Administrative Team Support":
    st.header("⚙️ Team Administrative Support")
    task_desc = st.text_area("Task Description:", height=150)
    if st.button("Execute Task"):
        result = run_with_timer("Admin Task", bot.admin_support, task_desc)
        st.text_area("Output:", result, height=250)

elif task_selection == "🧠 Strategic Brainstorming":
    st.header("🧠 Strategic Brainstorming")
    topic = st.text_input("Core Topic / Problem")
    goals = st.text_area("Desired Outcomes & Goals:", height=100)
    if st.button("Initiate Brainstorm"):
        result = run_with_timer("Brainstorming Session", bot.brainstorm, topic, goals)
        st.markdown(result)

elif task_selection == "💻 Code Generation & Debugging":
    st.header("💻 Code Generation & Debugging")
    language = st.selectbox("Programming Language", ["Python", "JavaScript", "HTML/CSS", "SQL", "Bash"])
    requirements = st.text_area("Task or Bug Details:", height=150)
    if st.button("Generate Code"):
        result = run_with_timer("Code Generation", bot.write_code, language, requirements)
        st.markdown(result)

elif task_selection == "🌐 Website Builder":
    st.header("🌐 Website Builder")
    specs = st.text_area("Website Specifications & Features:", height=150)
    if st.button("Generate Website"):
        result = run_with_timer("Website Build", bot.build_website, specs)
        st.markdown(result)
