import asyncio
from langchain_cohere import CohereEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from playwright.async_api import async_playwright
from datetime import datetime
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://news.10jqka.com.cn/realtimenews.html")
        attempts = 0
        max_attempts = 5
        while attempts < max_attempts:
            try:
                await page.goto("https://news.10jqka.com.cn/realtimenews.html")
                # 等待页面加载完成
                await page.wait_for_selector("ul.newsText.all")
                break
            except Exception as e:
                attempts += 1

        # 模拟点击“加载更多”按钮20次
        for _ in range(20):
            try:
                # 等待“加载更多”按钮可点击
                await page.wait_for_selector("div.downLoadMore")
                await page.click("div.downLoadMore")
                # 等待新的内容加载
                await page.wait_for_timeout(4000)  # 等待2秒，确保内容加载完成
            except Exception as e:
                print(f"加载更多内容时出错: {e}")
                break

        # 获取所有符合条件的<li>元素
        elements = await page.query_selector_all("ul.newsText.all li[class^='stock_']")
        
        text_content =''
        
        # 遍历所有<li>元素，提取时间和链接
        for element in elements:
            # 提取时间
            time_element = await element.query_selector("div.newsTimer")
            time_text = await time_element.inner_text() if time_element else "N/A"
            # 合并当前日期和爬取到的时间
            if time_text != "N/A":
                current_date = datetime.now().strftime("%Y-%m-%d")
                combined_time = f"{current_date}-{time_text}"
            else:
                combined_time = "N/A"
            # 提取链接
            a_element = await element.query_selector("a")
            href = await a_element.get_attribute("href") if a_element else "N/A"
            content = await a_element.inner_text() if a_element else "N/A"
            text_content+=content+'发布时间为:'+combined_time+'。网页源链接:'+href+'\n'
        await browser.close()
        documents = [Document(page_content=text_content)]
        return documents

# def convert_to_documents(news_data):
#     documents = []
#     for i, item in enumerate(news_data):
#         page_content = item["内容"]+'网页源链接:'+item["网页链接"]+'。发布时间:'+item["发布时间"]
#         documents.append(Document(page_content=page_content))
#     return documents

def retrieve_text(docs):
    # Split,Emdedding the document
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000,chunk_overlap = 200)
    splits = text_splitter.split_documents(docs)
    embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")
    current_date = datetime.now().strftime("%Y%m%d%H%M")
    collection_name = "vectorstore_"+current_date
    db_name = "./chroma_db_"+current_date
    Chroma.from_documents(collection_name=collection_name,documents=splits, embedding=embeddings,persist_directory=db_name)

async def cjyw_run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://news.10jqka.com.cn/today_list/")
        attempts = 0
        max_attempts = 5
        while attempts < max_attempts:
            try:
                await page.goto("https://news.10jqka.com.cn/today_list/")
                # 等待页面加载完成
                await page.wait_for_selector("ul.newsText.all")
                break
            except Exception as e:
                attempts += 1


    
if __name__ == '__main__':
    '''同花顺7*24小时新闻爬取'''
    # documents = asyncio.run(run())
    # print(documents)
    # # docs=convert_to_documents(news_data)
    # retrieve_text(documents)
    '''同花顺分板块爬取'''
    cjyw_docs = asyncio.run(cjyw_run()) #财经要闻