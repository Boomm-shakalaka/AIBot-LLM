import time
import streamlit as st
from config_setting import model_config, func_modules,prompt_config
from st_pages import Page, Section, show_pages, add_page_title
import requests
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.messages import AIMessage, HumanMessage


########################################
#机器人模型
########################################
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
import os

# os.environ["LANGCHAIN_TRACING_V2"] = "true"  #LangSmith init
load_dotenv(find_dotenv())
def retrieve_data(docs):
    try:
        text_splitter = RecursiveCharacterTextSplitter()
        splits = text_splitter.split_documents(docs)
        # bge_embeddings = HuggingFaceBgeEmbeddings(model_name="moka-ai/m3e-base")
        embeddings = CohereEmbeddings(model="embed-multilingual-light-v3.0")
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        return vectorstore.as_retriever()
    except Exception as e:
        return f"当前文本嵌入向量处理产生问题，请稍后重试，或者选择其他AI功能"

def get_response_langsmith(model_option,retriever,question):
    llm = ChatGroq(model_name=model_option)
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | prompt_config.rag_prompt
        | llm
        | StrOutputParser()
    )

    # rag_chain_with_source = RunnableParallel(
    #     {"context": retriever, "question": RunnablePassthrough()}
    # ).assign(answer=rag_chain_from_docs)
    rag_chain_with_source=RunnableParallel(
        {"context": retriever, "question": RunnablePassthrough()}
    ).assign(answer=rag_chain_from_docs)
    for chunk in rag_chain_with_source.stream(question):
        print(chunk)
    return ''


def get_response(model_option,retriever,question,chat_history):
    try:
        llm = ChatGroq(model_name=model_option)
        # Create the chain for historical messages
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", prompt_config.contextualize_q_system_prompt_en),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )
        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
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
            "chat_history": chat_history
            })
        return result['answer']
    except Exception as e:
        return f"当前检索暂不可用，请在左侧栏更换模型，或者选择其他功能。"



########################################
#初始化参数
########################################
#初始化消息"
init_url_message = "您好，我是基于AI大模型的网页解析机器人。您可以现在下方聊天框输入想要搜索的URL，我会根据该网页内容尽\
                    可能地回答您的问题。"

#初始化页面聊天记录
if "url_history" not in st.session_state:
    st.session_state.url_history = [AIMessage(content=init_url_message)]

#初始模型聊天记录
if "url_chat_history" not in st.session_state:
    st.session_state.url_chat_history = [
        AIMessage(content=init_url_message),
    ]
#初始化URL链接
if "url" not in st.session_state:
    st.session_state.url=''
#初始化向量
if "retriever" not in st.session_state:
    st.session_state.retriever = None
#初始化模型回答
if "response" not in st.session_state:
    st.session_state.response=''

########################################
#前端页面设计与功能开发
########################################
#页面title
set_page_config=st.set_page_config(
        page_title="AIBot", 
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="auto",  #侧边栏是否固定,"auto", "expanded", or "collapsed"
        # menu_items={
        #     'Get Help': 'https://www.extremelycoolapp.com/help',
        #     'Report a bug': "https://www.extremelycoolapp.com/bug",
        #     'About': "# This is a header. This is an *extremely* cool app!"
        # }

)


#页面导航
add_page_title() #有这个show_pages才能生效
show_pages(
    [    
        # Section(name='AI功能',icon='🤖'),
        Page("chat_page.py", "AI-聊天机器人"),
        Page("url_page.py", "URL检索机器人"),
        Page("pdf_page.py", "AI-PDF解析机器人"),
        # Page("summary_page.py", "摘要-AI分析机器人"),
        # Page("AboutPage.py", "关于About")
    ]
)
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
    def clear_chat_history():
        st.session_state.url_history = [AIMessage(content=init_url_message),]#初始化模型聊天记录
        st.session_state.url_chat_history = [AIMessage(content=init_url_message),]#初始模型聊天记录
        st.session_state.url=''#初始化URL链接
        st.session_state.retriever = None#初始化向量
        st.session_state.response=''#初始化模型回答
    
    st.button("清除记录", on_click=lambda: clear_chat_history())



#网页聊天记录
for message in st.session_state.url_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

def parse_data(url):
    loader = WebBaseLoader(url)
    docs = loader.load()
    return docs


def request_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # If the response status code is not 200, an exception is thrown
        return response.text
    except requests.RequestException as e:
        return None
    

#输入问题
question = st.chat_input('example: https://www.baidu.com')
if question:
    if st.session_state.url=='': #没有给网站链接
        url_response=request_website(question)
        if url_response:  #是URL
            with st.chat_message("AI"):
                with st.status("Load Website, please wait..", expanded=True) as status:
                    st.write("Parsing data on URL...")
                    docs=parse_data(question)
                    st.write("Embedding the data...")
                    st.session_state.retriever=retrieve_data(docs)
                    status.update(label="Parsing complete!", state="complete", expanded=False)
                tmp_text=f"\n\n当前访问URL为: {question}.\n\n您可以询问关于该网页的问题。\
                                如果您想查询别的网页,请直接输入新的URL "
                st.markdown(tmp_text)
                st.session_state.url=question  #保存URL
                st.session_state.url_history = [] #网页聊天记录初始化
                st.session_state.url_history.append(AIMessage(content=tmp_text))
                st.session_state.url_chat_history = [AIMessage(content=init_url_message),] #模型聊天记录初始化
        else: #无法访问
            tmp_text=f'URL: ( { question } ) 无法访问,请检查网页是否正确或者该网页无法连接(需要包含http或者https)'
            with st.chat_message("AI"):
                st.markdown(tmp_text)
            st.session_state.url_history.append(AIMessage(content=tmp_text))
    else:#已经有url，要么是提示词，要么是新的url
        url_response=request_website(question)
        if url_response:#新的url
            with st.chat_message("AI"):
                with st.status("Load Website, please wait..", expanded=True) as status:
                    st.write("Parsing data on URL...")
                    docs=parse_data(question)
                    st.write("Embedding the data...")
                    st.session_state.retriever=retrieve_data(docs)
                    status.update(label="Parsing complete!", state="complete", expanded=False)
                tmp_text=f"\n\n当前访问URL为: {question}.\n\n您可以询问关于该网页的问题。\
                                如果您想查询别的网页,请直接输入新的URL "
                st.markdown(tmp_text)
                st.session_state.url=question  #保存URL
                st.session_state.url_history = [] #网页聊天记录初始化
                st.session_state.url_history.append(AIMessage(content=tmp_text))
                st.session_state.url_chat_history = [AIMessage(content=init_url_message),] #模型聊天记录初始化
        else:#提示词
            with st.chat_message("Human"):
                st.markdown(question)
            st.session_state.url_history.append(HumanMessage(content=question)) #添加网页记录
            st.session_state.url_chat_history.append(HumanMessage(content=question))  #添加模型问题记录
            with st.chat_message("AI"):
                with st.spinner('检索中....'):
                    # response=st.write_stream(get_response_langsmith(model_option,st.session_state.retriever,question))
                    st.session_state.response = get_response(model_option,st.session_state.retriever,question, st.session_state.url_chat_history)
                st.markdown(st.session_state.response)          
            st.session_state.url_history.append(AIMessage(content=st.session_state.response))#添加网页记录
            st.session_state.url_chat_history.append(AIMessage(content=st.session_state.response))  #添加模型问题记录



                

