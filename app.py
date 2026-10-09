import streamlit as st
import os
import json
import re
from groq import Groq
from langchain_community.tools.tavily_search import TavilySearchResults
import streamlit.components.v1 as components

# 1. Web Page Styling Configuration
st.set_page_config(
    page_title="AI Coding & Web Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 CodePilot AI")
st.markdown("AI-Powered Coding & Web Development Assistant.")

# 2. Check Streamlit Secrets Vault First, Fallback to Manual Inputs
groq_key = ""
tavily_key = ""

if "GROQ_API_KEY" in st.secrets:
    groq_key = st.secrets["GROQ_API_KEY"]
if "TAVILY_API_KEY" in st.secrets:
    tavily_key = st.secrets["TAVILY_API_KEY"]

if not groq_key or not tavily_key:
    st.sidebar.header("🔑 API Credentials (Local Fallback)")
    if not groq_key:
        groq_key = st.sidebar.text_input("Groq API Key", type="password")
    if not tavily_key:
        tavily_key = st.sidebar.text_input("Tavily API Key", type="password")
    
    if not groq_key or not tavily_key:
        st.warning("⚠️ Please provide both your Groq and Tavily API keys in the sidebar to get started.")
else:
    st.sidebar.success("🔒 API Keys securely loaded from Cloud Vault!")

# 3. Agent Logic Engine
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

# 4. Feature 1: One-Click Prompt Preset Buttons Layout
st.markdown("##### ⚡ Quick Templates")
col1, col2 = st.columns(2)

# Initialize prompt state if it doesn't exist
if "preset_prompt" not in st.session_state:
    st.session_state.preset_prompt = ""

if col1.button("📋 Load Factorial Template"):
    st.session_state.preset_prompt = "Write a recursive factorial program in Python."

if col2.button("🌐 Load Portfolio Template"):
    st.session_state.preset_prompt = "Create a modern single-page HTML portfolio template for a web developer with nice embedded CSS styles."

# 5. Main UI Input Form
user_prompt = st.text_area(
    "✍️ What should the agent build for you?", 
    value=st.session_state.preset_prompt,
    placeholder="Select a template above or type your own custom request..."
)

if st.button("🚀 Execute Agent Task"):
    if groq_key and tavily_key and user_prompt:
        with st.spinner("🤖 Agent is coordinating logic and tools..."):
            response = run_web_agent(user_prompt, groq_key, tavily_key)
            
            st.success("✅ Task Completed!")
            
            # Feature 2: Expanded Response View incorporating Live Rendering Framework
            tab1, tab2, tab3 = st.tabs(["📝 Formatted View", "🌐 Raw Code View", "🖥️ Live Visual Preview"])
            
            with tab1:
                st.markdown(response)
                
            # Extract code block using regular expressions
            extracted_code = re.findall(r"```(?:html|python)?(.*?)```", response, re.DOTALL)
            final_code = extracted_code.strip() if extracted_code else response
            is_html = "html" in user_prompt.lower()
            
            with tab2:
                if extracted_code:
                    st.code(final_code, language="html" if is_html else "python")
                    st.download_button(
                        label="📥 Download Generated File", 
                        data=final_code, 
                        file_name="index.html" if is_html else "script.py", 
                        mime="text/html" if is_html else "text/plain"
                    )
                else:
                    st.text(response)
                    
            with tab3:
                if is_html:
                    st.info("ℹ️ Showing sandboxed live view of the generated code below:")
                    # Safely render the extracted HTML code block as an embedded visual window element
                    components.html(final_code, height=500, scrolling=True)
                else:
                    st.warning("⚠️ Live Visual Preview is only available for web requests containing HTML code layouts.")
    else:
        st.error("❌ Please make sure your credentials and prompt input are not empty.")
