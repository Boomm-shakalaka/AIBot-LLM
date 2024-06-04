import asyncio
import os
import streamlit as st
from config_setting import prompt_config,model_config
import requests
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import find_dotenv, load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_cohere import CohereEmbeddings
import crawler_modules
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config_setting import model_config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import QianfanChatEndpoint

class urlbot:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.model_option = None
        self.model_tokens = None
        self.llm = None
        self.context = None

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
        try:
            '''get context'''
            if self.model_option =='ERNIE-Lite-8K' or self.model_option=='ERNIE-speed-128k':
                self.llm = QianfanChatEndpoint(model=self.model_option)
            else:
                self.llm = ChatGroq(model_name=self.model_option,temperature=0.1,max_tokens=self.model_tokens)
            query=self.generate_based_history_query(question,chat_history)
            self.context = vectorstore.max_marginal_relevance_search(query=query, k=8)
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
            chain = PromptTemplate.from_template(prompt_config.qa_retrieve_prompt) | self.llm | StrOutputParser()

            return chain.stream({
                    "chat_history":chat_history, 
                    "question": question,
                    "context": self.context
                })
            # result=chain.invoke({"chat_history":chat_history, "question": question,"context": self.context})
            # return result
        except Exception as e:
            return f"当前检索暂不可用，请在左侧栏更换模型，或者选择其他功能。"

        
def init_params():
    if "url_messages" not in st.session_state:
        st.session_state.url_messages = []
    if "url" not in st.session_state:
        st.session_state.url=''
    if "url_bot" not in st.session_state:
        st.session_state.url_bot = urlbot()
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None

def request_website(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
    }
    try:
        response = requests.get(url,headers=headers)
        response.raise_for_status()  # If the response status code is not 200, an exception is thrown
        return response.text
    except requests.RequestException as e:
        return None
    

def clear():
    if "url_messages" in st.session_state:
        st.session_state.url_messages = []
    if "url" in st.session_state:
        st.session_state.url=''
    if "url_bot" in st.session_state:
        st.session_state.url_bot = urlbot()
    if "vectorstore" in st.session_state:
        st.session_state.vectorstore = None


def url_parser(url, select_crawler):
    parse_flag = False
    docs = ''
    try:
        if select_crawler == "Selenium":
            docs = crawler_modules.selenium_url_crawler(url)
        else:
            loop = asyncio.ProactorEventLoop()
            docs = loop.run_until_complete(crawler_modules.playwright_crawler_async(url))
        if len(docs[0].page_content) < 100:#判断是否解析成功
            return docs, parse_flag
        parse_flag = True
        return docs, parse_flag
    except Exception as e:
        return docs, parse_flag

def retrieve_data(docs):
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000,chunk_overlap = 200)
        splits = text_splitter.split_documents(docs)
        embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        return vectorstore
    except Exception as e:
        return f"当前文本嵌入向量处理产生问题，请稍后重试，或者选择其他AI功能"
def url_page():
    init_params()
    '''页面布局'''
    with st.sidebar:
        with st.container(border=True):
            select_model=st.selectbox("选择模型",options=["百度千帆大模型-128k","百度千帆大模型-8k","谷歌Gemma大模型","谷歌gemini大模型","Llama3-70b大模型","Llama3-8b大模型","Mixtral大模型"],index=0)
            model_option=model_config.model_ls[select_model]["name"]
            model_tokes=model_config.model_ls[select_model]["tokens"]
            select_crawler=st.selectbox("选择爬虫",options=["Playwright","Selenium"],index=0)
            show_retrive=st.checkbox("展示检索来源",value=False)
            st.button(label="清除聊天记录", on_click=lambda: clear(),use_container_width=True)
    st.title("🔗URL解析-AI机器人")
    st.subheader(body='',divider="rainbow")

    '''URL输入框'''
    with st.container(border=True):
        st.session_state.url=st.text_input(label='请输入您想要搜索的URL:',value='https://lilianweng.github.io/posts/2023-06-23-agent/')
        confirm_btn=st.button("确认")
    
    '''滚动更新聊天记录'''
    with st.chat_message("AI"):
        st.markdown("您好，我是基于AI大模型的网页解析机器人。您可以现在在上方输入框输入您要检索的网站(https/http)")
    for message in st.session_state.url_messages:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)

    '''URL解析'''
    if confirm_btn:#确认URL
        st.session_state.url_messages = [] #清除聊天记录
        url_response = request_website(st.session_state.url) #请求网页
        if url_response is not None: #判断是否请求成功
            parse_flag = True #解析成功
            with st.chat_message("AI"):
                with st.status("Load Website, please wait..", expanded=True) as status:
                    st.markdown("Parsing data on URL...")
                    docs, parse_flag=url_parser(st.session_state.url,select_crawler) #解析网页
                    if parse_flag==False: #解析失败
                        st.markdown("Parsing failed, please change the crawler model or URL")
                        status.update(label="解析失败，请更换爬虫模型或者URL", state="error", expanded=False)
                    else:#解析成功，开始向量嵌入
                        st.markdown("Embedding the data...")
                        st.session_state.vectorstore=retrieve_data(docs)
                        status.update(label="Parsing complete!", state="complete", expanded=False)
                if parse_flag:  #解析成功            
                    tmp_text = f"\n\n当前访问URL为: {st.session_state.url}.\n\n您可以询问关于该网页的问题。如果您想查询别的网页,请直接输入新的URL"
                    st.markdown(tmp_text) #展示解析成功信息     
        else:#请求失败
            tmp_text = f'URL: ( {st.session_state.url} ) 无法访问,请检查网页是否正确或者该网页无法连接(需要包含http或者https)'
            with st.chat_message("AI"):
                st.markdown(tmp_text)
    
    '''用户问题交互'''
    question = st.chat_input()
    if question and st.session_state.vectorstore:#判断是否有问题,并且已经解析成功
        with st.chat_message("Human"):
            st.markdown(question)
            st.session_state.url_messages.append(HumanMessage(content=question))
        with st.chat_message("AI"):
            with st.spinner('检索中....'):
                st.session_state.url_bot.model_option = model_option
                st.session_state.url_bot.model_tokens = model_tokes
                chat_history = st.session_state.url_messages
                vectorstore = st.session_state.vectorstore
                # response=st.session_state.url_bot.get_response(question,chat_history,vectorstore)
                response = st.write_stream(st.session_state.url_bot.get_response(question,chat_history,vectorstore))#流式输出
                st.session_state.url_messages.append(AIMessage(content=response))
            if show_retrive:#展示检索来源
                with st.expander("来源内容"):
                    for i in range(len(st.session_state.url_bot.context)):
                        st.markdown(f"第{i}个相关内容: {st.session_state.url_bot.context[i].page_content}")


