import asyncio
import re
from bs4 import BeautifulSoup
import requests
from langchain_core.documents import Document
from playwright.sync_api import sync_playwright
import time
from playwright.async_api import async_playwright
from langchain_community.document_loaders import WebBaseLoader
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from langchain_community.tools import DuckDuckGoSearchResults

def format_text(text):
    text = re.sub(r'\t+', '\t', text)# 用正则表达式将连续多个制表符替换为一个制表符
    text = re.sub(r' +', ' ', text)# 用正则表达式将连续多个空格替换为一个空格
    text = re.sub(r'\n\s*\n+', '\n', text)# 用正则表达式将多个换行符和空白字符的组合替换为一个换行符
    text = re.sub(r'\n\s+', '\n', text)# 用正则表达式将单个换行符和空白字符的组合替换为一个换行符
    return text

def google_search_sync(question):
    """
    使用Playwright同步执行的函数，用于爬取指定问题的Google搜索结果页面内容，包括动态div内容和链接。

    Parameters:
    question (str): 要搜索的问题或关键词。

    Returns:
    list: 包含搜索结果的字典列表，每个字典包括主题（h3文本）、描述（span文本）、内容（页面内容）和链接（href）。
    """
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch()
    page = browser.new_page()
    url=f"https://www.google.com/search?q={question}"
    page.goto(url)    
    time.sleep(2)# 等待页面加载
    data = []
    div_elements = page.query_selector_all('div[jscontroller="SC7lYd"]')  #获取搜索页面的div元素
    for div_element in div_elements[:3]:# 获取前两个符合条件的链接
        '''提取链接（href）'''
        link_element = div_element.query_selector('a') # 获取链接元素
        link_href = link_element.get_attribute('href') if link_element else None  # 获取其中的链接
        '''爬取link内容'''
        headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
                }
        loader = WebBaseLoader(url,header_template=headers,verify_ssl=True)
        docs = loader.load()
        content=format_text(docs[0].page_content[:400]) #bs4解析内容
        '''提取 span 内容'''
        span_text = ''.join(span_element.inner_text() for span_element in div_element.query_selector_all('div.kb0PBd.cvP2Ce.A9Y9g')) 
        '''提取 h3 内容'''
        h3_text = div_element.query_selector('h3').inner_text() if div_element.query_selector('h3') else None
        data.append({"Topic": h3_text,"Description": span_text,"Content":content,"href": link_href})
    browser.close()
    return data

async def google_search_async(question):
    """
    使用Playwright异步执行的函数，用于爬取指定问题的Google搜索结果页面内容，包括动态div内容和链接。

    Parameters:
    question (str): 要搜索的问题或关键词。

    Returns:
    list: 包含搜索结果的字典列表，每个字典包括主题（h3文本）、描述（span文本）、内容（页面内容）和链接（href）。
    """
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        url = f"https://www.google.com/search?q={question}"
        await page.goto(url)
        data = []
        div_elements = await page.query_selector_all('div[jscontroller="SC7lYd"]')
        for div_element in div_elements[:4]:  # 获取前两个符合条件的链接
            '''提取链接（href）'''
            link_element = await div_element.query_selector('a')
            link_href = await link_element.get_attribute('href') if link_element else None
            '''爬取 link 内容'''
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
                }
            loader = WebBaseLoader(url,header_template=headers,verify_ssl=True)
            docs = loader.load()
            content=format_text(docs[0].page_content[:400])
            '''提取 span 内容'''
            span_text = ''
            span_elements = await div_element.query_selector_all('div.kb0PBd.cvP2Ce.A9Y9g')
            for span_element in span_elements:
                span_text += await span_element.inner_text()
            '''提取 h3 内容'''
            h3_text = ''
            h3_elements= await div_element.query_selector_all('h3')
            for h3_element in h3_elements:
                h3_text += await h3_element.inner_text() 
            data.append({"Topic": h3_text, "Description": span_text, "Content":content,"href": link_href})
        await browser.close()
        return data

