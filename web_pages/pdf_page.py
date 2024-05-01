import streamlit as st
def pdf_page():
    st.toast(
            f"欢迎使用 [`Langchain-Chatchat`](https://github.com/chatchat-space/Langchain-Chatchat) ! \n\n"
            f"当前运行的模型, 您可以开始提问了."
        )
    st.write("PDF解析机器人")