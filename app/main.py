import streamlit as st
import json
import os
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text

# 🌟 Streamlit Page Config
st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")

# 💄 Custom CSS for UI Styling
st.markdown("""
    <style>
        .main {
            background-color: #f4f6f9;
        }
        .title {
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            color: #4a4a4a;
        }
        .subtitle {
            font-size: 18px;
            text-align: center;
            color: #7a7a7a;
        }
        .stTextInput>div>div>input {
            font-size: 16px;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            font-size: 16px;
            border-radius: 10px;
        }
        .stCodeBlock {
            font-size: 14px;
        }
    </style>
""", unsafe_allow_html=True)

# History File Path
HISTORY_FILE = "history.json"

# 💾 Load Search History
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []  # Return an empty list if JSON is corrupted
    return []

# 💾 Save Search History
def save_history(url, email):
    history = load_history()
    history.append({"url": url, "email": email})
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

# 🚮 Clear Search History
def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    st.sidebar.warning("📁 Search history cleared!")

# 🏆 Sidebar for Portfolio Upload & History
st.sidebar.header("📂 Portfolio Settings")
portfolio = Portfolio()
portfolio.load_portfolio()
st.sidebar.success("Portfolio Loaded Successfully!")

st.sidebar.header("🔍 Search History")
history = load_history()

# 🚮 Clear History Button
if st.sidebar.button("🗑 Clear History"):
    clear_history()

# 📌 Display Recent Searches
if history:
    for index, item in enumerate(reversed(history[-5:])):  # Show last 5 searches
        unique_key = f"{item['url']}_{index}"  # Ensure unique keys for buttons
        if st.sidebar.button(item["url"], key=unique_key):
            st.markdown(f"### 📌 Email for: {item['url']}")
            st.code(item["email"], language="markdown")
else:
    st.sidebar.info("No search history yet.")

# 🎯 Main Title
st.markdown("<p class='title'>📧 Cold Mail Generator</p>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Generate tailored cold emails for job applications</p>", unsafe_allow_html=True)

# 🔗 URL Input
url_input = st.text_input("🔍 Enter Job URL:", value="https://jobs.nike.com/job/R-33460")

# 🚀 Submit Button
submit_button = st.button("✨ Generate Email")

# 🎯 Processing on Submit
if submit_button:
    try:
        with st.spinner("🔄 Processing..."):
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)

            # 💼 Extract Jobs
            chain = Chain()
            jobs = chain.extract_jobs(data)

            for job in jobs:
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email = chain.write_mail(job, links)

                # ✅ Display Generated Email
                st.markdown("### ✉️ Generated Cold Email:")
                st.code(email, language='markdown')

                # 📌 Save to History
                save_history(url_input, email)
        
        st.success("✅ Email Generated & Saved to History!")
    
    except Exception as e:
        st.error(f"❌ An Error Occurred: {e}")
