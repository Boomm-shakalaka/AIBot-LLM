import re

from bs4 import BeautifulSoup
from langchain_core.documents import Document
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import time
from webdriver_manager.chrome import ChromeDriverManager

def url_to_text(url):
    options = Options()
    options.add_argument('--headless')
    # options.add_argument('--window-size=1920x1080')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    # time.sleep(2)  # Delay to ensure all dynamic content has loaded

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    text_content = soup.get_text()

    dynamic_divs = driver.find_elements(By.CSS_SELECTOR, "div")  # Find all div elements
    dynamic_links = [link.get_attribute('href') for link in driver.find_elements(By.TAG_NAME, 'a')]  # Find all links
    for i in range(len(dynamic_divs)):
        try:
            text_content += dynamic_divs[i].text
        except StaleElementReferenceException:
            # If element is stale, refetch elements and try to access it again
            dynamic_divs = driver.find_elements(By.CSS_SELECTOR, "div")
            text_content += dynamic_divs[i].text
    driver.quit()
    # data = [Document(page_content=format_text(text_content))]
    data = [Document(page_content=format_text(text_content))]

    return data


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

if __name__ == '__main__':
    data_ls=[]
    data_ls = url_to_text('https://edition.cnn.com/')
    # for link in links_ls[5:8]:
    #     new_text,new_links_ls = url_to_text(link)
    #     print(len(new_text[0].page_content))
    #     data_ls.extend(new_text)
    print(data_ls)






