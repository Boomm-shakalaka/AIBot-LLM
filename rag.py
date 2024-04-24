from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import find_dotenv, load_dotenv


class Chatbot:
    def __init__(self):
        load_dotenv(find_dotenv())  # Load the .env file.
        self.llm = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")





if __name__ == "__main__":
    # chatbot = Chatbot()
    load_dotenv(find_dotenv())  # Load the .env file.
    chat = ChatGroq(temperature=0, model_name="gemma-7b-it")
    system = "You are a helpful assistant."
    human = "{text}"
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    chain = prompt | chat
    result=chain.invoke({"text": "你知道铭传大学吗."})
    print(result)
    
