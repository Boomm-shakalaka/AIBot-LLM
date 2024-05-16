from url_crawler import url_to_text
from dotenv import find_dotenv, load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import AIMessage, HumanMessage


def retrieve_data(docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 800,chunk_overlap = 100)
    splits_documents = text_splitter.split_documents(docs)
    embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")
    db = Chroma.from_documents(documents=splits_documents, embedding=embeddings,persist_directory="./chroma_db")
    
def generate_based_history_query(question,chat_history):
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
    rag_chain = PromptTemplate.from_template(based_history_prompt) | llm | StrOutputParser()
    result=rag_chain.invoke(
        {
            "chat_history":chat_history , 
            "question": question
        }
    )
    return result

def qa_retrieval(llm,question,retriever,chat_history):
    qa_system_prompt="""
                    You need to answer User Questions based on Context.
                    If the User Questions are asked in Chinese, then your answers must also be in Chinese.
                    You can also use Chat History to help you understand User Questions.
                    If you don't know the answer, just say that you don't know, don't try to make up an answer.
                    Context: '''{context}'''
                    User Questions: '''{question}'''
                    Chat History: '''{chat_history}'''
                    """

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = PromptTemplate.from_template(qa_system_prompt) | llm | StrOutputParser()

    result=chain.invoke(
        {
            "chat_history":chat_history , 
            "question": question,
            "context": retriever

        }
    )
    return result
    


if __name__=='__main__':
    #初始化
    load_dotenv(find_dotenv())
    chat_history=[]
    llm = ChatGroq(model_name='mixtral-8x7b-32768',temperature=0)
    
    # #生成向量
    # url='https://www.qq.com/'
    # docs,links_ls = url_to_text(url)
    # retrieve_data(docs)

    #读取向量
    db = Chroma(persist_directory="./chroma_db", embedding_function=CohereEmbeddings(model="embed-multilingual-v3.0"))
    
    #生成查询
    question=input('enter question:')
    st='What is Task Decomposition'
    while True:
        query=generate_based_history_query(question,chat_history)
        # retriever=db.max_marginal_relevance_search(query=query, k=10)
        retriever = db.similarity_search_with_score(query=query, k=10)
        # retriever=db.as_retriever(search_type='mmr')
        print("query",query)
        # print("retriever",retriever)
        result=qa_retrieval(llm,question,retriever,chat_history)
        print(result)
        chat_history.extend([HumanMessage(content=question), result])
        question=input('inter question:')

