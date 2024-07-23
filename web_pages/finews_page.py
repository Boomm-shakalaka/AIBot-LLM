import random
from langchain_cohere import CohereEmbeddings
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_community.chat_models import QianfanChatEndpoint
from config_setting import model_config,prompt_config
from dotenv import find_dotenv, load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
import re
class finewsbot():
    def __init__(self):
        """
        初始化ChatBot类的实例，加载环境变量并设置模型选项和令牌数。
        """
        load_dotenv(find_dotenv())#加载环境变量
        self.llm = None
        self.model_tokens=4096
        self.context = None
    
    def init_llm_model(self,select_platform,select_model,select_temperature):
        """
        初始化模型。
        """
        self.model_tokens = model_config.model_description_ls[select_model]["tokens"]
        if select_platform=='百度云平台':
            self.llm = QianfanChatEndpoint(model=select_model,temperature=select_temperature)
        elif select_platform=='Groq平台':
            self.llm = ChatGroq(model_name=select_model,max_tokens=self.model_tokens,temperature=select_temperature)
        elif select_platform=='Siliconflow平台':
            self.llm = ChatOpenAI(model_name=select_model,base_url="https://api.siliconflow.cn/v1",temperature=select_temperature)
    
    def generate_based_history_query(self,question,chat_history):
        rag_chain = PromptTemplate.from_template(prompt_config.query_generated_prompt) | self.llm | StrOutputParser()
        result=rag_chain.invoke(
            {
                "chat_history":chat_history , 
                "question": question
            }
        )
        return result
    
    def get_response(self,question,chat_history,vectorstore):
        '''get context'''
        query=self.generate_based_history_query(question,chat_history)
        self.context = vectorstore.max_marginal_relevance_search(query=query, k=10)
        '''限制context长度'''
        context_len,chat_history_len=0,0
        if self.context is not None:
            context_len=len(self.context)
        if chat_history is not None:
            chat_history_len=len(chat_history)
        if context_len+chat_history_len-200 >self.model_tokens:
            self.context=self.context[:self.model_tokens-200]#限制context长度
            chat_history=chat_history[:self.model_tokens-200]#限制chat_history长度
        '''get response'''
        chain = PromptTemplate.from_template(prompt_config.finews_retrieve_prompt) | self.llm | StrOutputParser()
        return chain.stream({
                "chat_history":chat_history, 
                "question": question,
                "context": self.context
            })
            # result=chain.invoke({"chat_history":chat_history, "question": question,"context": self.context})
            # return result
    # except Exception as e:
    #     return f"当前检索暂不可用，请在左侧栏更换模型，或者选择其他功能。"

def get_latest_db_file():
    """
    获取最新的数据库文件。
    获取当前脚本的目录，然后获取项目根目录。
    获取所有以"chroma_db_"开头的文件名。
    使用正则表达式来提取时间戳。
    使用max函数找出最新的文件。
    返回最新的文件名，如果没有找到则返回None。
    """
    # 获取当前脚本的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录（E:\Desktop\AIBot-LLM）
    root_dir = os.path.dirname(current_dir)
    # 获取所有以"chroma_db_"开头的文件名
    chroma_db_files = [f for f in os.listdir(root_dir) if f.startswith("chroma_db_")]
    # 定义一个正则表达式来提取时间戳
    pattern = re.compile(r'chroma_db_(\d{12})')
    # 使用max函数找出最新的文件
    latest_db_name = None
    latest_timestamp = None
    for file in chroma_db_files:
        match = pattern.match(file)
        if match:
            timestamp = match.group(1)
            if latest_timestamp is None or timestamp > latest_timestamp:
                latest_timestamp = timestamp
                latest_db_name = file
    
    return root_dir,latest_db_name
    # except Exception as e:
    #     return None

def init_params():
    """
    初始化会话状态中的聊天记录和模型实例。
    将会话状态中的"finews_message"键对应的值重置为空列表。
    创建一个新的finewsbot实例并将其赋值给"finews_bot"键。
    """

    if "finews_message" not in st.session_state:
        st.session_state.finews_message = []
    if "finews_bot" not in st.session_state:
        st.session_state.finews_bot = finewsbot()
    if "finews_vectorstore" not in st.session_state:
        st.session_state.finews_vectorstore = None

