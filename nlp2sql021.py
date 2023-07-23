import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
import openai
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import text
import plotly_express as px
from pandasql import sqldf
import pymysql
#from mysql import connector


def main():

    load_dotenv()

    #openai.api_key = os.getenv("OPENAI_API_KEY")
    st.set_page_config(page_title = "Ask questions to your data")
    st.header("Generative SQL")
    st.header("Ask questions to your data")

    with st.expander("About the app"):
        st.write("This is an app through which you can ask questions to your data in natural language.")
        #st.write("Please do not load any confidential or company data.")
        #st.write("Please make sure that the column names or headers in csv has no spaces or special characters.")

    input_api_key = st.text_input("Enter your OpenAI key here", type="password")
    st.markdown(
                '<p style="text-align:center">Get your Open AI API key <a href="https://platform.openai.com/account/api-keys">here</a></p>',
                unsafe_allow_html = True
            )
    openai.api_key = input_api_key

    st.write("Sample Sales Data")
    
    #temp_file_path = "./nlp-2-sql-01/sales_data_sample.csv"
    temp_file_path = "./sales_data_sample.csv"

    df = pd.read_csv(temp_file_path)
    #st.write(df.head(5))
    st.write(df)

    temp_db = create_engine("sqlite:///:memory:", echo=True)
    #my_conn = create_engine("mysql+mysqldb://usrid:password@localhost/my_db")
    data = df.to_sql(name = "sales", con = temp_db)

       

    #with temp_db.connect() as conn:
        #result = conn.execute(text("select * from dataTable limit 5"))
        #st.write(result.all())
    with st.expander("Some sample queries"):
        st.write("what are the total sales of each product in usa") 
        st.write("Can you give the total sales by territory") 
        st.write("what was the total sales in the second month of year 2004")
        st.write("what was the total sales of motor cycles alone in the 4th month of year 2005")
        st.write("which country shipped maximum number of ships in 2005")
        st.write("which city in the USA shipped the least number of motorcycles in 2004")

    nlp_text = prompt_input()
    
    # connection to database
    db = pymysql.connect(host='database-1.cdatmsjowfie.us-east-1.rds.amazonaws.com',
                         user='admin',
                         password='awsmysql02',
                         database="db01")
    cursor = db.cursor()

    # connect to mysql
    #mysql_conn = connector.connect(
    #  host="database-1.cdatmsjowfie.us-east-1.rds.amazonaws.com",
    #  user="admin",
    #  passwd="awsmysql02",
    #  database="db01"
    #)

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

            #try:
            st.write(text(handle_response(response)))
            response_query = handle_response(response)
            response_query = response_query.replace("dataTable", "sales" )

            #pd_results = sqldf(response_query)
            #pd_results = sqldf("SELECT SUM(SALES) AS 2004_SALES FROM dataTable WHERE PRODUCTLINE = 'Motorcycles' AND YEAR_ID = 2004")
            #pd_results = sqldf("SELECT SUM(SALES) FROM df WHERE PRODUCTLINE = 'Motorcycles' AND YEAR_ID = 2004 UNION SELECT SUM(SALES)  FROM df WHERE PRODUCTLINE = 'Motorcycles' AND YEAR_ID = 2005")
            #st.write("Results from pandas query")
            #st.write(pd_results)

            st.write("Results from OpenAI query")

            
            query = handle_response(response)

            #query_result = pd.read_sql(query,mysql_conn)


            cursor.execute(query)
            query_result = cursor.fetchall()
            #query_result = dict(zip(cursor.column_names, cursor.fetchall()))

            df_query_result = pd.DataFrame(query_result)
            #st.write(result.all())
            st.write(df_query_result)

            #st.write(df_query_result.columns.values[0])
            #st.write(df_query_result.columns.values[1])
            
            #st.write(df_query_result.columns.values)
            
            

            if (len(df_query_result.columns.values.tolist()) >= 2 ):
                    columns = ["column0", "column1"]
                    df_query_result.columns = columns
                    #st.bar_chart(df_query_result , y = "column1", x="column0")
                    st.bar_chart(df_query_result , y = df_query_result.columns.values[1], x=df_query_result.columns.values[0])
                    #st.bar_chart(df_query_result , y = df_query_result[df_query_result.columns[1]], x=df_query_result[df_query_result.columns[0]])
                    #st.bar_chart(df_query_result , y = df_query_result[1], x=df_query_result[0])

            

       

def interactive_plot(df):
    x_axis_val = st.selectbox('Select X-Axis Value', options= df.columns)
    y_axis_val = st.selectbox('Select Y-Axis Value', options= df.columns)

    plot = px.scatter(df, x = x_axis_val, y = y_axis_val)
    st.plotly_chart(plot)


def handle_response(response):
    query = response['choices'][0]['text']
    if query.startswith(" "):
        query = "SELECT " + query

    return query



def create_table_definition(df):
    prompt = """ sqlite SQL table, with its properties:
    #
    # sales({})
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