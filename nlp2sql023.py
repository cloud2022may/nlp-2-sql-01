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
import time

st.set_page_config(page_title = "Ask questions to your data")

def app():
    

    

#def main():
    
    load_dotenv()

    # initialize session state
    if "load_state" not in st.session_state:
        st.session_state.load_state = False


    #openai.api_key = os.getenv("OPENAI_API_KEY")
    #st.set_page_config(page_title = "Ask questions to your data")
    st.header("Generative SQL")
    st.header("Ask questions to your data")

    with st.expander("About the app"):
        st.write("Ask questions to your data in natural language")
        #st.write("Please do not load any confidential or company data.")
        #st.write("Please make sure that the column names or headers in csv has no spaces or special characters.")

    with st.expander("OpenAI key"):
        input_api_key = st.text_input("Enter your OpenAI key here", type="password")
        st.markdown(
                    '<p style="text-align:center">Get your Open AI API key <a href="https://platform.openai.com/account/api-keys">here</a></p>',
                    unsafe_allow_html = True
                )
        openai.api_key = input_api_key

    #### sidebar
    st.sidebar.header("Select your parameters: ")

    model_name_option = st.sidebar.selectbox(
        'Model',
        ('text-davinci-003', 'text-davinci-002' )) #, 'davinci', 'curie', 'babbage', 'ada') )

    temperature_slider = st.sidebar.slider('Temperature', 0.0, 1.0, 0.0)    

    max_tokens_slider = st.sidebar.slider('Maximum no of tokens', 0, 300, 150)
    
    #st.write("Sample Sales Data")
    
    #temp_file_path = "./nlp-2-sql-01/sales_data_sample.csv"
    temp_file_path = "./sales_data_sample.csv"

    df = pd.read_csv(temp_file_path)
    #st.write(df.head(5))
    
    with st.expander("Sample Sales Data"):
        st.write(df)

    
    with st.expander("Ask anything or try an example"):
        
        st.write("what are the total sales of each product in usa") 
        st.write("Can you give the total sales by territory") 
        st.write("what was the total sales in the second month of year 2004")
        st.write("what was the total sales of motor cycles alone in the 4th month of year 2005")
        st.write("which country shipped maximum number of ships in 2005")
        st.write("which city in the USA shipped the least number of motorcycles in 2004")


    # container for the user's text input
    container = st.container()

    with container:
        nlp_text = prompt_input()
    
    # connection to database
    db = pymysql.connect(host='database-1.cdatmsjowfie.us-east-1.rds.amazonaws.com',
                        user='mysqluser',
                        password='mysqluser',
                        database="db01")
    cursor = db.cursor()

    # container for chat history
    response_container = st.container()

    with response_container:

        if nlp_text is not None and nlp_text != "":
            with st.spinner(text = "Analysis in progress..."):
                
            

                prompt = combine_prompts(df, nlp_text)
                #st.write(prompt) 

                response = openai.Completion.create(
                    model = model_name_option, #"text-davinci-003",
                    prompt = prompt,
                    temperature = temperature_slider ,#0,
                    max_tokens = max_tokens_slider, #150,
                    top_p = 1.0,
                    frequency_penalty = 0,
                    presence_penalty = 0,
                    #stop = ['#',';']
                    stop = ['#']

                )

                #handle_response(response)
                #st.write(response)

                #try:
                #st.write(text(handle_response(response)))
                response_query = handle_response(response)
                response_query = response_query.replace("dataTable", "sales" )
                #response_query = response_query.replace("SELECT", "\n; SELECT" )
                #response_query = response_query[ 2: ]
                st.write(response_query)

                st.write("Results ")

                
                query = handle_response(response)

                response_query_checked = checkforSQLInjection(response_query)

                ##### logging 
                with open("log.txt","a") as file:

                    file.write(f"\n########\nuser input: {nlp_text} \n" )
                    file.write(f"generated query: {response_query} \n" )
                    file.write(f"response_query_checked: {response_query_checked} \n")
                if response_query_checked != "stop":

                    cursor.execute(response_query_checked)
                    query_result = cursor.fetchall()
                    #query_result = dict(zip(cursor.column_names, cursor.fetchall()))

                    # Fetch the column names from the cursor.description
                    columns = [col[0] for col in cursor.description]
                    #st.write(columns)

                    df_query_result = pd.DataFrame(query_result)
                    df_query_result.columns = columns

                    #st.write(result.all())

                    st.write(df_query_result)

                    #interactive_plot(df_query_result)
                    
                    #if ( len(df_query_result.columns.values.tolist()) >= 2 ):
                            #columns = ["column0", "column1"]
                            #df_query_result.columns = columns
                            
                            #st.bar_chart(df_query_result , y = df_query_result.columns.values[1], x=df_query_result.columns.values[0])

                    #opt = st.radio('Plot type:', ['Bar', 'Pie'])
                    #if opt == 'Bar':
                    #    fig = px.bar(df_query_result, x = df_query_result.columns.values[0], y = df_query_result.columns.values[1] , title="Bar Chart")
                    #    st.plotly_chart(fig)
                    #else:
                    #    fig = px.pie(df_query_result, names = df_query_result.columns.values[0], values = df_query_result.columns.values[1] , title="Pie Chart")
                    #    st.plotly_chart(fig)

                    # check for column count
                    if ( len(df_query_result.columns.values.tolist()) >= 2 ):

                        tab1, tab2, tab3 = st.tabs(["📈 Bar Chart", "📈 Pie Chart", "🗃 Data"])

                        tab1.fig = px.bar(df_query_result, x = df_query_result.columns.values[0], y = df_query_result.columns.values[1] , title="Bar Chart")
                        tab1.plotly_chart(tab1.fig)

                        tab2.fig = px.pie(df_query_result, names = df_query_result.columns.values[0], values = df_query_result.columns.values[1] , title="Pie Chart")
                        tab2.plotly_chart(tab2.fig)

                        tab3.dataframe(df_query_result)

                #getExp = st.button('Fetch Explanation', on_click=getExplanationButtonCallback) 

    #st.write(df_query_result.columns[1])
    #st.write(df_query_result.sort_values(by=[df_query_result.columns[1]], ascending=False))
    
    #if nlp_text is not None and nlp_text != "":
    getExp = st.button('Fetch Explanation', on_click=getExplanationButtonCallback) 


    if getExp or st.session_state.load_state:

        st.session_state.load_state = True

        with st.spinner(text = "Analysis in progress..."):
        
            ##### describe data in text
            describe_prompt = create_describe_prompt(df_query_result)
            
            prompt = combine_prompts(df, nlp_text)
            #st.write(prompt) 
            time.sleep(10)

            des_response = openai.Completion.create(
                model = model_name_option, #"text-davinci-003",
                prompt = describe_prompt,
                temperature = temperature_slider ,#0,
                max_tokens = max_tokens_slider, #150,
                top_p = 1.0,
                frequency_penalty = 0,
                presence_penalty = 0,
                #stop = ['#',';']
                stop = ['#']

            )

            handle_response(response)
            st.write(des_response['choices'][0]['text'])




    


