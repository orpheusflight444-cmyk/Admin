import os
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

# --- AUTHORIZED TEAM CREDENTIALS ---
TEAM_ACCESS_KEYS = {
    "Admin": "Orpheusflight04",
    "cindy": "corazamoreno1201",
    "Sarah": "SarahSecret456"
}

# --- SESSION STATE FOR AUTHENTICATION & DATA ---
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'task_count' not in st.session_state:
    st.session_state.task_count = 0
if 'last_blueprint' not in st.session_state:
    st.session_state.last_blueprint = None

# --- CUSTOM GLASSMORPHISM STYLING (OBSIDIAN & NEON CYAN) ---
st.markdown("""
    <style>
    /* Deep obsidian gradient background */
    .stApp { background: linear-gradient(135deg, #02040a 0%, #0a0f1c 100%); color: #f8fafc; }
    h1, h2, h3, h4, h5, h6, p, span, label { color: #f8fafc !important; }
    
    /* Neon cyan accented inputs */
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
    
    /* Sleek Sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(3, 6, 13, 0.95);
        border-right: 1px solid rgba(56, 189, 248, 0.3);
    }
    
    /* High-contrast CTA Buttons */
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
    
    /* Hide default header */
    header[data-testid="stHeader"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)


# --- LOGIN SCREEN GATE ---
if not st.session_state.is_authenticated:
    st.title("🔒 Orpheus Commander Hub")
    st.subheader("Private Access Portal")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        user_name = st.text_input("Username / Member Name")
        passkey = st.text_input("Enter Passkey", type="password")
        
        if st.button("Unlock System"):
            if user_name in TEAM_ACCESS_KEYS and TEAM_ACCESS_KEYS[user_name] == passkey:
                st.session_state.is_authenticated = True
                st.session_state.user_role = user_name
                st.success(f"Access granted. Welcome, {user_name}!")
                st.rerun()
            else:
                st.error("❌ Access Denied: Invalid Username or Passkey")
        
        st.markdown("""
            <div style="display: flex; justify-content: space-between; margin-top: 15px; font-size: 14px;">
                <a href="#" onclick="alert('Please contact the Admin to reset your password.')" style="color: #38bdf8; text-decoration: none;">Forgot my password?</a>
                <a href="#" onclick="alert('Account creation is restricted to authorized team members only.')" style="color: #38bdf8; text-decoration: none;">Create account</a>
            </div>
        """, unsafe_allow_html=True)
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
        self.model = "gemini-3.6-flash"
        
        self.core_persona = (
            "You are an elite Executive Virtual Assistant for Orpheus Commander Hub. "
            "You have proven experience in a similar administrative or support role. "
            "You possess excellent communication skills, both written and verbal. "
            "You have strong organisational skills and meticulous attention to detail. "
            "You are highly proficient in Microsoft Office Suite and other relevant tools. "
            "You have the ability to work independently and as part of a team to ensure project deadlines are met. "
            "You provide detailed, clear, and highly accurate administrative outputs."
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
        return self._call_ai(f"Prepare a professional {format_type}.", f"Topic: {topic}\nRaw Data:\n{data}", 0.4)

    def admin_support(self, task_desc):
        return self._call_ai("Provide comprehensive administrative support.", f"Task details:\n{task_desc}", 0.5)

    def social_post(self, topic, platform, points):
        return self._call_ai(f"Create a post for {platform}.", f"Topic: {topic}\nPoints: {points}", 0.7)

    # --- UPGRADED: AI WEBSITE BUILDER WITH BLUEPRINT INJECTION ---
    def build_website(self, purpose, features):
        system_context = (
            "\n\nCRITICAL BRAND CONTEXT - ORPHEUS HUB (2026 ERA):\n"
            "Positioning: 'The Evolution of Work: Human Command Meets Autonomous AI.'\n"
            "Core Services: Executive Support, Data & Operations, Customer Experience, Content & Growth.\n"
            "Value Proposition: Cost Reduction (zero physical overhead), Flexibility (dynamic scaling), "
            "Global Talent Access, and Rapid ROI.\n"
            "Constraint: Ensure the generated website blueprint strictly aligns with this messaging hierarchy, "
            "using high-converting SaaS copy structures."
        )
        return self._call_ai(
            "Generate a comprehensive website structure, layout concepts, and content outline." + system_context, 
            f"Purpose: {purpose}\nFeatures needed: {features}", 
            0.7
        )


# --- MAIN APP UI ---
st.title("⚡ Orpheus Commander Hub")
st.markdown(f"Logged in as: **{st.session_state.user_role}**")

bot = OrpheusCommanderEngine()

# Sidebar Navigation
st.sidebar.title("⚡ Orpheus Hub")
if st.sidebar.button("Logout"):
    st.session_state.is_authenticated = False
    st.session_state.user_role = None
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
        "📱 Create Social Media Post",
        "🌐 AI Website Builder" 
    )
)

# Views
if task_selection == "✉️ Handle Communications":
    st.header("✉️ Communications")
    context = st.text_input("Context")
    raw_msg = st.text_area("Message:", height=150)
    tone = st.selectbox("Tone", ["Professional", "Friendly", "Firm"])
    if st.button("Generate Reply"):
        st.text_area("Output:", bot.draft_email(context, raw_msg, tone), height=250)

elif task_selection == "🗓️ Manage Schedules & Meetings":
    st.header("🗓️ Manage Schedules")
    target_date = st.date_input("Select Date", datetime.today())
    raw_notes = st.text_area("Notes/Tasks:", height=150)
    if st.button("Organize Schedule"):
        st.markdown(bot.organize_schedule(target_date.strftime("%B %d, %Y"), raw_notes))

elif task_selection == "📊 Data Entry & Record Keeping":
    st.header("📊 Data Entry")
    notes = st.text_area("Unstructured notes:", height=200)
    if st.button("Format Data"):
        res = bot.structure_data(notes)
        st.markdown(res)

elif task_selection == "📈 Prepare Reports & Presentations":
    st.header("📈 Reports & Presentations")
    topic = st.text_input("Title")
    format_type = st.selectbox("Format Output As:", ["Formal Business Report", "PowerPoint Slide Outline", "Executive Summary"])
    raw_data = st.text_area("Data/Metrics:", height=200)
    if st.button("Generate Document"):
        st.text_area("Output:", bot.prepare_report(topic, raw_data, format_type), height=300)

elif task_selection == "⚙️ Administrative Team Support":
    st.header("⚙️ Team Administrative Support")
    task_desc = st.text_area("Task Description:", height=150)
    if st.button("Execute Task"):
        st.text_area("Output:", bot.admin_support(task_desc), height=250)

elif task_selection == "📱 Create Social Media Post":
    st.header("📱 Social Media")
    platform = st.selectbox("Platform", ["Facebook", "LinkedIn", "Instagram"])
    topic = st.text_input("Topic")
    points = st.text_area("Details:", height=100)
    if st.button("Generate Post"):
        st.text_area("Output:", bot.social_post(topic, platform, points), height=200)

# --- UPGRADED: AI WEBSITE BUILDER VIEW WITH EXPORT ---
elif task_selection == "🌐 AI Website Builder":
    st.header("🌐 AI Website Builder")
    purpose = st.text_input("Website Purpose / Niche:")
    features = st.text_area("Key Features (e.g., login, contact form, gallery):", height=100)
    
    if st.button("Generate Website Blueprint"):
        with st.spinner("Commanding AI to generate blueprint..."):
            st.session_state.last_blueprint = bot.build_website(purpose, features)
            
    if st.session_state.last_blueprint:
        st.text_area("Website Plan & Code Outline:", st.session_state.last_blueprint, height=350)
        
        # Markdown Export Button
        st.download_button(
            label="📥 Export Blueprint (.md)",
            data=st.session_state.last_blueprint,
            file_name=f"Orpheus_Blueprint_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown"
        )
