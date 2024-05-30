import random
import time
from duckduckgo_search import DDGS
from langchain_community.document_loaders import WebBaseLoader
import re
from langchain_groq import ChatGroq
import requests
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_cohere import ChatCohere
from langchain_community.chat_models import QianfanChatEndpoint
from langchain_community.tools import DuckDuckGoSearchResults
from dotenv import find_dotenv, load_dotenv

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

    
def duckduck_search(question):
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
        




def judge_search(question,chat_history,llm):
    prompt_tempate="""
                    Give you a question, you need to judge whether you need real-time information to answer.\n
                    If you think you need more real-time information (It may include today,weather,location,new conceptsnames,non-existent concept etc.) to answer the question better, 
                    you need to output "[search]" with a standalone query. The query can be understood without the Chat History.\n
                    If you can answer the question using the chat history without needing real-time information, just output your answer.\n
                    Do not explain your decision process. 
                    Output format: "[search]: your query" or your answer.
                    User Question: {question}.
                    Chat History: {chat_history}.
                    """
    prompt = PromptTemplate.from_template(prompt_tempate)
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({
        "chat_history": chat_history,
        "question": question,
    })
    return response



def generate_based_history_query(question,chat_history,llm):
        based_history_prompt="""
                Use the following latest User Question to formulate a standalone query.
                The query can be understood without the Chat History.
                The output should just be the sentence sutiable for query. 
                If you feel confused, just output the latest User Question.
                Do not provide any answer.
                User Question: '''{question}'''
                Chat History: '''{chat_history}'''
                query:
        """
        rag_chain = PromptTemplate.from_template(based_history_prompt) | llm | StrOutputParser()
        result=rag_chain.invoke(
            {
                "chat_history":chat_history , 
                "question": question
            }
        )
        return result
    
def chat_response(question,chat_history,llm,content):
    try:
        # chatBot_template_prompt="""
        #                 You are a helpful assistant. Answer all questions to the best of your ability.
        #                 You can also use Chat History to help you understand User Questions.
        #                 You should use the Search Context to help you answer the User Questions.
        #                 If your cognition conflicts with the content in Search Context, please give priority to the content in Search Context.

        #                 If the User Questions are asked in Chinese, then your answers must also be in Chinese.
        #                 User Questions: {question}.
        #                 Chat History:{chat_history}.
        #                 Search Context:{content}.
        #                 """
        chatBot_template_prompt="""
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
        
        prompt = ChatPromptTemplate.from_template(chatBot_template_prompt)
        chain = prompt | llm | StrOutputParser()
        result=chain.invoke({
            "chat_history": chat_history,
            "question": question,
            "content": content
        })
        return result
        # return chain.stream({
        #     "chat_history": chat_history,
        #     "question": question,
        #     "content": content
        # })
    except Exception as e:
        return f"当前模型暂不可用，请稍后尝试。"


if __name__ == "__main__":
    question=input("请输入问题：")
    load_dotenv(find_dotenv())
    chat_history=[]
    while True:
        llm = QianfanChatEndpoint(model='ERNIE-Lite-8K')
        judge_result=judge_search(question,chat_history,llm)
        if '[search]' in judge_result:
            query=judge_result.split(":")[1]
            content=duckduck_search(query)
            llm=ChatGroq(model_name='mixtral-8x7b-32768',temperature=0.1)
            response=chat_response(question,chat_history,llm,content)
        else:
            response=judge_result
        chat_history.extend([HumanMessage(content=question), response])
        question=input("请输入问题：")