def playwright_crawler_sync(url):
    """
    使用Playwright同步执行的函数，用于爬取指定URL的页面内容和动态div内容和链接。

    Parameters:
    url (str): 要爬取的页面的URL。

    Returns:
    list: 包含页面内容的Document对象列表。
    """
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto(url)
    
    '''获取页面内容'''
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    text_content = soup.get_text()

    '''获取动态div内容和链接'''
    dynamic_divs = page.query_selector_all("div")
    dynamic_links = [a.get_attribute('href') for a in page.query_selector_all("a")]
    
    for div in dynamic_divs:
        text_content += div.inner_text()

    browser.close()
    
    data = [Document(page_content=format_text(text_content))]
    return data

async def playwright_crawler_async(url):
    """
    使用Playwright异步执行的函数，用于爬取指定URL的页面内容和动态div内容和链接。

    Parameters:
    url (str): 要爬取的页面的URL。

    Returns:
    list: 包含页面内容的Document对象列表。
    """
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)

        '''获取页面内容'''
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        text_content = soup.get_text()

        '''获取动态div内容和链接'''
        dynamic_divs = await page.query_selector_all("div")
        dynamic_links = [await a.get_attribute('href') for a in await page.query_selector_all("a")]

        for div in dynamic_divs:
            text_content += await div.inner_text()

        await browser.close()

        data = [Document(page_content=format_text(text_content))]
        return data
    

def selenium_url_crawler(url):
    options = Options()
    options.add_argument('--headless')
    # options.add_argument('--window-size=1920x1080')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    # time.sleep(2) 

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    text_content = soup.get_text()

    dynamic_divs = driver.find_elements(By.CSS_SELECTOR, "div")  # Find all div elements
    dynamic_links = [link.get_attribute('href') for link in driver.find_elements(By.TAG_NAME, 'a')]  # Find all links
    for i in range(len(dynamic_divs)):
        try:
            text_content += dynamic_divs[i].text
        except StaleElementReferenceException:
            dynamic_divs = driver.find_elements(By.CSS_SELECTOR, "div")
            text_content += dynamic_divs[i].text
    driver.quit()
    data = [Document(page_content=format_text(text_content))]
    return data

def duckduck_search(question):
    """
    使用DuckDuckGo搜索引擎爬取指定问题的搜索结果，并获取前几个链接的页面内容。

    Parameters:
    question (str): 要搜索的问题或关键词。

    Returns:
    list: 包含搜索结果的列表，列表中包括搜索结果内容和前几个链接的页面内容。
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
    }
    search = DuckDuckGoSearchResults()
    results = search.run(question)
    time.sleep(2)
    content = []
    content.append(results)
    links = re.findall(r'link: (https?://[^\s\]]+)', results)
    count = 0
    for url in links:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            loader = WebBaseLoader(url)
            docs = loader.load()
            for doc in docs:
                page_text = format_text(doc.page_content)
                page_text = page_text[:2000]
                content.append(page_text)
            count += 1
            if count >= 3:
                break
    return content


if __name__ == '__main__':
    question=''
    '''duckducksearch'''
    # data_dockduck=duckduck_search(question)
    # print(data_dockduck)

    '''selenium'''
    # data_selenium = selenium_url_crawler('https://www.google.com/search?q=墨尔本天气')
    # print(data_selenium)

    '''playwright'''
    # data_playwright = playwright_crawler_sync('https://www.google.com/search?q=墨尔本天气')
    # print(data_playwright)

    '''playwright_async'''
    # loop = asyncio.ProactorEventLoop()
    # data_playwright_async = loop.run_until_complete(playwright_crawler_async('https://www.google.com/search?q=墨尔本天气'))
    # print(data_playwright_async)

    '''google_search_sync'''
    # data_sync = google_search_sync(question)
    # print(data_sync)

    '''google_search_async'''
    loop = asyncio.ProactorEventLoop()
    data_async = loop.run_until_complete(google_search_async(question))
    print(data_async)


    