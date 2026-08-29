import os
import streamlit as st
from datetime import datetime
from openai import OpenAI

# --- PAGE CONFIG & ELITE GLASSMORPHISM STYLING ---
st.set_page_config(page_title="Orpheus Commander Hub", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    /* Main Title Styling */
    h1 {
        color: #38bdf8;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        letter-spacing: -0.5px;
    }

    /* Glassmorphism Card Effect */
    div.stTextArea, div.stTextInput, div.stSelectbox {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 12px;
        border: 1px solid rgba(56, 189, 248, 0.2);
        backdrop-filter: blur(10px);
    }

    /* Colorful Gradient Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #0284c7, #38bdf8);
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: 700;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #0369a1, #0ea5e9);
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.6);
        transform: translateY(-2px);
        color: white;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #050811;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: #cbd5e1 !important;
        font-weight: 500;
    }
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span {
        color: #f8fafc !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'task_count' not in st.session_state:
    st.session_state.task_count = 0

# --- AI CORE LOGIC ---
class OrpheusCommanderEngine:
    def __init__(self, api_key=None):
        if api_key:
            self.api_key = api_key
        else:
            try:
                self.api_key = st.secrets["GEMINI_API_KEY"]
            except Exception:
                self.api_key = os.getenv("GEMINI_API_KEY", "")

        self.client = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=self.api_key
        )
        self.model = "gemini-3.6-flash"

    def _call_ai(self, system_prompt, user_prompt, temperature=0.5):
        if not user_prompt or not user_prompt.strip():
            return "⚠️ Warning: Input text cannot be empty."
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )
            st.session_state.task_count += 1
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ API Request Failed: {str(e)}"

    def draft_email(self, context, msg, tone):
        return self._call_ai(f"You are an elite Executive VA. Draft an email. Tone: {tone}.", f"Context: {context}\nMessage: {msg}", 0.6)

    def structure_data(self, text):
        return self._call_ai("You are a Data Entry VA. Extract all entities into a clean Markdown table.", text, 0.2)

    def social_post(self, topic, platform, points):
        return self._call_ai(f"You are a Digital Marketing VA. Create a high-converting post for {platform} with emojis and hashtags.", f"Topic: {topic}\nPoints: {points}", 0.7)

    def action_items(self, notes):
        return self._call_ai("You are an Operations VA. Extract action items into a numbered list with Task, Assignee, and Deadline.", notes, 0.3)

    def executive_brief(self, topic, source):
        return self._call_ai("You are an Executive Research VA. Create an executive summary with bold insights and strategic takeaways.", f"Topic: {topic}\nSource:\n{source}", 0.4)

    def invoice(self, client, items, total, due):
        return self._call_ai("You are a Finance VA. Generate a professional invoice template.", f"Client: {client}\nItems: {items}\nTotal: {total}\nDue: {due}", 0.3)

    def website_builder(self, biz_name, biz_type, style, features):
        sys_prompt = "You are an expert Full-Stack Web Developer VA. Write complete, beautiful, responsive HTML and CSS code for a landing page based on client requirements. Output clean code."
        usr_prompt = f"Business Name: {biz_name}\nType: {biz_type}\nStyle: {style}\nFeatures: {features}"
        return self._call_ai(sys_prompt, usr_prompt, 0.5)


# --- WEB INTERFACE ---
st.title("⚡ Orpheus Commander Virtual Assistant")
st.markdown("🚀 *Elite Glassmorphism AI Command Hub for Freelance & Agency Operations.*")

# Top Metrics Row (Live Analytics)
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("System Status", "Online ⚡", "100% Operational")
col_m2.metric("Tasks Executed", f"{st.session_state.task_count} Tasks", "Live Session")
col_m3.metric("AI Engine", "Gemini 3.6", "Ultra-Fast")
col_m4.metric("Platform Mode", "Advanced SaaS", "Active")

st.markdown("---")

bot = OrpheusCommanderEngine()

# --- CLIENT PORTAL & NAVIGATION GATE ---
st.sidebar.header("🔐 Access Portal")
portal_mode = st.sidebar.radio("Select Portal Mode", ["Commander Admin", "Paid Client Portal"])

if portal_mode == "Paid Client Portal":
    passkey = st.sidebar.text_input("Enter Client Passkey", type="password")
    if passkey != "OrpheusClient2026":
        st.sidebar.warning("🔒 Enter valid passkey to unlock client workspace (Test passkey: OrpheusClient2026)")
        st.stop()
    else:
        st.sidebar.success("🔓 Client Access Verified!")

st.sidebar.markdown("---")
st.sidebar.header("📋 Client Services Hub")
task_selection = st.sidebar.radio(
    "Choose a task to perform:",
    (
        "Draft Client Email", 
        "Convert Messy Notes to Table", 
        "Create Social Media Post",
        "Extract Action Items & Tasks",
        "Generate Executive Brief",
        "Generate Client Invoice",
        "🛠️ AI Website Builder (Paid Service)"
    )
)

st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Commander Protocol:**\n1. Input project specifications.\n2. Run AI generation.\n3. Export & deliver deliverables!")

# 1. EMAIL DRAFTER
if task_selection == "Draft Client Email":
    st.header("✉️ Draft Client Email")
    context = st.text_input("Who are we emailing? (Context)")
    raw_msg = st.text_area("Paste incoming message or instructions:", height=150)
    tone = st.selectbox("Select Tone", ["Professional", "Friendly", "Firm", "Apologetic"])
    if st.button("✨ Generate Email Reply"):
        with st.spinner("Drafting response..."):
            res = bot.draft_email(context, raw_msg, tone)
            st.success("Done!")
            st.text_area("Copy output:", res, height=250)
            st.download_button("📥 Download Email (.txt)", res, file_name="client_email_reply.txt", mime="text/plain")

# 2. DATA ENTRY
elif task_selection == "Convert Messy Notes to Table":
    st.header("📊 Data Entry & Formatting")
    notes = st.text_area("Paste unstructured client notes:", height=200)
    if st.button("✨ Format Data"):
        with st.spinner("Structuring data..."):
            res = bot.structure_data(notes)
            st.success("Done!")
            st.markdown(res)
            st.download_button("📥 Download Table Data (.md)", res, file_name="structured_data.md", mime="text/markdown")

# 3. SOCIAL MEDIA
elif task_selection == "Create Social Media Post":
    st.header("📱 Social Media Manager")
    c1, c2 = st.columns(2)
    with c1:
        platform = st.selectbox("Platform", ["Facebook", "LinkedIn", "Instagram", "Twitter"])
    with c2:
        topic = st.text_input("Main Topic")
    points = st.text_area("Specific details to include:", height=100)
    if st.button("✨ Generate Post"):
        with st.spinner("Crafting viral content..."):
            res = bot.social_post(topic, platform, points)
            st.success("Done!")
            st.text_area("Copy post:", res, height=220)
            st.download_button("📥 Download Post (.txt)", res, file_name="social_post.txt", mime="text/plain")

# 4. ACTION ITEMS
elif task_selection == "Extract Action Items & Tasks":
    st.header("✅ Action Item Extractor")
    notes = st.text_area("Paste meeting transcript or notes:", height=200)
    if st.button("✨ Extract Tasks"):
        with st.spinner("Analyzing meeting notes..."):
            res = bot.action_items(notes)
            st.success("Done!")
            st.text_area("Copy action items:", res, height=220)
            st.download_button("📥 Download Tasks (.txt)", res, file_name="action_items.txt", mime="text/plain")

# 5. EXECUTIVE BRIEF
elif task_selection == "Generate Executive Brief":
    st.header("📝 Executive Research Brief")
    topic = st.text_input("Research Topic")
    source = st.text_area("Paste article, report, or text:", height=200)
    if st.button("✨ Generate Brief"):
        with st.spinner("Summarizing research..."):
            res = bot.executive_brief(topic, source)
            st.success("Done!")
            st.text_area("Copy executive brief:", res, height=220)
            st.download_button("📥 Download Brief (.md)", res, file_name="executive_brief.md", mime="text/markdown")

# 6. INVOICE
elif task_selection == "Generate Client Invoice":
    st.header("💳 Client Invoice & Billing Generator")
    c_name = st.text_input("Client Name / Company")
    c_items = st.text_area("Services Rendered / Itemized Details", height=100)
    ca, cb = st.columns(2)
    with ca:
        c_total = st.text_input("Total Amount")
    with cb:
        c_due = st.text_input("Due Date")
    if st.button("✨ Generate Invoice"):
        with st.spinner("Compiling invoice..."):
            res = bot.invoice(c_name, c_items, c_total, c_due)
            st.success("Done!")
            st.text_area("Copy invoice:", res, height=250)
            st.download_button("📥 Download Invoice (.txt)", res, file_name="client_invoice.txt", mime="text/plain")

# 7. AI WEBSITE BUILDER (PAID SERVICE)
elif task_selection == "🛠️ AI Website Builder (Paid Service)":
    st.header("🛠️ AI Website Code & Wireframe Generator")
    st.markdown("Use this tool when a client pays you to build a custom landing page. Enter their specifications to generate production-ready code!")
    
    wb_name = st.text_input("Business Name")
    wb_type = st.text_input("Business Type (e.g., Cafe, Startup, Portfolio)")
    wb_style = st.selectbox("Design Aesthetic", ["Modern & Minimalist", "Dark & Cyberpunk", "Warm & Cozy", "Sleek & Corporate"])
    wb_features = st.text_area("Required Sections (e.g., Hero, About, Menu, Contact Form)", height=100)
    
    if st.button("✨ Generate Full Website Code"):
        with st.spinner("Coding website architecture..."):
            res = bot.website_builder(wb_name, wb_type, wb_style, wb_features)
            st.success("Website Code Generated Successfully!")
            st.code(res, language="html")
            st.download_button("📥 Download Website Code (.html)", res, file_name="index.html", mime="text/html")