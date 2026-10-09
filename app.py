import streamlit as st
import os
import json
import re
from groq import Groq
from langchain_community.tools.tavily_search import TavilySearchResults

# 1. Web Page Styling Configuration
st.set_page_config(
    page_title="AI Coding & Web Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 CodePilot AI")
st.markdown("AI-Powered Coding & Web Development Assistant.")

# 2. Sidebar Setup for API Keys
st.sidebar.header("🔑 API Credentials")
groq_key = st.sidebar.text_input("Groq API Key", type="password")
tavily_key = st.sidebar.text_input("Tavily API Key", type="password")

if not groq_key or not tavily_key:
    st.warning("⚠️ Please provide both your Groq and Tavily API keys in the sidebar to get started.")

# 3. Agent Logic Engine
def run_web_agent(user_query, g_key, t_key):
    # Set the key in the environment variables dynamically for the Tavily tool
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
            # Using the production-ready llama-3.3-70b-specdec tier on Groq
            chat_completion = client.chat.completions.create(
                model="openai/gpt-oss-120b", 
                messages=current_messages,
                temperature=0.2,
                extra_body={"reasoning_effort": "low"}
            )
            agent_response = chat_completion.choices[0].message.content
            
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

# 4. Main UI Input Form
user_prompt = st.text_area("✍️ What should the agent build for you?", 
                           placeholder="Example: 'Write a recursive factorial program in Python' or 'Create a modern HTML portfolio template'")

if st.button("🚀 Execute Agent Task"):
    if groq_key and tavily_key and user_prompt:
        with st.spinner("🤖 Agent is coordinating logic and tools..."):
            response = run_web_agent(user_prompt, groq_key, tavily_key)
            
            st.success("✅ Task Completed!")
            
            # Layout Response Tabs
            tab1, tab2 = st.tabs(["📝 Formatted View", "🌐 Raw Code View"])
            
            with tab1:
                st.markdown(response)
                
            with tab2:
                # Use regex to isolate code inside markdown wrappers for clean UI display
                extracted_code = re.findall(r"```(?:html|python)?(.*?)```", response, re.DOTALL)
                if extracted_code:
                    final_code = extracted_code[0].strip()
                    st.code(final_code, language="html" if "html" in user_prompt.lower() else "python")
                    
                    # File download capability
                    is_html = "html" in user_prompt.lower()
                    st.download_button(
                        label="📥 Download Generated File", 
                        data=final_code, 
                        file_name="index.html" if is_html else "script.py", 
                        mime="text/html" if is_html else "text/plain"
                    )
                else:
                    st.text(response)
    else:
        st.error("❌ Please make sure your credentials and prompt input are not empty.")