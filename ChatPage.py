import streamlit as st
import ChatBot_framework
from langchain.memory import ChatMessageHistory
from st_pages import Page, Section, show_pages, add_page_title
import config_setting.model_config as model_config


#页面标题
st.set_page_config(page_title="大模型AI平台", page_icon="📈")
# add_page_title()

#页面导航
show_pages(
    [    
        Section(name='AI功能'),
        Page("ChatPage.py", "聊天机器人ChatBot", "🤖"),
        # Page(None, "知识图谱机器人KnowledgeGraphBot(未开放)", "🤖"),
        # Page("pdfPage.py", "pdf解析机器人PDFParseBot(未开放)", "🤖"),
        Page("URLPage.py", "通用URL解析机器人URLParseBot", "🤖"),
        # Page("SummaryPage.py", "总结机器人SummaryBot(未开放)", "🤖"),
        # Page("aboutPage.py", "关于About", "🤖"),
    ]
)

with st.sidebar:
    #模型选择
    model_option = st.selectbox(
    "选择机器人模型:",
    options=list(model_config.models.keys()),
    format_func=lambda x: model_config.models[x]["name"],
    index=0  # Default to mixtral
    )
    #清除聊天记录
    def clear_chat_history():
        st.session_state.pop("messages", None)
        st.session_state.chat_history = ChatMessageHistory()
    st.button("Clear Chat History", on_click=lambda: clear_chat_history())
    st.text("Gemma更适合中文语境")
    # st.text("LLaMA2-70b性能均衡")
    st.text("LLaMA3-70b精准度高")
    st.text("LLaMA3-8b速度快")
    st.text("Mixtral速度快，适合长文本")


#主页面标题
st.header("ChatBot-AI机器人", divider="rainbow", anchor=False)
#初始化模型选择
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None
#初始化页面聊天记录
if "messages" not in st.session_state:
    st.session_state["messages"] = list()
#初始化模型聊天记录
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatMessageHistory()

#初始化对话过程
st.chat_message("assistant").write("您好，我是基于AI大模型的对话机器人，\
                                   我会尽可能地回答您的问题。此外，在我的左侧栏中，您可以选择不同的AI功能，也能指定您需要的AI模型。")

#显示对话过程
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

#初始模型
bot=ChatBot_framework.Bot(model_option)

#输入问题
question = st.chat_input()
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)
    response = bot.chat(question,st.session_state.chat_history)
    st.session_state.chat_history.add_user_message(question)
    st.session_state.chat_history.add_ai_message(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)

    


  