def clear():
    """
    清除会话状态中的聊天记录和模型实例。

    将会话状态中的"finews_message"键对应的值重置为空列表。
    创建一个新的finewsbot实例并将其赋值给"finews_bot"键。

    """
    st.session_state.finews_message = [] #清除聊天记录
    st.session_state.finews_bot = finewsbot() #重新初始化模型
    if "finews_vectorstore" not in st.session_state:
        st.session_state.finews_vectorstore = None

def finews_page():
    init_params()#初始化模型和聊天记录
    '''页面布局'''    
    with st.sidebar:
        with st.container(border=True):
            select_platform=st.selectbox("选择模型平台",options=list(model_config.model_platform_ls.keys()))#模型选择
            select_model=st.selectbox("选择模型",options=model_config.model_platform_ls[select_platform]) 
            select_temperature=st.slider("温度系数",min_value=0.1,max_value=1.0,step=0.1,value=0.7,help='数值低输出更具确定和一致性，数值高更具创造和多样性')#温度选择
            show_retrive=st.checkbox("展示检索来源",value=False)
            st.button(label="清除聊天记录", on_click=lambda: clear(),use_container_width=True) #清除聊天记录按钮
    st.title("💰 金融资讯机器人")
    st.subheader(body='',divider="rainbow")

    '''滚动更新聊天记录'''
    with st.chat_message("AI"):
        st.markdown("您好，我是AI金融资讯机器人，我会根据最新的一些金融新闻回答你的问题。此外在我的左侧栏中，您可以更换不同的AI模型。")
    for message in st.session_state.finews_message:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)
    finews_vectorstore_flag=st.session_state.finews_vectorstore
    if finews_vectorstore_flag is None:
        with st.chat_message("AI"):
            with st.status("正在获取最新的金融资讯", expanded=True) as status:
                st.markdown("获取最新数据库...")
                root_dir,latest_db_name=get_latest_db_file() #获取最新的数据库文件
                if latest_db_name is None:
                    st.markdown("数据库获取失败")
                    status.update(label="获取失败，请稍后尝试或者在About页面提交Issue", state="error", expanded=False)
                else:
                    collection_name="vectorstore_"+latest_db_name.split("_")[-1]
                    db_name=os.path.join(root_dir,latest_db_name)
                    print(db_name)
                    st.session_state.finews_vectorstore = Chroma(collection_name=collection_name,persist_directory=db_name, embedding_function=CohereEmbeddings(model="embed-multilingual-v3.0"))
                    if st.session_state.finews_vectorstore is not None:
                        st.markdown("数据库获取成功")
                        status.update(label="数据库获取成功", state="complete", expanded=False)
                    else:
                        st.markdown("数据库获取失败")
                        status.update(label="数据库获取失败", state="error", expanded=False)
        finews_vectorstore_flag=st.session_state.finews_vectorstore

    if finews_vectorstore_flag is not None:
        '''用户问题交互'''
        question = st.chat_input("输入你的问题")
        if question:
            with st.chat_message("Human"):
                st.markdown(question)
                st.session_state.finews_message.append(HumanMessage(content=question))#添加用户问题聊天记录
            with st.chat_message("AI"):
                with st.spinner('检索中....'):
                    chat_history = st.session_state.finews_message
                    vectorstore = st.session_state.finews_vectorstore
                    # response=st.session_state.finews_bot.get_response(question,chat_history,vectorstore)
                    st.session_state.finews_bot.init_llm_model(select_platform,select_model,select_temperature)
                    response = st.write_stream(st.session_state.finews_bot.get_response(question,chat_history,vectorstore))#流式输出
                    st.session_state.finews_message.append(AIMessage(content=response))
                if show_retrive:#展示检索来源
                    with st.expander("来源内容"):
                        for i in range(len(st.session_state.finews_bot.context)):
                            st.markdown(f"第{i}个相关内容: {st.session_state.finews_bot.context[i].page_content}")
