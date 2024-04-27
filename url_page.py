import time
import streamlit as st
import config_setting.model_config as model_config
import URLBot_framework
import re
import requests
from urllib.parse import urlparse
from langchain_community.document_loaders import WebBaseLoader
from langchain.memory import ChatMessageHistory
#https://www.google.com


def parse_data(url):
    loader = WebBaseLoader(url)
    docs = loader.load()
    return docs

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
    
    

def validate_url(url):
    pattern = r"^http"  # Begin with http
    if re.match(pattern, url):
        url=url
    else:
        url='https://'+url
    url_response=request_website(url)
    if url_response:
        print(st.session_state.url_flag)
        st.session_state.url_flag=1
    else:
        st.session_state.url_flag=0

def request_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # If the response status code is not 200, an exception is thrown
        return response.text
    except requests.RequestException as e:
        return None
     
with st.sidebar:
    #模型选择
    model_option = st.selectbox(
    "选择机器人模型:",
    options=list(model_config.models.keys()),
    format_func=lambda x: model_config.models[x]["name"],
    index=1  # Default to mixtral
    )
    #清除聊天记录
    def clear_chat_history():
        st.session_state.pop("messages", None)
        st.session_state.URL_chat_history=[]
        st.session_state.retriever = None
        st.session_state.url=''

    st.button("Clear Chat History", on_click=lambda: clear_chat_history())
    st.text("Gemma更适合中文语境")
    # st.text("LLaMA2-70b性能均衡")
    st.text("LLaMA3-70b精准度高")
    st.text("LLaMA3-8b速度快")
    st.text("Mixtral速度快，适合长文本")
st.header("基于URL检索-AI机器人", divider="rainbow", anchor=False)



#初始化模型选择
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None
#初始化页面聊天记录
if "messages" not in st.session_state:
    st.session_state["messages"] = list()
#初始化URL链接
if "url" not in st.session_state:
    st.session_state.url=''
#初始模型聊天记录
if "URL_chat_history" not in st.session_state:
    st.session_state.URL_chat_history = []
#初始化向量
if "retriever" not in st.session_state:
    st.session_state.retriever = None

#初始模型
# if "bot" not in st.session_state:
#     st.session_state.bot=URLBot_framework.Bot(model_option)

#初始化对话过程
with st.chat_message("assistant"):
    st.write("您好，我是基于AI大模型的网页解析机器人，\
                                        您可以现在下方聊天框输入想要搜索的URL，我会根据该网页内容尽可能地回答您的问题。")



#初始模型
bot=URLBot_framework.Bot(model_option)

#输入问题
question = st.chat_input('example: https://www.baidu.com')
if question:
    if st.session_state.url=='': #没有给网站链接
        url_response=request_website(question)
        if url_response:  #是URL

            with st.status("Load Website, please wait..", expanded=True) as status:
                st.write("Parsing data on URL...")
                docs=parse_data(question)
                st.write("Embedding the data...")
                bot.retrieve_data(docs)
                status.update(label="Parsing complete!", state="complete", expanded=False)

            with st.chat_message("assistant"):
                st.write("当前访问URL为:"+question)
                st.write('您可以进行提问。如果您想查询别的网页,请直接输入URL')

            st.session_state.url=question  #保存URL
            st.session_state.retriever=bot.retriever #保存retriever
            st.session_state.URL_chat_history=bot.chat_history#保存chat_history
        else: #无法访问
            st.chat_message("assistant").write('URL无法访问,请检查URL是否正确或者网页无法连接(需要包含http或者https)')
    else:#已经有url，要么是提示词，要么是新的url
        url_response=request_website(question)
        if url_response:#新的url
            with st.status("Load Website, please wait..", expanded=True) as status:
                st.write("Parsing data on URL...")
                docs=parse_data(question)
                st.write("Embedding the data...")
                bot.retrieve_data(docs)
                status.update(label="Parsing complete!", state="complete", expanded=False)

            with st.chat_message("assistant"):
                st.write("当前访问URL为:"+question)
                st.write('您可以进行提问。如果您想查询别的网页,请直接输入URL')
                
            st.session_state.url=question  #保存URL
            st.session_state.retriever=bot.retriever #保存retriever
            st.session_state.URL_chat_history=bot.chat_history#保存chat_history
        else:#提示词
            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).write(msg["content"])
            #问答
            with st.status("AIbot is thinking...", expanded=True) as status:
                result=bot.get_answer(question,st.session_state.retriever,st.session_state.URL_chat_history)
                status.update(label="Complete!", state="complete", expanded=False)

            st.session_state.URL_chat_history=bot.chat_history
            st.session_state.messages.append({"role": "user", "content": question})
            st.session_state.messages.append({"role": "assistant", "content": result})
            st.chat_message("user").write(question)
            st.chat_message("assistant").write(result)

                

