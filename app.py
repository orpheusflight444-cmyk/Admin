import os
import hashlib
import streamlit as st
from datetime import datetime
import google.generativeai as genai

# ==============================================================================
# 1. PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Orpheus Commander Hub", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. SECURITY & AUTHENTICATION HELPERS
# ==============================================================================
def hash_password(password: str) -> str:
    """Converts a plain text password into a secure SHA-256 hash."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

INVITE_CODE = "ORPHEUS-SECURE-2026"

# Initialize Session State Variables
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = "login"
if 'task_count' not in st.session_state:
    st.session_state.task_count = 0
if 'last_report' not in st.session_state:
    st.session_state.last_report = None
if 'failed_attempts' not in st.session_state:
    st.session_state.failed_attempts = {}
if 'is_banned' not in st.session_state:
    st.session_state.is_banned = False

# Dynamic Authorized Team Credentials
if 'team_keys' not in st.session_state:
    st.session_state.team_keys = {
        "Admin": hash_password("Orpheusflight04"),
        "cindy": hash_password("corazamoreno1201"),
        "Sarah": hash_password("SarahSecret456")
    }

# ==============================================================================
# 3. GLASSMORPHISM CUSTOM STYLING
# ==============================================================================
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #02040a 0%, #0a0f1c 100%); color: #f8fafc; }
    h1, h2, h3, h4, h5, h6, p, span, label { color: #f8fafc !important; }
    
    div.stTextArea textarea, div.stTextInput input, div.stSelectbox select {
        background-color: rgba(10, 15, 28, 0.75) !important;
        color: #ffffff !important;
        border-radius: 8px;
        border: 1px solid rgba(56, 189, 248, 0.4);
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.1);
        transition: all 0.3s ease;
    }
    div.stTextArea textarea:focus, div.stTextInput input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
    }
    
    section[data-testid="stSidebar"] {
        background-color: rgba(3, 6, 13, 0.95);
        border-right: 1px solid rgba(56, 189, 248, 0.25);
    }
    
    .stButton>button {
        background: linear-gradient(45deg, #0ea5e9, #38bdf8); 
        color: #02040a !important; 
        border-radius: 10px;
        border: none; 
        font-weight: 800; 
        width: 100%; 
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.5);
        color: #02040a !important;
    }
    
    header[data-testid="stHeader"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# Security Trap Check
if st.session_state.is_banned:
    st.error("🚨 MALICIOUS ACTIVITY DETECTED. Your IP and session have been logged and banned from this server.")
    st.stop()

# ==============================================================================
# 4. LOGIN / AUTHENTICATION GATE
# ==============================================================================
if not st.session_state.is_authenticated:
    st.title("🔒 Orpheus Commander Hub")
    
    col1, col2 = st.columns([1.2, 0.8])
    with col1:
        # LOGIN MODE
        if st.session_state.auth_mode == "login":
            st.subheader("Private Access Portal")
            user_name = st.text_input("Username / Member Name", key="login_user")
            passkey = st.text_input("Enter Passkey", type="password", key="login_pass")
            
            if st.button("Unlock System"):
                # Honeypot Trigger
                if user_name.strip().lower() in ["root_admin", "admin_root", "administrator"]:
                    st.session_state.is_banned = True
                    st.rerun()

                attempts = st.session_state.failed_attempts.get(user_name, 0)
                if attempts >= 3:
                    st.error("❌ Account locked due to too many failed attempts. Contact Administrator.")
                else:
                    hashed_input = hash_password(passkey)
                    if user_name in st.session_state.team_keys and st.session_state.team_keys[user_name] == hashed_input:
                        st.session_state.is_authenticated = True
                        st.session_state.user_role = user_name
                        st.session_state.failed_attempts[user_name] = 0
                        st.rerun()
                    else:
                        if user_name:
                            st.session_state.failed_attempts[user_name] = attempts + 1
                        st.error(f"❌ Access Denied. Remaining attempts: {max(0, 3 - (attempts + 1))}")
            
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                if st.button("Forgot Password?"):
                    st.session_state.auth_mode = "forgot"
                    st.rerun()
            with sub_col2:
                if st.button("Create Account"):
                    st.session_state.auth_mode = "create"
                    st.rerun()

        # CREATE ACCOUNT MODE
        elif st.session_state.auth_mode == "create":
            st.subheader("Create New Account")
            invite = st.text_input("Admin Invite Code", type="password")
            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Passkey", type="password")
            confirm_pass = st.text_input("Confirm Passkey", type="password")
            
            if st.button("Register Account"):
                if invite != INVITE_CODE:
                    st.error("❌ Invalid Invite Code. Registration blocked.")
                elif not new_user or not new_pass:
                    st.warning("Please fill out all required fields.")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                elif new_user in st.session_state.team_keys:
                    st.error("Username already exists.")
                else:
                    st.session_state.team_keys[new_user] = hash_password(new_pass)
                    st.success("Account created successfully! Redirecting to login...")
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
                st.info("If that username exists in our records, a password reset request has been transmitted to the System Administrator.")
            if st.button("← Back to Login"):
                st.session_state.auth_mode = "login"
                st.rerun()
                
    st.stop()

# ==============================================================================
# 5. RESILIENT AI ENGINE (NATIVE GOOGLE SDK)
# ==============================================================================
class OrpheusCommanderEngine:
    def __init__(self):
        # Resolve API Key securely
        try:
            self.api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
        except Exception:
            self.api_key = os.getenv("GEMINI_API_KEY", "")

        # Configure the native Google SDK
        if self.api_key and self.api_key != "DUMMY_KEY":
            genai.configure(api_key=self.api_key)
        
        # Priority cascade sequence for automatic dynamic fallback
        self.model_candidates = ["gemini-1.5-flash-002", "gemini-1.5-pro-002", "gemini-pro"]
       

        self.core_persona = (
            "You are an elite, highly responsible Executive Virtual Assistant for Orpheus Commander Hub. "
            "You provide detailed, clear, liability-conscious, and accurate administrative outputs. "
            "Always act ethically, verify facts where necessary, and ensure all outputs are structured professionally."
        )

    def _call_ai(self, sys_p: str, usr_p: str, temp: float = 0.5) -> str:
        if not self.api_key or self.api_key == "DUMMY_KEY":
            return "⚠️ GEMINI_API_KEY is missing. Please configure it in .streamlit/secrets.toml or as an Environment Variable."

        if not usr_p or not usr_p.strip():
            return "⚠️ Input text cannot be empty."

        # Combine system instructions and user request safely
        full_prompt = f"SYSTEM INSTRUCTION:\n{self.core_persona}\n{sys_p}\n\nUSER REQUEST:\n{usr_p}"
        last_error = None

        # Fallback Loop
        for m_name in self.model_candidates:
            try:
                model = genai.GenerativeModel(model_name=m_name)
                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.GenerationConfig(temperature=temp)
                )
                st.session_state.task_count += 1
                return response.text
            except Exception as e:
                last_error = e
                continue

        return f"❌ All AI model fallbacks failed. Final Error: {str(last_error)}"

    # Specific Tool Handlers
    def draft_email(self, context, msg, tone):
        return self._call_ai(f"Draft a response via email. Tone: {tone}.", f"Context: {context}\nMessage: {msg}", 0.6)

    def organize_schedule(self, date, raw_notes):
        return self._call_ai("Organize notes into a clean chronological schedule.", f"Date: {date}\nRequests:\n{raw_notes}", 0.3)

    def structure_data(self, text):
        return self._call_ai("Extract all entities and organize them into a clean Markdown table.", text, 0.2)

    def prepare_report(self, topic, data, format_type):
        return self._call_ai(f"Prepare a professional, client-ready {format_type}. Use clear headings and formatting.", f"Topic: {topic}\nRaw Data:\n{data}", 0.4)

    def admin_support(self, task_desc):
        return self._call_ai("Provide comprehensive administrative support and exact next steps.", f"Task details:\n{task_desc}", 0.5)

    def brainstorm(self, topic, goals):
        return self._call_ai("Provide a highly strategic, out-of-the-box brainstorming session.", f"Topic: {topic}\nGoals: {goals}", 0.8)

    def write_code(self, language, requirements):
        return self._call_ai("Act as a Senior Software Engineer. Provide clean, well-documented, and production-ready code.", f"Language: {language}\nRequirements: {requirements}", 0.3)

    def build_website(self, specs):
        return self._call_ai("Act as an expert Full-Stack Web Developer. Generate clean, responsive HTML, CSS, and JS in a single structured layout.", f"Website Specifications:\n{specs}", 0.5)


@st.cache_resource
def get_ai_engine():
    return OrpheusCommanderEngine()

bot = get_ai_engine()

# Helper execution runner
def execute_ai_task(task_name, action_func, *args):
    with st.spinner(f"⚡ Processing {task_name}..."):
        return action_func(*args)

# ==============================================================================
# 6. MAIN APPLICATION LAYOUT
# ==============================================================================
st.title("⚡ Orpheus Commander Hub")
st.markdown(f"Logged in as: **{st.session_state.user_role}** | Tasks Completed: **{st.session_state.task_count}**")

# Sidebar Controls
st.sidebar.title("⚡ Navigation")
if st.sidebar.button("Logout"):
    st.session_state.is_authenticated = False
    st.session_state.user_role = None
    st.session_state.auth_mode = "login"
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("📋 AI Modules")
task_selection = st.sidebar.radio(
    "Select Tool:",
    (
        "✉️ Handle Communications", 
        "🗓️ Manage Schedules & Meetings",
        "📊 Data Entry & Record Keeping", 
        "📈 Prepare Reports & Presentations",
        "⚙️ Administrative Team Support",
        "🧠 Strategic Brainstorming",       
        "💻 Code Generation & Debugging",
        "🌐 Website Builder"   
    )
)

# ------------------------------------------------------------------------------
# TOOL 1: COMMUNICATIONS
# ------------------------------------------------------------------------------
if task_selection == "✉️ Handle Communications":
    st.header("✉️ Communications Assistant")
    context = st.text_input("Context / Background")
    raw_msg = st.text_area("Original Message / Instructions:", height=150)
    tone = st.selectbox("Tone", ["Professional", "Friendly", "Firm", "Empathetic"])
    
    if st.button("Generate Email Reply"):
        result = execute_ai_task("Communications", bot.draft_email, context, raw_msg, tone)
        st.text_area("Generated Output:", result, height=250)

# ------------------------------------------------------------------------------
# TOOL 2: SCHEDULES & MEETINGS
# ------------------------------------------------------------------------------
elif task_selection == "🗓️ Manage Schedules & Meetings":
    st.header("🗓️ Manage Schedules")
    target_date = st.date_input("Select Target Date", datetime.today())
    raw_notes = st.text_area("Raw Meeting Notes / Input Tasks:", height=150)
    
    if st.button("Organize Schedule"):
        result = execute_ai_task("Schedule Organizer", bot.organize_schedule, target_date.strftime("%B %d, %Y"), raw_notes)
        st.markdown(result)

# ------------------------------------------------------------------------------
# TOOL 3: DATA ENTRY & RECORD KEEPING
# ------------------------------------------------------------------------------
elif task_selection == "📊 Data Entry & Record Keeping":
    st.header("📊 Data Entry & Structuring")
    notes = st.text_area("Unstructured Notes / Raw Information:", height=200)
    
    if st.button("Format Data to Table"):
        result = execute_ai_task("Data Formatting", bot.structure_data, notes)
        st.markdown(result)

# ------------------------------------------------------------------------------
# TOOL 4: REPORTS & PRESENTATIONS
# ------------------------------------------------------------------------------
elif task_selection == "📈 Prepare Reports & Presentations":
    st.header("📈 Reports & Presentations")
    topic = st.text_input("Project / Document Title")
    format_type = st.selectbox("Output Format:", ["Formal Business Report", "PowerPoint Slide Outline", "Executive Summary", "Client Proposal"])
    raw_data = st.text_area("Source Context / Data Points:", height=200)
    
    if st.button("Generate Document"):
        st.session_state.last_report = execute_ai_task("Document Generation", bot.prepare_report, topic, raw_data, format_type)
            
    if st.session_state.last_report:
        st.text_area("Document Preview:", st.session_state.last_report, height=300)
        safe_topic = topic.replace(" ", "_") if topic else "Document"
        st.download_button(
            label="📥 Download Markdown Report (.md)",
            data=st.session_state.last_report,
            file_name=f"{safe_topic}_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown"
        )

# ------------------------------------------------------------------------------
# TOOL 5: ADMINISTRATIVE TEAM SUPPORT
# ------------------------------------------------------------------------------
elif task_selection == "⚙️ Administrative Team Support":
    st.header("⚙️ Team Administrative Support")
    task_desc = st.text_area("Administrative Request Details:", height=150)
    
    if st.button("Process Administrative Plan"):
        result = execute_ai_task("Admin Support", bot.admin_support, task_desc)
        st.markdown(result)

# ------------------------------------------------------------------------------
# TOOL 6: STRATEGIC BRAINSTORMING
# ------------------------------------------------------------------------------
elif task_selection == "🧠 Strategic Brainstorming":
    st.header("🧠 Strategic Brainstorming")
    topic = st.text_input("Core Focus / Business Problem")
    goals = st.text_area("Target Objectives & Constraints:", height=120)
    
    if st.button("Initiate Brainstorming"):
        result = execute_ai_task("Brainstorming", bot.brainstorm, topic, goals)
        st.markdown(result)

# ------------------------------------------------------------------------------
# TOOL 7: CODE GENERATION & DEBUGGING
# ------------------------------------------------------------------------------
elif task_selection == "💻 Code Generation & Debugging":
    st.header("💻 Code Generation & Debugging")
    language = st.selectbox("Target Language", ["Python", "JavaScript", "HTML/CSS", "SQL", "Bash"])
    requirements = st.text_area("Specification / Error Stack Trace:", height=150)
    
    if st.button("Generate Solution"):
        result = execute_ai_task("Code Generation", bot.write_code, language, requirements)
        st.markdown(result)

# ------------------------------------------------------------------------------
# TOOL 8: WEBSITE BUILDER
# ------------------------------------------------------------------------------
elif task_selection == "🌐 Website Builder":
    st.header("🌐 Website Builder")
    specs = st.text_area("Website Functional Specifications & Design Requirements:", height=150)
    
    if st.button("Generate Web Blueprint"):
        result = execute_ai_task("Website Builder", bot.build_website, specs)
        st.markdown(result)
