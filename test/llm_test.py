import random
from langchain_groq import ChatGroq
from dotenv import find_dotenv, load_dotenv
import time

# llm=ChatGroq(model_name='gemma-7b-it',temperature=1)
# question="宁诺附中老师"
# result=llm.invoke(question)
# print(result)

from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv(find_dotenv())
num=0
while True:
    model=random.choice(["gemini-1.5-flash-latest",'gemini-1.0-pro-001','gemini-1.5-pro-latest',"gemini-1.0-pro"])
    print(model)
    # model_random=["gemini-1.5-flash-latest",'gemini-1.0-pro-001','gemini-1.5-pro-latest',"gemini-1.0-pro"]
    llm = ChatGoogleGenerativeAI(model=model,temperature=1)
    question="你是谁"
    result=llm.invoke(question)
    print(num)
    time.sleep(1)
    num+=1
