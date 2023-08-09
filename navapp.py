import nlp2sql023
import askcsv01
import streamlit as st

PAGES = {
    "NLP 2 SQL": nlp2sql023,
    "Ask CSV": askcsv01
}
st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page.app()