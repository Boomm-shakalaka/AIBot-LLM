en_chat_prompt="You are a helpful assistant. Answer all questions to the best of your ability. \
                The provided chat history includes facts about the user you are speaking with: {chat_history}"
cn_chat_prompt="你是一个聊天机器人，你需要根据问题来回答。请你根据问题来作出回应。必要时可以检索聊天记录。\
                如果聊天记录中没有与问题相关的信息，尽你所能回答所有问题，但不要瞎编答案。你回答的语言应该根据问题的语言来决定。"

retrieve_document_prompt="""Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""

qa_system_prompt = """DOCUMENT:{context}
                        QUESTION:{input}
                        Answer the users QUESTION using the DOCUMENT text above.
                        Keep your answer ground in the facts of the DOCUMENT.
                        If the DOCUMENT doesn't contain the facts to answer the QUESTION,just say that you don't know.
                        Your answer language should same as the QUESTION language.
                        """


"""You are an assistant for question-answering tasks. \
                        if the question is in Chinese, you should answer it in Chinese. \
                        You can only use the provided context to answer the question. \
                        Your answer should be as detailed and complete, but don't make up any answers .\
                        If you don't know the answer, just say that you don't know.\
                        context:{context}
                        question:{input}
                        answer:""" 


contextualize_q_system_prompt_zh="""给定一个聊天记录和最新的用户问题，哪一个可能在聊天历史中引用上下文，形成一个独立的问题\
        不用聊天记录也能看懂。不要回答这个问题，如果需要，只需重新制定它，否则就原样返回。""" 


qa_system_prompt_zh ="""
                        你是负责回答问题的助手。使用以下检索到的上下文片段来回答问题。\
                        如果你不知道答案，就说你不知道。 
                        Context: {context} 
                        """
chatBot_template_prompt="""
                        You are a helpful assistant. Answer all questions to the best of your ability.
                        If the User Questions are asked in Chinese, then your answers must also be in Chinese.
                        You can also use Chat History to help you understand User Questions.
                        If you don't know, you can ask for more information, or you can make some appropriate guesses.
                        User Questions: {question}.
                        Chat History:{chat_history}.
                        """

rag_prompt="""
                You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
                Context: {context} 
                Answer:
                """

searchBot_template_prompt_zh="""
                        你是一个有用的助手。请你回答所有问题。
                        当问题是中文时，你也可以用中文回答。
                        当问题是中文以外的语言时，你需要用英文回答。
                        我们已经为你提供了一个搜索结果，当你认为你的答案结合聊天记录，与搜索结果完全不同时，请使用你的答案。
                        当你认为你的答案与搜索结果相似时，请结合搜索结果和你的答案。
                        必要时，你可以查看我们的聊天记录。
                        question: {question}.
                        chat_history:{chat_history}.
                        search_result:{search_result}.
                        """