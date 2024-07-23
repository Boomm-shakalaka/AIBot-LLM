import random
import time
from langchain_openai import ChatOpenAI
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_community.chat_models import QianfanChatEndpoint
from config_setting import model_config
from langchain_community.document_loaders import PDFMinerLoader
from dotenv import find_dotenv, load_dotenv
import tempfile
import os
from config_setting import prompt_config
class pdfbot:
    def __init__(self):
        """
        初始化PDFBot类的实例，加载环境变量并设置模型选项和令牌数。
        """
        load_dotenv(find_dotenv())
        self.llm = None

    def judge_type_prompt(self,pdf_type):
        """
        根据PDF类型选择相应的提示模板。

        Parameters:
        pdf_type (str): PDF的类型。

        Returns:
        str: 选择的提示模板。
        """
        if pdf_type=='简历分析':
            prompt=prompt_config.resume_prompt
        # elif pdf_type=='学术论文解析':
        #     prompt=prompt_config.academic_prompt
        # else:
        #     prompt=prompt_config.general_prompt
        return prompt

    def init_llm_model(self,select_platform,select_model,select_temperature):
        """
        初始化模型。

        Parameters:
        select_platform (str): 选择的模型平台。
        select_model (str): 选择的模型。
        select_temperature (float): 温度系数。
        """
        self.model_option = select_model
        self.model_tokens = model_config.model_description_ls[select_model]["tokens"]
        if select_platform=='百度云平台':
            self.llm = QianfanChatEndpoint(model=select_model,temperature=select_temperature)
        elif select_platform=='Groq平台':
            self.llm = ChatGroq(model_name=select_model,max_tokens=self.model_tokens,temperature=select_temperature)
        elif select_platform=='Siliconflow平台':
            self.llm = ChatOpenAI(model_name=select_model,base_url="https://api.siliconflow.cn/v1",temperature=select_temperature)
    
    def get_response(self,question,pdf_type,pdf_content,chat_history):
        """
        根据用户的问题、PDF类型、PDF内容和对话历史获取响应。

        Parameters:
        question (str): 用户的问题。
        pdf_type (str): PDF的类型。
        pdf_content (str): PDF的内容。
        chat_history (list): 对话历史列表。

        Returns:
        str或generator: 如果使用流式输出，返回一个生成器对象；否则返回一个字符串。
        """
        try:
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
    """
    初始化会话状态参数。

    如果会话状态中不存在"pdf_message"键，则创建一个空列表并将其赋值给"pdf_message"。
    如果会话状态中不存在"pdf"键，则将其初始化为None。
    如果会话状态中不存在"pdf_bot"键，则创建一个新的PDFBot实例并将其赋值给"pdf_bot"。
    如果会话状态中不存在"pdf_content"键，则将其初始化为None。
    如果会话状态中不存在"resume_summary"键，则将其初始化为None。
    """
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
    """
    清除会话状态中的PDF相关记录和PDFBot实例。

    将会话状态中的"pdf_message"键对应的值重置为空列表。
    创建一个新的PDFBot实例并将其赋值给"pdf_bot"键。
    将"pdf"、"pdf_content"和"resume_summary"键对应的值重置为None。
    """
    st.session_state.pdf_message = []
    st.session_state.pdf_bot = pdfbot()
    st.session_state.pdf= None
    st.session_state.pdf_content = None
    st.session_state.resume_summary=None
    

def summary_resume(pdf_content,select_platform,select_model):
    """
    生成PDF简历的摘要。

    Parameters:
    pdf_content (str): PDF简历的内容。
    model_option (str): 选择的模型。
    model_tokes (int): 模型的最大令牌数。

    Returns:
    str或generator: 如果使用流式输出，返回一个生成器对象；否则返回一个字符串。
    """
    try:
        select_temperature=0.2
        model_tokens = model_config.model_description_ls[select_model]["tokens"]
        if select_platform=='百度云平台':
            llm = QianfanChatEndpoint(model=select_model,temperature=select_temperature)
        elif select_platform=='Groq平台':
            llm = ChatGroq(model_name=select_model,max_tokens=model_tokens,temperature=select_temperature)
        elif select_platform=='Siliconflow平台':
            llm = ChatOpenAI(model_name=select_model,base_url="https://api.siliconflow.cn/v1",temperature=select_temperature)
        prompt_selected=prompt_config.resume_summary_prompt
        prompt = ChatPromptTemplate.from_template(prompt_selected)
        chain = prompt | llm | StrOutputParser()
        return chain.stream({
            "resume_content": pdf_content,
        })
    except Exception as e:
        return f"当前模型{select_model}暂不可用，请在左侧栏选择其他模型。"
    

def pdf_page():
    init_params()
    '''页面布局'''
    with st.sidebar:
        with st.container(border=True):
            select_platform=st.selectbox("选择模型平台",options=list(model_config.model_platform_ls.keys()))#模型选择
            select_model=st.selectbox("选择模型",options=model_config.model_platform_ls[select_platform]) 
            select_temperature=st.slider("温度系数",min_value=0.1,max_value=1.0,step=0.1,value=0.7,help='数值低输出更具确定和一致性，数值高更具创造和多样性')#温度选择
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
            if pdf_type=='简历分析':
                with st.chat_message("AI"):
                    st.session_state.resume_summary = st.write_stream(summary_resume(st.session_state.pdf_content,select_platform,select_model))#简历分析
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
        with st.chat_message("Human"):
            st.markdown(question)
            st.session_state.pdf_message.append(HumanMessage(content=question))
        with st.chat_message("AI"):
            st.session_state.pdf_bot.init_llm_model(select_platform,select_model,select_temperature)
            response = st.write_stream(st.session_state.pdf_bot.get_response(question,pdf_type,st.session_state.pdf_content,st.session_state.pdf_message))
            st.session_state.pdf_message.append(AIMessage(content=response))


