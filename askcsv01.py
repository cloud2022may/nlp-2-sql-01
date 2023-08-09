import streamlit as st
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
from dotenv import load_dotenv
import openai
import tempfile
from streamlit_chat import message
from langchain.chains import ConversationalRetrievalChain

def app():
    #st.set_page_config(page_title="Ask Questions to your CSV")

    load_dotenv()

    #st.set_page_config(page_title="Ask Questions to your CSV")
    st.header("Ask questions to your CSV file")

    # session state
    if 'history' not in st.session_state:
        st.session_state['history'] = []

    if 'generated' not in st.session_state:
        st.session_state['generated'] = [ "Hello! Ask me anything about the file "] # + uploaded_file.name + " 🤗"]
    
    if 'past' not in st.session_state:
        st.session_state['past'] = ["Hey ! How are you today 👋"]

    # container for chat history
    response_container = st.container()    
    # container for the user's text input
    container = st.container()

    with st.expander("About the app"):
        st.write("Ask questions to your CSV data in natural language")
        #st.write("Please do not load any confidential or company data.")
        #st.write("Please make sure that the column names or headers in csv has no spaces or special characters.")

    with st.expander("OpenAI key"):
        input_api_key = st.text_input("Enter your OpenAI key here", type="password")
        st.markdown(
                    '<p style="text-align:center">Get your Open AI API key <a href="https://platform.openai.com/account/api-keys">here</a></p>',
                    unsafe_allow_html = True
                )
        openai.api_key = input_api_key

    user_csv = st.sidebar.file_uploader("Upload your CSV file", type = "csv")



    if user_csv is not None:

        # use tempfile
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(user_csv.getvalue())
            tmp_file_path = tmp_file.name

        user_question = st.text_input("Ask a question about your CSV data")

        llm = OpenAI(temperature=0 ,   openai_api_key = input_api_key ) #openai_api_key=openai.api_key)
        #st.write(openai.api_key)
        #agent = create_csv_agent(llm, user_csv, verbose=True)
        agent = create_csv_agent(llm, tmp_file_path, verbose=True)

        if user_question is not None and user_question != "":
            response = agent.run(user_question)

            st.write(response)

            st.session_state['past'].append(user_question)
            st.session_state['generated'].append(response)

        
        if st.session_state['generated']:
            with response_container:
                for i in range(len(st.session_state['generated'])):
                    message(st.session_state["past"][i], is_user=True, key= str(i) + '_user', avatar_style="big-smile")
                    message(st.session_state["generated"][i], key=str(i)  ) #, avatar_style="robot"  )