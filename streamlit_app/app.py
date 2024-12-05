import streamlit as st
import requests
import json

st.title("Conversational RAG Search")

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar for sources
st.sidebar.title("Sources")
sources_placeholder = st.sidebar.empty()

# Chat input
query = st.chat_input("Enter your query:")

if query:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": query})
    
    # # Display user message
    # with st.chat_message("user"):
    #     st.write(query)
    
    # Show loading spinner
    with st.spinner('Searching and generating answer...'):
        try:
            # Make a POST request to the Flask API
            response = requests.post(
                'http://localhost:5001/query', 
                json={'query': query},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', "No answer received.")
                sources = data.get('sources', [])
                
                # Add AI response to chat history
                st.session_state.chat_history.append({"role": "ai", "content": answer})
                
                # Display AI response
                with st.chat_message("ai"):
                    st.write(answer)
                
                # Update sources in sidebar
                sources_placeholder.markdown("### Related Sources")
                for source in sources:
                    sources_placeholder.write(source)
            
            else:
                st.error(f"Error: {response.status_code}")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Display chat history
for message in st.session_state.chat_history:
    if message['role'] == 'user':
        with st.chat_message("user"):
            st.write(message['content'])
    else:
        with st.chat_message("ai"):
            st.write(message['content'])