import random
import time
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_community.chat_models import QianfanChatEndpoint
from config_setting import model_config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PDFMinerLoader
from dotenv import find_dotenv, load_dotenv
import tempfile
import os
from config_setting import prompt_config
class pdfbot:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.model_option = None
        self.model_tokens = None
        self.llm = None

    def judge_type_prompt(self,pdf_type):
        if pdf_type=='简历分析':
            prompt=prompt_config.resume_prompt
        # elif pdf_type=='学术论文解析':
        #     prompt=prompt_config.academic_prompt
        # else:
        #     prompt=prompt_config.general_prompt
        return prompt
    
    def get_response(self,question,pdf_type,pdf_content,chat_history):
        try:
            if self.model_option =='ERNIE-Lite-8K' or self.model_option=='ERNIE-speed-128k':
                self.llm = QianfanChatEndpoint(model=self.model_option)
            else:
                self.llm = ChatGroq(model_name=self.model_option,temperature=0.1,max_tokens=self.model_tokens)
            prompt_selected=self.judge_type_prompt(pdf_type)
            prompt = ChatPromptTemplate.from_template(prompt_selected)
            chain = prompt | self.llm | StrOutputParser()
            return chain.stream({
                "chat_history": chat_history,
                "question": question,
                "resume_content": pdf_content
            })
        except Exception as e:
            return f"当前模型{self.model_option}暂不可用，请在左侧栏选择其他模型。"

def init_params():
    if "pdf_message" not in st.session_state:
        st.session_state.pdf_message = []
    if "pdf" not in st.session_state:
        st.session_state.pdf= None
    if "pdf_bot" not in st.session_state:
        st.session_state.pdf_bot = pdfbot()
    if "pdf_content" not in st.session_state:
        st.session_state.pdf_content = None
    if "resume_summary" not in st.session_state:
        st.session_state.resume_summary = None


def clear():
    st.session_state.pdf_message = []
    st.session_state.pdf_bot = pdfbot()
    st.session_state.pdf= None
    st.session_state.pdf_content = None
    st.session_state.resume_summary=None
    

def summary_resume(pdf_content,model_option,model_tokes):
    try:
        if model_option =='ERNIE-Lite-8K':
            llm = QianfanChatEndpoint(model=model_option,temperature=0.7)
        else:
            llm = ChatGroq(model_name=model_option,temperature=1,max_tokens=model_option)
        prompt_selected=prompt_config.resume_summary_prompt
        prompt = ChatPromptTemplate.from_template(prompt_selected)
        chain = prompt | llm | StrOutputParser()
        return chain.stream({
            "resume_content": pdf_content,
        })
    except Exception as e:
        return f"当前模型{model_option}暂不可用，请在左侧栏选择其他模型。"
    

def pdf_page():
    init_params()
    '''页面布局'''
    with st.sidebar:
        with st.container(border=True):
            select_model=st.selectbox("选择模型",options=["百度千帆大模型-8k","百度千帆大模型-128k","谷歌Gemma大模型","Llama3-70b大模型","Llama3-8b大模型","Mixtral大模型"],index=0)#模型选择
            model_option=model_config.model_ls[select_model]["name"]
            model_tokes=model_config.model_ls[select_model]["tokens"]
            st.button(label="清除聊天记录", on_click=lambda: clear(),use_container_width=True)
    st.title("🗎pdf解析-AI机器人")
    st.subheader(body='',divider="rainbow")

    '''初始化消息'''
    #初始化消息
    with st.chat_message("AI"):
        st.markdown("您好，我是基于PDF解析的AI聊天机器人,请你先上传你的PDF文件，然后输入你的问题，我会尽力回答你的问题")
    

    '''PDF上传'''
    with st.container(border=True):
        st.session_state.pdf = st.file_uploader('请上传你的PDF', type="pdf")
        pdf_type=st.selectbox("选择PDF解析功能",options=['简历分析'],index=0)
        upload_btn= st.button('上传文档')



    if upload_btn:#上传PDF文件
        st.session_state.pdf_message=[] #初始化pdf内容
        if st.session_state.pdf is not None:
            '''PDF解析'''
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(st.session_state.pdf.read())
            loader = PDFMinerLoader(tmp_file.name)
            st.session_state.pdf_content = loader.load_and_split()
            os.remove(tmp_file.name)
            '''先整体回答PDF问题'''
            st.session_state.pdf_bot.model_option = model_option
            st.session_state.pdf_bot.model_tokens = model_tokes
            if pdf_type=='简历分析':
                with st.chat_message("AI"):
                    st.session_state.resume_summary = st.write_stream(summary_resume(st.session_state.pdf_content,model_option,model_tokes))#简历分析
                    st.session_state.pdf_message.append(AIMessage(content=st.session_state.resume_summary))
        else:
            st.warning("请先上传P正确的PDF文件")

    '''滚动更新聊天记录'''
    for message in st.session_state.pdf_message:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)

    '''用户问题交互'''
    question = st.chat_input("输入你的问题")
    if question and st.session_state.pdf_content is not None:
        st.session_state.pdf_bot.model_option = model_option
        st.session_state.pdf_bot.model_tokens = model_tokes
        with st.chat_message("Human"):
            st.markdown(question)
            st.session_state.pdf_message.append(HumanMessage(content=question))
        with st.chat_message("AI"):
            response = st.write_stream(st.session_state.pdf_bot.get_response(question,pdf_type,st.session_state.pdf_content,st.session_state.pdf_message))
            st.session_state.pdf_message.append(AIMessage(content=response))
        
   

    

   





    