#    if __name__ == '__main__':
#        main()

def interactive_plot(df):
        #x_axis_val = st.selectbox('Select X-Axis Value', options= df.columns)
        #y_axis_val = st.selectbox('Select Y-Axis Value', options= df.columns)

        #plot = px.bar(df, x = x_axis_val, y = y_axis_val, orientation='v')
        plot = px.bar(df, x = df.columns.values[0], y = df.columns.values[1], orientation='v')
        st.plotly_chart(plot)                        
                
def checkforSQLInjection(response_query):
    # check list
    check_list = ["insert", "delete", "truncate", "update", "password", "EXEC", "sp_executesql", "sp_execute","sp", 'grant', 'revoke',"1==1", "1=1","OR 1==1","OR '1'='1'", "OR 1=1","hacking", "script", "network"]

    # using list comprehension
    # checking if string contains list element
    #res = any(ele.lower() in response_query for ele in check_list)

    if any(ele.lower() in response_query.lower() for ele in check_list):
        st.error("Please check your query as it seems to contain some invalid tokens")
        return "stop"
    else:
        #print("String does not contains the list element")
        return response_query
    
    

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
    prompt = """ mssql SQL table, with its properties:
    #
    # dataTable({})
    #
    """.format(",".join( str(col) for col in df.columns  ))

    return prompt

def prompt_input():
    user_question = st.text_input("Enter your query here: ", max_chars=120)

    return user_question

def combine_prompts(df, query_prompt):
    definition = create_table_definition(df)
    query_init_string = f"### A query to answer: {query_prompt}\nSELECT"

    return definition + query_init_string

def create_describe_prompt(df):
    #df_sorted = df.sort_values(by=[df.columns[1]], ascending=False)
    prompt = """ 
    #
    # data: {}
    #
    # can you describe the above data in a textual form, higher the sales higher the value and then state any assumptions and write a explanation or analysis about the data, higher the number higher the value
    """.format(df)

    return prompt

def getExplanationButtonCallback():
        st.write("Button clicked")