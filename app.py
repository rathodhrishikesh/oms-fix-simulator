import streamlit as st
from oms_simulation import oms_ui

# Top layout: Creator info on right
col1, col2 = st.columns([6, 4])
with col1:
    pass  # Empty space for title alignment
with col2:
    st.markdown("""
    <div style='text-align: right; font-size: 14px;'>
        <b>Created by:</b> Hrishikesh Rathod<br>
        <b>Portfolio:</b> <a href="https://hr-msba-portfolio.netlify.app/" target="_blank">hr-msba-portfolio.netlify.app</a>
    </div>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="Neovest OMS & FIX Protocol Simulator", layout="wide")

st.title("📊 Neovest - OMS & FIX Protocol Simulator")

oms_ui()
