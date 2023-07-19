import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
import openai
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import text

def main():

    load_dotenv()

    #openai.api_key = os.getenv("OPENAI_API_KEY")
    st.set_page_config(page_title = "Ask questions to your data")
    st.header("Ask questions to your data")

    with st.expander("About the app"):
        st.write("This is an app through which you can ask questions to your data in natural language.")
        st.write("Please do not load any confidential or company data.")
        st.write("Please make sure that the column names or headers in csv has no spaces or special characters.")

    input_api_key = st.text_input("Enter your OpenAI key here", type="password")
    st.markdown(
                '<p style="text-align:center">Get your Open AI API key <a href="https://platform.openai.com/account/api-keys">here</a></p>',
                unsafe_allow_html = True
            )
    openai.api_key = input_api_key

    
    user_csv = st.sidebar.file_uploader("Upload a CSV file", type = "csv" )
    if user_csv is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_file.write(user_csv.getvalue())
            temp_file_path = temp_file.name

            df = pd.read_csv(temp_file_path)
            st.write(df.head(5))

            temp_db = create_engine("sqlite:///:memory:", echo=True)
            data = df.to_sql(name = "dataTable", con = temp_db)

            with temp_db.connect() as conn:
                result = conn.execute(text("select * from dataTable limit 5"))
                #st.write(result.all())

    nlp_text = prompt_input()

    if nlp_text is not None and nlp_text != "":
        with st.spinner(text = "Analysis in progress..."):
            
        

            prompt = combine_prompts(df, nlp_text)
            #st.write(prompt) 

            response = openai.Completion.create(
                model = "text-davinci-003",
                prompt = prompt,
                temperature = 0,
                max_tokens = 150,
                top_p = 1.0,
                frequency_penalty = 0,
                presence_penalty = 0,
                stop = ['#',';']

            )

            #handle_response(response)
            #st.write(response)

            with temp_db.connect() as conn:
                result = conn.execute(text(handle_response(response)))

                st.write(result.all())

       




def handle_response(response):
    query = response['choices'][0]['text']
    if query.startswith(" "):
        query = "SELECT " + query

    return query



def create_table_definition(df):
    prompt = """ sqlite SQL table, with its properties:
    #
    # dataTable({})
    #
    """.format(",".join( str(col) for col in df.columns  ))

    return prompt

def prompt_input():
    user_question = st.text_input("Enter your query here: ")

    return user_question

def combine_prompts(df, query_prompt):
    definition = create_table_definition(df)
    query_init_string = f"### A query to answer: {query_prompt}\nSELECT"

    return definition + query_init_string


if __name__ == '__main__':
    main()