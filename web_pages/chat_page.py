import streamlit as st
from config_setting import model_config,prompt_config
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from dotenv import find_dotenv, load_dotenv

class chatbot:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.model_option = None

    def get_response(self,question,chat_history):
        try:
            llm = ChatGroq(model_name=self.model_option,temperature=0)
            prompt = ChatPromptTemplate.from_template(prompt_config.chatBot_template_prompt_zh)
            chain = prompt | llm | StrOutputParser()
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
        model_option = st.selectbox(
            "选择机器人模型:",
            options=list(model_config.models.keys()),
            format_func=lambda x: model_config.models[x]["name"],
            index=0  # Default to mixtral
        )
        st.button("Clear Chat History", on_click=lambda: clear(init_chat_message))
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
        with st.chat_message("Human"):
            st.markdown(question)
            st.session_state.chat_message.append(HumanMessage(content=question))
        with st.chat_message("AI"):
            response = st.write_stream(st.session_state.chat_bot.get_response(question,st.session_state.chat_message))
            st.session_state.chat_message.append(AIMessage(content=response))
