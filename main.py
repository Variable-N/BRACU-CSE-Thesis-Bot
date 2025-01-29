import os
import json
import streamlit as st
from groq import Groq
import chromadb
from PIL import Image
# GROQ INITIALIZATION
working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))
GROQ_API_KEY = config_data["GROQ_API_KEY"]
os.environ['GROQ_API_KEY'] = GROQ_API_KEY
client = Groq()

chroma_client = chromadb.PersistentClient(path="C:/Users/Niloy/Desktop/Chatbot with RAG/vector_database")
collection = chroma_client.get_or_create_collection(
        name="qa_collection",
    )
# Variable INITIALIZATION

if 'chatStarted' not in st.session_state:
    st.session_state.chatStarted = False
    st.session_state.chat_history = []
    st.session_state.all_chat_history = []
    st.session_state.refresh_required = False
    st.session_state.end_conversation = False


# Functions


def generate_response():
    
    messages = [
        {'role': 'system', 'content': """You are BRACU THESIS BOT, a helpful assistant from BRAC University CSE departments students. 
         At first, introduce yourself to the user. Never use emojis, unless explicitly asked to.
         You are pretrained with proper documents and resources, so be confident about your findings and reasoning. You response must be friendly, humble and polite.
        
         Whenever a user asks a question, you will be given some context by the system. You need to answer based on the given context. However, do not mention the word context in your response. If the user ask for out of context question, then warn the user by saying that your knowledge about this topic is not up to the date.
        
         Dont use system context if the user question does not require.
         Once done chatting, you can end the conversation by saying nice things and take care.
        If user does not co-operate or says inappropriate word, or the conversation is done, then you can forcefully end the conversation by responsing '<<END>>' with no preamble. 
         """},
        *st.session_state.chat_history
    ]
    try:
        response = client.chat.completions.create(
            model = "llama-3.3-70b-specdec",
            messages = messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e} \n \n Looks like the GROQ API Server is down. Please try again after a while."


# Page Decoration 
st.set_page_config(
    page_title = "BRACU Thesis ChatBot",
    page_icon = "📚",
    layout = "centered"
)

# st.image("C:/Users/Niloy/Desktop/Chatbot with RAG/bracu_logo.png")
st.title("📚 BRACU Thesis ChatBot")

# Start Screen
if not st.session_state.chatStarted:
    st.html("""<h1>Welcome to BRACU Thesis Chatbot!</h1>
    <p>Here are the things you can do:</p>
    <ol>
            <li><strong>Want to know about what is thesis?</li>

    </ol>""")

if not st.session_state.end_conversation:
    user_prompt = st.chat_input("Ask me!")
    if user_prompt:
        st.session_state.chatStarted = True
        st.session_state.turn = "agent"
        st.session_state.all_chat_history.append({'role': 'user', 'content': user_prompt})
        st.session_state.chat_history.append({'role': 'user', 'content': user_prompt})
        query = user_prompt
        result = collection.query(query_texts=[query], n_results=3)
        context = "CONTEXT: \n"
        for c in result['documents'][0]:
            context += c + '\n'
        st.session_state.chat_history.append({'role': 'system', 'content': context})
        # st.chat_message("user").markdown(user_prompt)   
    
#Chat Screen

def updateChat():
    for message in st.session_state.all_chat_history:
        if message['role'] != 'system':
            with st.chat_message(message['role']):
                st.markdown(message["content"])

if st.session_state.chatStarted:
    if  st.session_state.turn == "agent":
        assistant_response = generate_response()
        st.session_state.chat_history.append({"role":"assistant", "content": assistant_response})
        if "<<END>>" not in assistant_response:
            st.session_state.all_chat_history.append({"role":"assistant", "content": assistant_response})
        # with st.chat_message("assistant"):
        #     st.markdown(remove_commands(assistant_response))
        if "<<END>>" in st.session_state.chat_history[-1]['content']:
            st.session_state.end_conversation = True
            st.rerun()
        else:
            st.session_state.turn = "user"
    updateChat()

if st.session_state.refresh_required:
    st.session_state.refresh_required = False
    st.rerun()

if st.session_state.end_conversation:
    with st.chat_message("System"):
        st.markdown("The conversation was ended. To start a new conversation, please reload the page.")