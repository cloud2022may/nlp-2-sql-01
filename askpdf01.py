from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import openai
from langchain.callbacks import get_openai_callback
from streamlit_chat import message

def app():
    load_dotenv()

    #st.set_page_config(page_title="Ask questions to your PDF")

    st.header("Ask questions to your PDF")

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
        st.write("Ask questions to your PDF file in natural language")
        #st.write("Please do not load any confidential or company data.")
        #st.write("Please make sure that the column names or headers in csv has no spaces or special characters.")

    with st.expander("OpenAI key"):
        input_api_key = st.text_input("Enter your OpenAI key here", type="password")
        st.markdown(
                    '<p style="text-align:center">Get your Open AI API key <a href="https://platform.openai.com/account/api-keys">here</a></p>',
                    unsafe_allow_html = True
                )
        openai.api_key = input_api_key

    # upload file
    pdf = st.sidebar.file_uploader("Upload your PDF", type="pdf")

    # extract the text from pdf
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # split into chunks
        text_splitter = CharacterTextSplitter(
            separator = "\n",
            chunk_size = 1000,
            chunk_overlap = 200,
            length_function = len
        )

        chunks = text_splitter.split_text(text)

        # create embeddings
        embeddings = OpenAIEmbeddings(openai_api_key = input_api_key)
        knowledge_base = FAISS.from_texts(chunks, embeddings)

        with container:

            with st.form(key="input_form", clear_on_submit=True):

                user_question = st.text_input("Ask a question about your pdf:", placeholder="Query your csv data here", key="input")
                submit_button = st.form_submit_button(label="Send")

            if user_question:
                docs = knowledge_base.similarity_search(user_question)

                llm = OpenAI(openai_api_key = input_api_key)

                chain = load_qa_chain(llm,chain_type="stuff")

                with get_openai_callback() as cb:
                    response = chain.run(input_documents = docs, question = user_question)
                    print(cb)

                st.write(response)

                st.session_state['past'].append(user_question)
                st.session_state['generated'].append(response)

        
        if st.session_state['generated']:
            with response_container:
                for i in range(len(st.session_state['generated'])):
                    message(st.session_state["past"][i], is_user=True, key= str(i) + '_user', avatar_style="big-smile")
                    message(st.session_state["generated"][i], key=str(i)  ) #, avatar_style="robot"  )


        


