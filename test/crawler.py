
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


key = '唐梧迁'


driver.get(f'https://www.google.com/search?q={key}')
time.sleep(2)


dynamic_divs = driver.find_elements(By.CSS_SELECTOR, "#rso > div:nth-child(4) > div:nth-child(1)")
print(dynamic_divs)
# for i in range(len(dynamic_divs)):
#     try:
#         print(dynamic_divs[i].text)
#     except StaleElementReferenceException:
#         dynamic_divs = driver.find_elements(By.CSS_SELECTOR, "#rso > div:nth-child(4) > div:nth-child(1)")
#         print(dynamic_divs[i].text)

driver.quit()


