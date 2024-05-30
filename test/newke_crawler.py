from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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


if __name__ == '__main__':
    url='https://www.nowcoder.com/'
    options = Options()
    options.add_argument('--window-size=1920x1080')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    # 网页加载等待时间
    time.sleep(3)
    # 找到 输入 用户名 和密码框，并且设置内容
    username = driver.find_element_by_id('jsEmailIpt')
    # 输入账号名，xxx替换为自己的账户名
    username.send_keys('xxx')
    time.sleep(1)
    password = driver.find_element_by_id('jsPasswordIpt')
    #输入密码，xxx替换为自己的密码
    password.send_keys('xxx')
    time.sleep(1)
    # 分析网页，找到登录按钮
    login = driver.find_elements_by_css_selector('div[class=col-input-login] a')[0]
    # 点击按钮
    login.click()
    time.sleep(3)
    # 格式化源代码
    soup = BeautifulSoup(driver.page_source,'lxml')
    # 退出浏览器
    driver.quit()

