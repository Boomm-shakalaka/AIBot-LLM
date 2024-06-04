import random
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_community.chat_models import QianfanChatEndpoint
from config_setting import model_config,prompt_config
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import find_dotenv, load_dotenv

class chatbot:
    def __init__(self):
        load_dotenv(find_dotenv())#加载环境变量
        self.model_option = None
        self.model_tokens = None
        self.llm = None

    def get_response(self,question,chat_history):
        try:
            if self.model_option =='ERNIE-Lite-8K' or self.model_option=='ERNIE-speed-128k': #选择百度千帆大模型
                self.llm = QianfanChatEndpoint(model=self.model_option)
            elif self.model_option == 'gemini-1.5-flash-latest': #选择谷歌Gemma大模型,不支持流式输出暂未使用
                model_choice=random.choice(["gemini-1.5-flash-latest",'gemini-1.0-pro-001','gemini-1.5-pro-latest',"gemini-1.0-pro"])
                self.llm = ChatGoogleGenerativeAI(model=model_choice,temperature=0.7)#ChatGoogleGenerativeAI模型
            else:
                self.llm = ChatGroq(model_name=self.model_option,temperature=0.5,max_tokens=self.model_tokens)#ChatGroq模型
            prompt = ChatPromptTemplate.from_template(prompt_config.chatbot_prompt)
            chain = prompt | self.llm | StrOutputParser()
            # result=chain.invoke({"chat_history": chat_history,"question": question,}) #非流式输出
            # return result
            return chain.stream({
                "chat_history": chat_history,
                "question": question,
            })
        except Exception as e:
            return f"当前模型{self.model_option}暂不可用，请在左侧栏选择其他模型。"
        
def init_params():
    if "chat_message" not in st.session_state:
        st.session_state.chat_message = []
    if "chat_bot" not in st.session_state:
        st.session_state.chat_bot = chatbot()
        
#清除聊天记录
def clear():
    st.session_state.chat_message = [] #清除聊天记录
    st.session_state.chat_bot = chatbot() #重新初始化模型

    
def chat_page():
    init_params()#初始化模型和聊天记录
    '''页面布局'''    
    with st.sidebar:
        with st.container(border=True):
            select_model=st.selectbox("选择模型",options=["百度千帆大模型-8k","百度千帆大模型-128k","谷歌Gemma大模型","Llama3-70b大模型","Llama3-8b大模型","Mixtral大模型"],index=0)#模型选择
            model_option=model_config.model_ls[select_model]["name"]#模型名称
            model_tokes=model_config.model_ls[select_model]["tokens"]#模型tokens
            st.button(label="清除聊天记录", on_click=lambda: clear(),use_container_width=True) #清除聊天记录按钮
    st.title("💬 AI聊天机器人")
    st.subheader(body='',divider="rainbow")

    '''滚动更新聊天记录'''
    with st.chat_message("AI"):
        st.markdown("您好，我是AI聊天机器人，我会尽力回答您的问题。此外在我的左侧栏中，您可以更换不同的AI模型。")
    for message in st.session_state.chat_message:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)

    '''用户问题交互'''
    question = st.chat_input("输入你的问题")
    if question:
        st.session_state.chat_bot.model_option = model_option
        st.session_state.chat_bot.model_tokens = model_tokes
        with st.chat_message("Human"):
            st.markdown(question)
            st.session_state.chat_message.append(HumanMessage(content=question))#添加用户问题聊天记录
        with st.chat_message("AI"):
            response = st.write_stream(st.session_state.chat_bot.get_response(question,st.session_state.chat_message)) #流式输出，所以不用markdown
            st.session_state.chat_message.append(AIMessage(content=response))#添加用户问题聊天记录
