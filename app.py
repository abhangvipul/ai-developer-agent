import streamlit as st
import os
import json
import re
from groq import Groq
from langchain_community.tools.tavily_search import TavilySearchResults
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(
    page_title="CodePilot AI - Advanced Developer Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Injecting High-Contrast Light Mode Studio Styling
st.markdown("""
    <style>
    /* Clean Light Technical Grid Background */
    .stApp {
        background-color: #F8FAFC !important;
        background-image: radial-gradient(#CBD5E1 1px, transparent 1px) !important;
        background-size: 20px 20px !important;
    }
    
    /* High-Contrast Main Title and Subtitle Text overrides */
    h1, h2, h3, p {
        color: #0F172A !important;
    }
    
    /* Structured Light-Mode Glassmorphism Input Frame */
    div.stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 12px !important;
        font-family: 'Fira Code', monospace !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }
    div.stTextArea textarea:focus {
        border-color: #0284c7 !important;
        box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.2) !important;
    }
    
    /* Vibrant Professional Blue Interaction Button Layout */
    div.stButton > button {
        background: linear-gradient(90deg, #0284c7, #0369a1) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 12px 28px !important;
        border-radius: 8px !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.2) !important;
        width: 100%;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #0369a1, #024e73) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(2, 132, 199, 0.3) !important;
    }
    
    /* Dedicated Crisp Light Sidebar Overrides */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] p {
        color: #334155 !important;
    }
    
    /* Clean Tab Navigation Bar Configurations */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #E2E8F0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #F1F5F9 !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 6px 6px 0 0 !important;
        color: #64748B !important;
        padding: 8px 20px !important;
        font-weight: 500 !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #0284c7 !important;
        background-color: #E2E8F0 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #0284c7 !important;
        border-bottom: 2px solid #0284c7 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Main Dashboard Headers Structure Layout
st.markdown("<h1 style='margin-bottom: 0px;'>⚡ CodePilot AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:1.15rem; margin-top:2px; font-weight: 400;'>Advanced Neural Studio for Code Optimization & Layout Engineering</p>", unsafe_allow_html=True)

st.markdown("---")

# 4. Check Streamlit Secrets Vault First, Fallback to Manual Inputs
groq_key = ""
tavily_key = ""

if "GROQ_API_KEY" in st.secrets:
    groq_key = st.secrets["GROQ_API_KEY"]
if "TAVILY_API_KEY" in st.secrets:
    tavily_key = st.secrets["TAVILY_API_KEY"]

if not groq_key or not tavily_key:
    st.sidebar.markdown("### 🔑 API Core Credentials")
    if not groq_key:
        groq_key = st.sidebar.text_input("Groq API Key", type="password", help="Input your Groq cloud endpoint security handshake token")
    if not tavily_key:
        tavily_key = st.sidebar.text_input("Tavily API Key", type="password", help="Input your Tavily infrastructure system search token")
    
    if not groq_key or not tavily_key:
        st.sidebar.warning("⚠️ Action Required: Provide API Keys above to unlock neural compiling threads.")
else:
    st.sidebar.markdown("### 🔐 Security Shield Status")
    st.sidebar.success("🔒 Cloud Key Injection Active")
    st.sidebar.info("Dashboard is fully authenticated with credentials pulled securely from background environments.")

# 5. Agent Logic Engine
def run_web_agent(user_query, g_key, t_key):
    os.environ["TAVILY_API_KEY"] = t_key
    client = Groq(api_key=g_key)
    search_tool = TavilySearchResults(max_results=2)
    
    system_prompt = (
        "You are an expert AI Developer Agent powered by Groq and Tavily.\n"
        "Your goal is to write clean, optimized code and modern HTML/CSS templates.\n"
        "If you need to look up current syntax or design patterns, call your web search tool.\n\n"
        "You have access to a tool named 'web_search'.\n"
        "To use this tool, your output MUST be formatted exactly like this JSON block:\n"
        "{\n"
        "  \"action\": \"web_search\",\n"
        "  \"query\": \"search query text here\"\n"
        "}\n\n"
        "If you do not need to look anything up and have the final code ready, "
        "just reply directly with your explanation and code blocks."
    )
    
    current_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": str(user_query)}
    ]
    
    for turn in range(3):
        try:
            chat_completion = client.chat.completions.create(
                model="openai/gpt-oss-120b", 
                messages=current_messages,
                temperature=0.2,
                extra_body={"reasoning_effort": "low"}
            )
            agent_response = chat_completion.choices.message.content
            
            if '"action": "web_search"' in agent_response:
                start_idx = agent_response.find("{")
                end_idx = agent_response.rfind("}") + 1
                tool_call = json.loads(agent_response[start_idx:end_idx])
                search_query = tool_call.get("query")
                
                search_results = search_tool.invoke({"query": search_query})
                current_messages.append({"role": "assistant", "content": agent_response})
                current_messages.append({"role": "user", "content": f"Observation from web_search: {str(search_results)}"})
                continue
            else:
                return agent_response
        except Exception as e:
            return f"Error occurred: {str(e)}"
    return "Agent timed out."

# 6. Main Prompt Creation Canvas Area Layout
user_prompt = st.text_area(
    "✍️ Core Development Requirements Prompt Canvas", 
    height=150,
    placeholder="Describe your design specifications or engineering objectives here...\nExample: 'Build a fully responsive dashboard webpage using clean semantic HTML elements and CSS variables.'"
)

# 🧠 FIXED: Added explicit column weights [1, 2, 1] to partition layout correctly without crashes
_, col_btn, _ = st.columns([1, 2, 1])
with col_btn:
    execute_clicked = st.button("🚀 Initialise Compiling Request Thread")

if execute_clicked:
    if groq_key and tavily_key and user_prompt:
        with st.spinner("🧠 Orchestrating agent logic, web parameters, and context compilation branches..."):
            response = run_web_agent(user_prompt, groq_key, tavily_key)
            
            st.markdown("### 📤 Output Workspace Canvas Layout")
            
            tab1, tab2, tab3 = st.tabs(["📝 Formatted Architecture View", "💻 Raw Production Code Source", "🖥️ Sandboxed Live Interface Preview"])
            
            with tab1:
                st.markdown(response)
                
            extracted_code = re.findall(r"```(?:html|python)?(.*?)```", response, re.DOTALL)
            final_code = extracted_code.strip() if extracted_code else response
            is_html = "html" in user_prompt.lower()
            
            with tab2:
                if extracted_code:
                    st.code(final_code, language="html" if is_html else "python")
                    st.download_button(
                        label="📥 Download Generated File Archive", 
                        data=final_code, 
                        file_name="index.html" if is_html else "script.py", 
                        mime="text/html" if is_html else "text/plain"
                    )
                else:
                    st.text(response)
                    
            with tab3:
                if is_html:
                    st.markdown("<p style='color:#0284c7; font-weight:500;'>🌐 Sandbox Frame Canvas Instance Viewport:</p>", unsafe_allow_html=True)
                    components.html(final_code, height=650, scrolling=True)
                else:
                    st.warning("⚠️ Live Canvas Render Execution requires active HTML output layouts within the execution context template stream.")
    else:
        st.error("❌ Thread Blocked: Ensure both API key hashes and core engineering prompt inputs are populated before executing pipeline.")
