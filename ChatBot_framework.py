
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import find_dotenv, load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import config_setting.prompt as prompt_config


class Bot:
    def __init__(self,model_option):
        self.name = "ChatBot"
        self.llm=self.load_model(model_option)


    def load_model(self,model_option):
        load_dotenv(find_dotenv())  # Load the .env file.
        llm = ChatGroq(model_name=model_option)
        return llm
    

    #保存最新的n条聊天记录
    # def trim_messages(self,chain_input):
    #     stored_messages = self.chat_history.messages
    #     if len(stored_messages) <= 50:
    #         return False

    #     self.chat_history.clear()

    #     for message in stored_messages[-50:]:
    #         self.chat_history.add_message(message)

    #     return True

    def chat(self,question,demo_ephemeral_chat_history):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    prompt_config.cn_chat_prompt,
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        chain = prompt | self.llm

        chain_with_message_history = RunnableWithMessageHistory(
            chain,
            lambda session_id: demo_ephemeral_chat_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        result=chain_with_message_history.invoke(
            {"input": question},
            {"configurable": {"session_id": "unused"}},
        )
        return result.content





        
if __name__ == "__main__":
    bot=Bot("llama3-8b-8192")
    demo_ephemeral_chat_history = ChatMessageHistory()
    demo_ephemeral_chat_history.add_ai_message("Hello!")
    demo_ephemeral_chat_history.add_user_message("How are you today?")
    demo_ephemeral_chat_history.add_ai_message("Fine thanks!")
    result=bot.chat("What's my name?",demo_ephemeral_chat_history)
    print(result)
    


        