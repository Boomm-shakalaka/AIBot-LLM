import streamlit as st
from config_setting import prompt_config
import requests
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import find_dotenv, load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_cohere import CohereEmbeddings
from url_crawler import url_to_text
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config_setting import model_config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import QianfanChatEndpoint
import random
class urlbot:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.model_option = None
        self.model_tokens = None
        self.chat_history = []

    def retrieve_data(self,docs):
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000,chunk_overlap = 200)
            splits = text_splitter.split_documents(docs)
            # bge_embeddings = HuggingFaceBgeEmbeddings(model_name="moka-ai/m3e-base")
            embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")
            self.vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        except Exception as e:
            return f"当前文本嵌入向量处理产生问题，请稍后重试，或者选择其他AI功能"
    
    def generate_based_history_query(self,question,chat_history):
        based_history_prompt="""
            Use the following latest User Question to formulate a standalone query.
            If the user's questions are asked in Chinese, then the standalone query you formulate can also be output in Chinese.
            The query can be understood without the Chat History.
            The output should just be the sentence sutiable for query. 
            If you feel confused, just output the latest User Question.
            Do not provide any answer.
            User Question: '''{question}'''
            Chat History: '''{chat_history}'''
            query:
        """
        rag_chain = PromptTemplate.from_template(based_history_prompt) | self.llm | StrOutputParser()
        result=rag_chain.invoke(
            {
                "chat_history":chat_history , 
                "question": question
            }
        )
        return result

    def get_response(self,question):
        try:
            '''get context'''
            if self.model_option =='ERNIE-Lite-8K':
                self.llm = QianfanChatEndpoint(model=self.model_option,temperature=0.1)
            else:
                self.llm = ChatGroq(model_name=self.model_option,temperature=0.1,max_tokens=self.model_tokens)
            query=self.generate_based_history_query(question,self.chat_history)
            self.context = self.vectorstore.max_marginal_relevance_search(query=query, k=8)
            '''get response'''
            qa_system_prompt="""
                            You need to answer User Questions based on Context.
                            If the User Questions are asked in Chinese, then your answers must also be in Chinese.
                            You can also use Chat History to help you understand User Questions.
                            If you don't know the answer, just say that you don't know, don't try to make up an answer.
                            Context: '''{context}'''
                            User Questions: '''{question}'''
                            Chat History: '''{chat_history}'''
                            """
            chain = PromptTemplate.from_template(qa_system_prompt) | self.llm | StrOutputParser()

            return chain.stream({
                    "chat_history":self.chat_history, 
                    "question": question,
                    "context": self.context
                })
        except Exception as e:
            return f"当前检索暂不可用，请在左侧栏更换模型，或者选择其他功能。"

        
def init_params(init_url_message):
    #初始化页面聊天记录
    if "url_messages" not in st.session_state:
        st.session_state.url_messages = [AIMessage(content=init_url_message)]
    #初始化URL链接
    if "url" not in st.session_state:
        st.session_state.url=''
    #初始化机器人
    if "url_bot" not in st.session_state:
        st.session_state.url_bot = urlbot()

def parse_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
    }
    loader = WebBaseLoader(web_paths=url)
    docs = loader.load()
    return docs


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
    

def clear(init_url_message):
    #初始化页面聊天记录
    if "url_messages" in st.session_state:
        st.session_state.url_messages = [AIMessage(content=init_url_message)]
    #初始化URL链接
    if "url" in st.session_state:
        st.session_state.url=''
    #初始化机器人
    if "url_bot" in st.session_state:
        st.session_state.url_bot = urlbot()
    

def url_page():
    #左侧栏
    with st.sidebar:
        #模型选择
        select_model=st.selectbox("选择模型",options=["百度千帆大模型","谷歌Gemma大模型","谷歌gemini大模型","Llama3-70b大模型","Llama3-8b大模型","Mixtral大模型"],index=0)
        model_option=model_config.model_ls[select_model]["name"]
        model_tokes=model_config.model_ls[select_model]["tokens"]

        #清除聊天记录
        st.button("清除记录", on_click=lambda: clear(init_url_message))
    
    
    # #初始化消息"
    init_url_message = "您好，我是基于AI大模型的网页解析机器人。您可以现在在上方输入框输入您要检索的网站(https/http)"
    init_params(init_url_message)
    #输入网站
    with st.container(border=True):
        st.session_state.url=st.text_input(label='请输入您想要搜索的URL:',value='https://lilianweng.github.io/posts/2023-06-23-agent/')
        confirm_btn=st.button("确认")
    
    #网页聊天记录
    for message in st.session_state.url_messages:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)

    if confirm_btn:
        st.session_state.url_bot.chat_history = []  #模型清空聊天记录
        url_response = request_website(st.session_state.url)
        if url_response is not None:
            parse_flag = True
            with st.chat_message("AI"):
                with st.status("Load Website, please wait..", expanded=True) as status:
                    st.markdown("Parsing data on URL...")
                    # docs = parse_data(st.session_state.url)   #parse_data
                    docs=url_to_text(st.session_state.url)
                    if len(docs[0].page_content) < 100:
                        parse_flag = False
                        st.markdown("该URL无法解析，请使用其他URL")
                        status.update(label="该URL无法解析，请使用其他URL!", state="error", expanded=False)
                    else:
                        parse_flag = True
                        st.markdown("Embedding the data...")
                        st.session_state.url_bot.retrieve_data(docs)
                        status.update(label="Parsing complete!", state="complete", expanded=False)
                if parse_flag:              
                    tmp_text = f"\n\n当前访问URL为: {st.session_state.url}.\n\n您可以询问关于该网页的问题。\
                            如果您想查询别的网页,请直接输入新的URL "
                    st.markdown(tmp_text)
                    st.session_state.url_messages = [AIMessage(content=tmp_text)]      
        else:
            tmp_text = f'URL: ( {st.session_state.url} ) 无法访问,请检查网页是否正确或者该网页无法连接(需要包含http或者https)'
            with st.chat_message("AI"):
                st.markdown(tmp_text)
                st.session_state.url_messages =[AIMessage(content=tmp_text)]
    question = st.chat_input()
    if question and st.session_state.url_bot.vectorstore:
        with st.chat_message("Human"):
            st.markdown(question)
            st.session_state.url_messages.append(HumanMessage(content=question))
        with st.chat_message("AI"):
            with st.spinner('检索中....'):
                st.session_state.url_bot.model_option = model_option
                st.session_state.url_bot.model_tokens = model_tokes
                response = st.write_stream(st.session_state.url_bot.get_response(question))
                st.session_state.url_bot.chat_history.extend([HumanMessage(content=question), response])
                st.session_state.url_messages.append(AIMessage(content=response))
            with st.expander("来源内容"):
                for i in range(len(st.session_state.url_bot.context)):
                    st.markdown(f"第{i}个相关内容: {st.session_state.url_bot.context[i].page_content}")


