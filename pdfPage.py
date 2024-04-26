import streamlit as st
from st_pages import Page, Section, show_pages, add_page_title
import config_setting.model_config as model_config
from config_setting import model_config, func_modules,prompt_config
from langchain_core.messages import AIMessage, HumanMessage


########################################
#初始化参数
########################################
#初始化消息
# init_message = "您好，我是AI聊天机器人，我会尽力回答您的问题。\
#                 此外在我的左侧栏中，您可以更换不同的AI模型。"
init_pdf_message = "功能开发ing..."

#初始化模型聊天记录
if "pdf_history" not in st.session_state:
    st.session_state.pdf_history = [
        AIMessage(content=init_pdf_message),
    ]
########################################
#前端页面设计与功能开发
########################################

#页面title
st.set_page_config(page_title="AIBot", page_icon="🤖")
add_page_title()

#左侧栏
with st.sidebar:
    #模型选择
    model_option = st.selectbox(
        "选择机器人模型:",
        options=list(model_config.models.keys()),
        format_func=lambda x: model_config.models[x]["name"],
        index=0  # Default to mixtral
    )
    #清除聊天记录
    def clear_pdf_history():
        st.session_state.pop("messages", None)
        st.session_state.pdf_history = [
            AIMessage(content=init_pdf_message),
        ]
    st.button("Clear Chat History", on_click=lambda: clear_pdf_history())

# #页面标题
# st.header("Chat-AI机器人", divider="rainbow", anchor=False)


#网页聊天记录
for message in st.session_state.pdf_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)