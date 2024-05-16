import streamlit as st
from streamlit_option_menu import option_menu
from web_pages.chat_page import chat_page
from web_pages.url_page import url_page
from web_pages.pdf_page import pdf_page
from web_pages.online_chat_page import online_chat_page
    
st.set_page_config(
    page_title="AIBot",
    page_icon="🤖",
    layout="wide",
    # initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Boomm-shakalaka/AIBot-LLM',
        'Report a bug': "https://github.com/Boomm-shakalaka/AIBot-LLM/issues",
        'About': f"""欢迎使用!"""
    }
)
pages = {
    "聊天机器人": {
        "icon": "chat", #基于streamlit-component-template-vue 构建，使用 Bootstrap 进行样式设置并使用 bootstrap-icons 中的图标。
        "func": chat_page,
    },
    "在线聊天": {
        "icon": "globe2",
        "func": online_chat_page,
    },
    "URL检索":{
        "icon": "bi-link-45deg",
        "func": url_page,
    },
    # "PDF解析": {
    #     "icon": "bi-filetype-pdf",
    #     "func": pdf_page,
    # },
}


selected_page = option_menu(None,
                        options= list(pages),
                        icons=[pages[x]["icon"] for x in pages],
                        default_index=0,
                        orientation="horizontal")


# with st.sidebar:
#     st.image('img/title.png')

if selected_page in pages.keys():
    pages[selected_page]["func"]()
