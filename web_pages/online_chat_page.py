import asyncio
import sys
import streamlit as st
from config_setting import prompt_config
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from dotenv import find_dotenv, load_dotenv
from config_setting import model_config
from langchain_community.chat_models import QianfanChatEndpoint
from langchain_core.prompts import PromptTemplate
import crawler_modules

class SearchBot:
    def __init__(self):
        """
        初始化SearchBot类的实例，加载环境变量并设置模型选项和令牌数。
        """
        load_dotenv(find_dotenv())#加载环境变量.env
        self.model_option = None
        self.model_tokens = None
        self.content=None

    def generate_based_history_query(self,question,chat_history):
        """
        根据问题和对话历史生成搜索查询。

        Parameters:
        question (str): 用户的问题。
        chat_history (list): 对话历史列表。

        Returns:
        str: 生成的搜索查询。
        """ 
        prompt=PromptTemplate.from_template(prompt_config.query_generated_prompt)
        rag_chain = prompt | self.llm | StrOutputParser()
        result=rag_chain.invoke(
            {
                "chat_history":chat_history, 
                "question": question
            }
        )
        return result
    
    def judge_search(self,question,chat_history):
        """
        判断是否需要进行搜索。

        Parameters:
        question (str): 用户的问题。
        chat_history (list): 对话历史列表。

        Returns:
        str: 判断结果。
        """
        judge_model=QianfanChatEndpoint(model='ERNIE-Lite-8K')
        prompt = PromptTemplate.from_template(prompt_config.judge_search_prompt)
        chain = prompt | judge_model | StrOutputParser()
        response = chain.invoke({
            "chat_history": chat_history,
            "question": question,
        })
        return response
    
    def get_response(self, question,select_search_type,chat_history):
        """
        根据用户的问题和对话历史获取响应。

        Parameters:
        question (str): 用户的问题。
        select_search_type (str): 选择的搜索类型。
        chat_history (list): 对话历史列表。

        Returns:
        str或generator: 如果使用流式输出，返回一个生成器对象；否则返回一个字符串。
        """   
        if self.model_option =='ERNIE-Lite-8K' or self.model_option=='ERNIE-speed-128k': #选择百度千帆大模型
            self.llm = QianfanChatEndpoint(model=self.model_option)
        else:
            self.llm = ChatGroq(model_name=self.model_option,temperature=0.5,max_tokens=self.model_tokens)#ChatGroq模型
        try:
            judge_result=self.judge_search(question,chat_history)#判断是否需要搜索
            if 'yes' in judge_result:#需要搜索
                query=self.generate_based_history_query(question,chat_history)#生成搜索query
                if select_search_type=="duckduckgo":
                    self.content=crawler_modules.duckduck_search(query)
                else:
                    sys_type=sys.platform
                    if sys_type == "win32":
                        loop = asyncio.ProactorEventLoop()#windows系统
                    else:
                        loop = asyncio.SelectorEventLoop()#linux系统
                    self.content = loop.run_until_complete(crawler_modules.google_search_async(query))#异步搜索
                prompt = ChatPromptTemplate.from_template(prompt_config.searchbot_prompt)
                chain = prompt | self.llm | StrOutputParser()
                return chain.stream({
                    "chat_history": chat_history,
                    "question": question,
                    "content": self.content
                })
            else:
                prompt = ChatPromptTemplate.from_template(prompt_config.chatbot_prompt)#不需要搜索，直接chat
                chain = prompt | self.llm | StrOutputParser()
                return chain.stream({
                    "chat_history": chat_history,
                    "question": question,
                })
        except Exception as e:
            return f"当前模型{self.model_option}暂不可用，请在左侧栏选择其他模型。"

def init_params():
    """
    初始化会话状态参数。

    如果会话状态中不存在"search_message"键，则创建一个空列表并将其赋值给"search_message"。
    如果会话状态中不存在"searchbot"键，则创建一个新的SearchBot实例并将其赋值给"searchbot"。
    """
    if "search_message" not in st.session_state:
        st.session_state.search_message=[]
    if "searchbot" not in st.session_state:
        st.session_state.search_bot = SearchBot()


def clear():
    """
    清除会话状态中的搜索记录和SearchBot实例。

    将会话状态中的"search_message"键对应的值重置为空列表。
    创建一个新的SearchBot实例并将其赋值给"searchbot"键。
    """
    st.session_state.search_message = []
    st.session_state.search_bot = SearchBot()


def online_chat_page():
    init_params() # 初始化模型和聊天记录
    '''页面布局'''  
    with st.sidebar:
        with st.container(border=True):
            select_model=st.selectbox("选择模型",options=["百度千帆大模型-128k","百度千帆大模型-8k","谷歌Gemma大模型","Llama3-70b大模型","Llama3-8b大模型","Mixtral大模型"],index=0)# 模型选择
            model_option=model_config.model_ls[select_model]["name"]
            model_tokes=model_config.model_ls[select_model]["tokens"]
            select_search_type=st.selectbox("选择搜索引擎模型",options=["duckduckgo","基于自动化爬虫搜索"],index=1)
            st.button(label="清除聊天记录", on_click=lambda: clear(),use_container_width=True)
    st.title("🌐在线聊天机器人")
    st.subheader(body='',divider="rainbow")
    
    '''滚动更新聊天记录'''
    with st.chat_message("AI"):
        st.markdown("您好，我是基于在线引擎的AI聊天机器人，必要时我会根据实时信息来回答您的问题。此外在我的左侧栏中，您可以更换不同的AI模型和爬虫模型。")
    for message in st.session_state.search_message:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)


    '''用户问题交互'''
    question = st.chat_input("输入你的问题")
    if question:
        st.session_state.search_bot.model_option = model_option
        st.session_state.search_bot.model_tokens = model_tokes
        with st.chat_message("Human"):
            st.markdown(question)
            st.session_state.search_message.append(HumanMessage(content=question))
        with st.chat_message("AI"):
            with st.spinner('思考中....'):  
                response =  st.write_stream(st.session_state.search_bot.get_response(question,select_search_type,st.session_state.search_message))#流式输出
            st.session_state.search_message.append(AIMessage(content=response))


