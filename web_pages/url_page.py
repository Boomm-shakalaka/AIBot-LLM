import streamlit as st
from config_setting import model_config,prompt_config
import requests
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import find_dotenv, load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
from langchain_groq import ChatGroq
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.chains import create_history_aware_retriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough,RunnableParallel
from langchain_cohere import CohereEmbeddings
import bs4
class urlbot:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.model_option = None
        self.retriever = None
        self.chat_history = []

    def retrieve_data(self,docs):
        try:
            text_splitter = RecursiveCharacterTextSplitter()
            splits = text_splitter.split_documents(docs)
            # bge_embeddings = HuggingFaceBgeEmbeddings(model_name="moka-ai/m3e-base")
            embeddings = CohereEmbeddings(model="embed-multilingual-light-v3.0")
            vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
            self.retriever=vectorstore.as_retriever()
            # return vectorstore.as_retriever()
        except Exception as e:
            return f"当前文本嵌入向量处理产生问题，请稍后重试，或者选择其他AI功能"

    def get_response(self,question):
        try:
            llm = ChatGroq(model_name=self.model_option,temperature=0)
            # Create the chain for historical messages
            contextualize_q_prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", prompt_config.contextualize_q_system_prompt_en),
                        MessagesPlaceholder("chat_history"),
                        ("human", "{input}"),
                    ]
                )
            history_aware_retriever = create_history_aware_retriever(
                llm, self.retriever, contextualize_q_prompt
            )
            # Create the chain for full question and answer
            qa_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", prompt_config.qa_system_prompt_en),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )
            question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
            rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
            result=rag_chain.invoke({
                "input": question, 
                "chat_history": self.chat_history
                })
            self.chat_history.extend([HumanMessage(content=question), result["answer"]])
            return result['answer']
        except Exception as e:
            return f"当前检索暂不可用，请在左侧栏更换模型，或者选择其他功能。"
def init_params(init_url_message):
    #初始化页面聊天记录
    if "url_messages" not in st.session_state:
        st.session_state.url_messages = [AIMessage(content=init_url_message)]
    #初始化URL链接
    if "url" not in st.session_state:
        st.session_state.url=''
    # #初始化向量
    # if "retriever" not in st.session_state:
    #     st.session_state.retriever = None
    #初始化机器人
    if "url_bot" not in st.session_state:
        st.session_state.url_bot = urlbot()

def parse_data(url):
    loader = WebBaseLoader(
    web_paths=(url,),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header"))
        ),
    )

    docs = loader.load()
    return docs


def request_website(url):
    try:
        response = requests.get(url)
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
    #初始化向量
    # if "retriever" in st.session_state:
    #     st.session_state.retriever = None
    #初始化机器人
    if "url_bot" in st.session_state:
        st.session_state.url_bot = urlbot()
    

def url_page():
    #左侧栏
    with st.sidebar:
        #模型选择
        model_option = st.selectbox(
            "选择机器人模型:",
            options=list(model_config.models.keys()),
            format_func=lambda x: model_config.models[x]["name"],
            index=4  # Default to mixtral
        )
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
        url_response = request_website(st.session_state.url)
        if url_response:
            with st.chat_message("AI"):
                with st.status("Load Website, please wait..", expanded=True) as status:
                    st.markdown("Parsing data on URL...")
                    docs = parse_data(st.session_state.url)   #parse_data
                    if len(docs[0].page_content) ==0:
                        st.markdown("该URL无法解析，请使用其他URL")
                        status.update(label="该URL无法解析，请使用其他URL!", state="error", expanded=False)
                    else:
                        st.markdown("Embedding the data...")
                        st.session_state.url_bot.retrieve_data(docs)  #retrieve_data
                        status.update(label="Parsing complete!", state="complete", expanded=False)
                        tmp_text = f"\n\n当前访问URL为: {st.session_state.url}.\n\n您可以询问关于该网页的问题。\
                                如果您想查询别的网页,请直接输入新的URL "
                        st.markdown(tmp_text)
                        st.session_state.url_messages = [AIMessage(content=tmp_text)]
                # st.session_state.url_bot.chat_history = []  #模型清空聊天记录
        else:
            tmp_text = f'URL: ( {st.session_state.url} ) 无法访问,请检查网页是否正确或者该网页无法连接(需要包含http或者https)'
            with st.chat_message("AI"):
                st.markdown(tmp_text)
                st.session_state.url_messages =[AIMessage(content=tmp_text)]

    question = st.chat_input()
    if question and st.session_state.url_bot.retriever:
        with st.chat_message("Human"):
            st.markdown(question)
            st.session_state.url_messages.append(HumanMessage(content=question))
        with st.chat_message("AI"):
            with st.spinner('检索中....'):
                st.session_state.url_bot.model_option = model_option
                response = st.session_state.url_bot.get_response(question)
            st.markdown(response)
        st.session_state.url_messages.append(AIMessage(content=response))



