en_chat_prompt="You are a helpful assistant. Answer all questions to the best of your ability. \
                The provided chat history includes facts about the user you are speaking with: {chat_history}"
cn_chat_prompt="你是一个聊天机器人，你需要根据问题来回答。请你根据问题来作出回应。必要时可以检索聊天记录。\
                如果聊天记录中没有与问题相关的信息，尽你所能回答所有问题，但不要瞎编答案。你回答的语言应该根据问题的语言来决定。"

contextualize_q_system_prompt="""Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""
qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
{context}"""
chatBot_template_prompt_zh="""
                        你是一个有用的助手。请你回答所有问题。
                        当问题是中文时，你也可以用中文回答。
                        当问题是中文以外的语言时，你需要用英文回答。
                        必要时，你可以查看我们的聊天记录。
                        如果不知道，你可以要求提供更多信息，或者你可以进行一些适当的猜测。
                        question: {question}.
                        chat_history:{chat_history}.
                        """