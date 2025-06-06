import streamlit as st
import requests
import json
from typing import List, Dict, Any

# Configure the app
st.set_page_config(
    page_title="Real Estate Chat Assistant",
    page_icon="🏠",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stTextInput > div > div > input {
        padding: 12px !important;
        border-radius: 8px !important;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        max-width: 80%;
    }
    .user-message {
        background-color: #f0f2f6;
        margin-left: 20%;
        border-bottom-right-radius: 0;
    }
    .assistant-message {
        background-color: #4CAF50;
        color: white;
        margin-right: 20%;
        border-bottom-left-radius: 0;
    }
    .chat-container {
        margin-bottom: 2rem;
        height: 70vh;
        overflow-y: auto;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your real estate assistant. How can I help you find your dream property today?"}
    ]

# Function to call the chat API
def call_chat_api(message: str, chat_history: List[Dict[str, str]]) -> Dict[str, Any]:
    """Call the FastAPI chat endpoint"""
    url = "http://app:8000/chat"  # Using service name in Docker network
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "message": message,
        "chat_history": chat_history,
        "model": "gpt-4o"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"status": "error", "message": f"Failed to get response: {str(e)}"}

# Display chat messages
st.title("🏠 Real Estate Assistant")
st.write("Ask me anything about properties, and I'll help you find what you're looking for!")

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)
    
    # Display assistant response in chat message container
    with st.spinner("Searching for properties..."):
        # Call the API
        response = call_chat_api(
            prompt,
            [msg for msg in st.session_state.messages if msg["role"] != "system"]
        )
        
        if response.get("status") == "success":
            assistant_response = response.get("message", "I'm sorry, I couldn't process that request.")
        else:
            assistant_response = "I'm sorry, there was an error processing your request. Please try again."
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(assistant_response, unsafe_allow_html=True)

# Add a clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your real estate assistant. How can I help you find your dream property today?"}
    ]
    st.rerun()
