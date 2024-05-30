import streamlit as st
from config_setting import prompt_config
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from dotenv import find_dotenv, load_dotenv
from config_setting import model_config
from langchain_community.chat_models import QianfanChatEndpoint
from duckduckgo_search import DDGS
from langchain_core.prompts import PromptTemplate
from langchain_community.tools import DuckDuckGoSearchResults
import requests
import re
import time
from langchain_community.document_loaders import WebBaseLoader

class SearchBot:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.model_option = None
        self.chat_history = []
        self.model_tokens = None
        self.content=None

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
    def judge_search(self,question,chat_history):
        judge_model=QianfanChatEndpoint(model='ERNIE-Lite-8K')
        prompt_tempate="""
                        Give you a question, you need to judge whether you need real-time information to answer.\n
                        If you think you need more real-time information to answer the question better, 
                        you just need to output "yes".\n
                        If you think you can answer the question without real-time information, you just need to output "no".\n
                        Do not explain your decision process and have any tips. The output should be "yes" or "no".\n
                        User Question: {question}.
                        Chat History: {chat_history}.
                        """
        prompt = PromptTemplate.from_template(prompt_tempate)
        chain = prompt | judge_model | StrOutputParser()
        response = chain.invoke({
            "chat_history": chat_history,
            "question": question,
        })
        return response
    
    def duckduck_search(self,question):
        def format_text(text):
            # 用正则表达式将连续多个制表符替换为一个制表符
            text = re.sub(r'\t+', '\t', text)
            # 用正则表达式将连续多个空格替换为一个空格
            text = re.sub(r' +', ' ', text)
            # 用正则表达式将多个换行符和空白字符的组合替换为一个换行符
            text = re.sub(r'\n\s*\n+', '\n', text)
            # 用正则表达式将单个换行符和空白字符的组合替换为一个换行符
            text = re.sub(r'\n\s+', '\n', text)
            return text
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
        }
        search = DuckDuckGoSearchResults()
        results=search.run(question)
        time.sleep(2)
        content=[]
        content.append(results)
        links = re.findall(r'link: (https?://[^\s\]]+)', results)
        count=0
        for url in links:
            response = requests.get(url,headers=headers)
            if response.status_code == 200:
                loader = WebBaseLoader(url)
                docs = loader.load()
                for doc in docs:
                    page_text=format_text(doc.page_content)
                    page_text=page_text[:2000]
                    content.append(page_text)
                count+=1
                if count>=3:
                    break
        return content

    def get_response(self, question, chat_history):
        if self.model_option =='ERNIE-Lite-8K':
            self.llm = QianfanChatEndpoint(model='ERNIE-speed-128k')
        else:
            self.llm = ChatGroq(model_name=self.model_option,temperature=0.5,max_tokens=self.model_tokens)
        try:
            judge_result=self.judge_search(question,chat_history)
            if 'yes' in judge_result:
                query=self.generate_based_history_query(question,self.chat_history)
                self.content=self.duckduck_search(query)
                searchBot_template_prompt="""
                    You are a chat assistant. Please answer User Questions to the best of your ability.
                    If the User Questions are asked in Chinese, then your answers must also be in Chinese.
                    You can use the context of the Chat History to help you understand the user's question.
                    If your understanding conflicts with the Search Context, please use the Search Context first to answer the question.
                    If you think the Search Context is not helpful, please answer based on your understanding.
                    If necessary, please output useful links from the Search Context at the end.
                    User Questions: {question}.
                    Chat History:{chat_history}.
                    Search Context:{content}.
                    """
                prompt = ChatPromptTemplate.from_template(searchBot_template_prompt)
                chain = prompt | self.llm | StrOutputParser()
                return chain.stream({
                    "chat_history": chat_history,
                    "question": question,
                    "content": self.content
                })
            else:
                chatBot_template_prompt="""
                            You are a helpful assistant. Answer all questions to the best of your ability.
                            If the User Questions are asked in Chinese, then your answers must also be in Chinese.
                            You can also use Chat History to help you understand User Questions.
                            If you don't know, you can ask for more information, or you can make some appropriate guesses.
                            User Questions: {question}.
                            Chat History:{chat_history}.
                            """
                prompt = ChatPromptTemplate.from_template(chatBot_template_prompt)
                chain = prompt | self.llm | StrOutputParser()
                return chain.stream({
                    "chat_history": chat_history,
                    "question": question,
                })
        except Exception as e:
            return f"当前模型{self.model_option}暂不可用，请在左侧栏选择其他模型。"


def init_params(init_search_message):
    if "search_message" not in st.session_state:
        st.session_state.search_message = [AIMessage(content=init_search_message)]
    if "searchbot" not in st.session_state:
        st.session_state.search_bot = SearchBot()

# 清除聊天记录
def clear(init_search_message):
    st.session_state.search_message = [AIMessage(content=init_search_message)]
    st.session_state.search_bot = SearchBot()


def online_chat_page():
    with st.sidebar:
        # 模型选择
        select_model=st.selectbox("选择模型",options=["百度千帆大模型","谷歌Gemma大模型","Llama3-70b大模型","Llama3-8b大模型","Mixtral大模型"],index=0)
        model_option=model_config.model_ls[select_model]["name"]
        model_tokes=model_config.model_ls[select_model]["tokens"]

        st.button("Clear Chat History", on_click=lambda: clear(init_search_message))
    # 初始化消息
    init_search_message = "您好，我是AI在线聊天机器人，我会根据实时信息来回答您的问题。\
                    此外在我的左侧栏中，您可以更换不同的AI模型。"
    init_params(init_search_message)

    # 输出所有聊天记录
    for message in st.session_state.search_message:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)


    # 输入问题
    question = st.chat_input("输入你的问题")
    if question:
        st.session_state.search_bot.model_option = model_option
        st.session_state.search_bot.model_tokens = model_tokes
        with st.chat_message("Human"):
            st.markdown(question)
            st.session_state.search_message.append(HumanMessage(content=question))
        with st.chat_message("AI"):
            with st.spinner('思考中....'):  
                response =  st.write_stream(st.session_state.search_bot.get_response(question, st.session_state.search_message))
                # response= st.session_state.search_bot.get_response(question, st.session_state.search_message)
            st.session_state.search_bot.chat_history.extend([HumanMessage(content=question), response])
            st.session_state.search_message.append(AIMessage(content=response))
            if st.session_state.search_bot.content:
                with st.expander("来源内容"):
                    st.markdown(st.session_state.search_bot.content)


