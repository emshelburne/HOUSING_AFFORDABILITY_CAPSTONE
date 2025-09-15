import os
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

import streamlit as st
st.set_page_config(page_title="Boot OK", layout="centered")
st.write(" Minimal app booted")

