import streamlit as st
from dotenv import find_dotenv, load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
models = {
    "gemma-7b-it": {"name": "Gemma-7b-it", "tokens": 8192, "developer": "Google"},
    "llama2-70b-4096": {"name": "LLaMA2-70b-chat", "tokens": 4096, "developer": "Meta"},
    "llama3-70b-8192": {"name": "LLaMA3-70b-8192", "tokens": 8192, "developer": "Meta"},
    "llama3-8b-8192": {"name": "LLaMA3-8b-8192", "tokens": 8192, "developer": "Meta"},
    "mixtral-8x7b-32768": {"name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768, "developer": "Mistral"},
}

def load_model(question,model_option):
    load_dotenv(find_dotenv())  # Load the .env file.
    chat = ChatGroq(temperature=0, model_name=model_option)
    system = "You are a helpful assistant."
    human = "{text}"
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
    chain = prompt | chat
    result=chain.invoke({"text":question })
    return result.content

if __name__ == "__main__":
    #页面绘制
    st.header("ChatBot-AI机器人", divider="rainbow", anchor=False)
    # st.caption("🚀 A streamlit website based by GroqCloud")

    #初始化模型选择
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = None

    # 初始化聊天记录
    if "messages" not in st.session_state:#初始化聊天记录
        st.session_state["messages"] = list()

    with st.sidebar:
        #模型选择
        model_option = st.selectbox(
        "Choose a model:",
        options=list(models.keys()),
        format_func=lambda x: models[x]["name"],
        index=0  # Default to mixtral
        )
        #清除聊天记录
        st.button("Clear Chat History", on_click=lambda: st.session_state.pop("messages", None))
        st.text("Gemma适合中文语境")
        st.text("LLaMA2-70b性能均衡")
        st.text("LLaMA3-70b精准度高")
        st.text("LLaMA3-8b速度快")
        st.text("Mixtral速度快，适合长文本")
    
    st.chat_message("assistant").write("你好，我是基于大模型的AI对话机器人，请输入你想询问的问题")
    # if "messages" not in st.session_state:
        # st.session_state["messages"] = [
        #     {"role": "assistant", "content": "你好，我是基于大模型的AI对话机器人，请输入你想询问的问题"}
        # ]
    #显示对话过程
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    #输入问题
    question = st.chat_input()
    if question:
    # print(question)
        st.session_state.messages.append({"role": "user", "content": question})
        st.chat_message("user").write(question)
        response = load_model(question,model_option)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)

    


  