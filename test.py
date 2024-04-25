
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma



def parse_data(url):
    loader = WebBaseLoader(url)
    docs = loader.load()
    return docs


def retrieve_data(docs):
    # Split,Emdedding the document
    text_splitter = RecursiveCharacterTextSplitter()
    splits = text_splitter.split_documents(docs)
    bge_embeddings = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-m3")
    vectorstore = Chroma.from_documents(documents=splits, embedding=bge_embeddings)
    retriever = vectorstore.as_retriever()
    return retriever



docs=parse_data("https://www.unimelb.edu.au")
result=retrieve_data(docs)
