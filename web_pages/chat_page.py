import random
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_community.chat_models import QianfanChatEndpoint
from config_setting import model_config,prompt_config
from langchain_openai import ChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import find_dotenv, load_dotenv

class chatbot:
    def __init__(self):
        """
        初始化ChatBot类的实例，加载环境变量并设置模型选项和令牌数。
        """
        load_dotenv(find_dotenv())#加载环境变量
        self.llm = None

    def init_llm_model(self,select_platform,select_model,select_temperature):
        """
        初始化模型。

        Parameters:
        select_platform (str): 选择的模型平台。
        select_model (str): 选择的模型。
        """
        model_tokens = model_config.model_description_ls[select_model]["tokens"]
        if select_platform=='百度云平台':
            self.llm = QianfanChatEndpoint(model=select_model,temperature=select_temperature)
        elif select_platform=='Groq平台':
            self.llm = ChatGroq(model_name=select_model,max_tokens=model_tokens,temperature=select_temperature)
        elif select_platform=='Siliconflow平台':
            self.llm = ChatOpenAI(model_name=select_model,base_url="https://api.siliconflow.cn/v1",temperature=select_temperature)
        # elif select_platform=='Google':
        #     self.llm = ChatGoogleGenerativeAI(model=select_model,temperature=0.7)#ChatGoogleGenerativeAI模型


    def get_response(self,question,chat_history):
        """
        根据用户的问题和对话历史获取响应。

        Parameters:
        question (str): 用户的问题。
        chat_history (list): 对话历史列表。

        Returns:
        str或generator: 如果使用流式输出，返回一个生成器对象；否则返回一个字符串。
        """
        try:
            prompt = ChatPromptTemplate.from_template(prompt_config.chatbot_prompt)
            chain = prompt | self.llm| StrOutputParser()
            # result=chain.invoke({"chat_history": chat_history,"question": question,}) #非流式输出
            # return result
            return chain.stream({
                "chat_history": chat_history,
                "question": question,
            })
        except Exception as e:
            return f"当前模型{self.model_option}暂不可用，请在左侧栏选择其他模型。"
        
def init_params():
    """
    初始化会话状态参数。

    如果会话状态中不存在"chat_message"键，则创建一个空列表并将其赋值给"chat_message"。
    如果会话状态中不存在"chat_bot"键，则创建一个新的ChatBot实例并将其赋值给"chat_bot"。
    """
    if "chat_message" not in st.session_state:
        st.session_state.chat_message = []
    if "chat_bot" not in st.session_state:
        st.session_state.chat_bot = chatbot()
        
def clear():
    """
    清除会话状态中的聊天记录和模型实例。

    将会话状态中的"chat_message"键对应的值重置为空列表。
    创建一个新的ChatBot实例并将其赋值给"chat_bot"键。
    """
    st.session_state.chat_message = [] #清除聊天记录
    st.session_state.chat_bot = chatbot() #重新初始化模型

def chat_page():
    init_params()#初始化模型和聊天记录
    '''页面布局'''    
    with st.sidebar:
        with st.container(border=True):
            select_platform=st.selectbox("选择模型平台",options=list(model_config.model_platform_ls.keys()))#模型选择
            select_model=st.selectbox("选择模型",options=model_config.model_platform_ls[select_platform]) 
            select_temperature=st.slider("温度系数",min_value=0.1,max_value=1.0,step=0.1,value=0.7,help='数值低输出更具确定和一致性，数值高更具创造和多样性')#温度选择
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
        with st.chat_message("Human"):
            st.markdown(question)
            st.session_state.chat_message.append(HumanMessage(content=question))#添加用户问题聊天记录
        with st.chat_message("AI"):
            st.session_state.chat_bot.init_llm_model(select_platform,select_model,select_temperature)
            response = st.write_stream(st.session_state.chat_bot.get_response(question,st.session_state.chat_message)) #流式输出，所以不用markdown
            st.session_state.chat_message.append(AIMessage(content=response))#添加用户问题聊天记录
