import streamlit as st
from st_pages import Page, Section, show_pages, add_page_title
import config_setting.model_config as model_config
from config_setting import model_config, func_modules,prompt_config
from langchain_core.messages import AIMessage, HumanMessage


########################################
#机器人模型
########################################
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
def get_response(model_option,question, chat_history):
    try:
        llm = ChatGroq(model_name=model_option)
        prompt = ChatPromptTemplate.from_template(prompt_config.chatBot_template_prompt_zh)
        chain = prompt | llm | StrOutputParser()
        return chain.stream({
            "chat_history": chat_history,
            "question": question,
        })
    # return chain.invoke({
    #     "chat_history": chat_history,
    #     "question": question,
    # })
    except Exception as e:
        return f"当前模型{model_option}暂不可用，请在左侧栏选择其他模型。"


########################################
#初始化参数
########################################
#初始化消息
init_chat_message = "您好，我是AI聊天机器人，我会尽力回答您的问题。\
                此外在我的左侧栏中，您可以更换不同的AI模型。"

#初始化模型聊天记录
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content=init_chat_message),
    ]

########################################
#前端页面设计与功能开发
########################################

#页面title
set_page_config=st.set_page_config(
        page_title="AIBot", 
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="auto",  #侧边栏是否固定,"auto", "expanded", or "collapsed"
        # menu_items={
        #     'Get Help': 'https://www.extremelycoolapp.com/help',
        #     'Report a bug': "https://www.extremelycoolapp.com/bug",
        #     'About': "# This is a header. This is an *extremely* cool app!"
        # }

)

#页面导航
add_page_title() #有这个show_pages才能生效
show_pages(
    [    
        # Section(name='AI功能',icon='🤖'),
        Page("chat_page.py", "AI-聊天机器人"),
        Page("url_page.py", "URL检索机器人"),
        Page("pdf_page.py", "AI-PDF解析机器人"),
        # Page("summary_page.py", "摘要-AI分析机器人"),
        # Page("AboutPage.py", "关于About")
    ]
)
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
    def clear_chat_history():
        st.session_state.chat_history = [
            AIMessage(content=init_chat_message),
        ]
    st.button("Clear Chat History", on_click=lambda: clear_chat_history())

# #页面标题
# st.header("Chat-AI机器人", divider="rainbow", anchor=False)


#网页聊天记录
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)


#输入问题
question = st.chat_input("输入你的问题")
if question:
    st.session_state.chat_history.append(HumanMessage(content=question))

    with st.chat_message("Human"):
        st.markdown(question)

    with st.chat_message("AI"):
        
        response = st.write_stream(get_response(model_option,question, st.session_state.chat_history))
        
        # response = get_response(model_option,question, st.session_state.chat_history)
        # st.write(response)

    st.session_state.chat_history.append(AIMessage(content=response))