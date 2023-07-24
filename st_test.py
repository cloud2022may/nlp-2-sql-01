import streamlit as st
from streamlit_chat import message

import numpy as np

with message("assistant"):
    st.write("Hello 👋")
    st.line_chart(np.random.randn(30, 3))

