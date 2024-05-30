import random
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_community.chat_models import QianfanChatEndpoint
from config_setting import model_config
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import find_dotenv, load_dotenv

class chatbot:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.model_option = None
        self.chat_history = []
        self.model_tokens = None

    def get_response(self,question,chat_history):
        try:
            if self.model_option =='ERNIE-Lite-8K':
                llm = QianfanChatEndpoint(model=self.model_option,temperature=0.7)
            # elif self.model_option == 'gemini-1.5-flash-latest':
            #     model_choice=random.choice(["gemini-1.5-flash-latest",'gemini-1.0-pro-001','gemini-1.5-pro-latest',"gemini-1.0-pro"])
            #     llm = ChatGoogleGenerativeAI(model=model_choice,temperature=0.7)
            else:
                llm = ChatGroq(model_name=self.model_option,temperature=1,max_tokens=self.model_tokens)
            chatBot_template_prompt="""
                        You are a helpful assistant. Answer all questions to the best of your ability.
                        If the User Questions are asked in Chinese, then your answers must also be in Chinese.
                        You can also use Chat History to help you understand User Questions.
                        If you don't know, you can ask for more information, or you can make some appropriate guesses.
                        User Questions: {question}.
                        Chat History:{chat_history}.
                        """
            prompt = ChatPromptTemplate.from_template(chatBot_template_prompt)
            chain = prompt | llm | StrOutputParser()
            # result=chain.invoke({
            #     "chat_history": chat_history,
            #     "question": question,
            # })
            # print(result)
            return chain.stream({
                "chat_history": chat_history,
                "question": question,
            })
        except Exception as e:
            return f"当前模型{self.model_option}暂不可用，请在左侧栏选择其他模型。"
        
def init_params(init_chat_message):
    if "chat_message" not in st.session_state:
        st.session_state.chat_message = [AIMessage(content=init_chat_message)]
    if "chat_bot" not in st.session_state:
        st.session_state.chat_bot = chatbot()
#清除聊天记录
def clear(init_chat_message):
    st.session_state.chat_message = [AIMessage(content=init_chat_message)]
    st.session_state.chat_bot = chatbot()

    
def chat_page():
    with st.sidebar:
        #模型选择
        select_model=st.selectbox("选择模型",options=["百度千帆大模型","谷歌Gemma大模型","Llama3-70b大模型","Llama3-8b大模型","Mixtral大模型"],index=0)
        model_option=model_config.model_ls[select_model]["name"]
        model_tokes=model_config.model_ls[select_model]["tokens"]
        st.button("清除聊天记录", on_click=lambda: clear(init_chat_message))
    #初始化消息
    init_chat_message = "您好，我是AI聊天机器人，我会尽力回答您的问题。\
                    此外在我的左侧栏中，您可以更换不同的AI模型。"
    init_params(init_chat_message)


    #输出所有聊天记录
    for message in st.session_state.chat_message:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)

    #输入问题
    question = st.chat_input("输入你的问题")
    if question:
        st.session_state.chat_bot.model_option = model_option
        st.session_state.chat_bot.model_tokens = model_tokes
        with st.chat_message("Human"):
            st.markdown(question)
            st.session_state.chat_message.append(HumanMessage(content=question))
        with st.chat_message("AI"):
            response = st.write_stream(st.session_state.chat_bot.get_response(question,st.session_state.chat_message))
            st.session_state.chat_bot.chat_history.extend([HumanMessage(content=question), response])
            st.session_state.chat_message.append(AIMessage(content=response))
