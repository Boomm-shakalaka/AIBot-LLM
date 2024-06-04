import streamlit as st
def about_page():
    st.title("📄 AI Robot平台介绍")
    st.subheader("",divider="rainbow")
    st.markdown(
        """
        ### 欢迎来到AI Robot平台！

        欢迎使用AI Robot平台！这是一款开源的AI语言模型机器人，集成了人机对话、信息检索生成、PDF和URL解析对话等功能。

        ### 平台优势

        * 全部采用免费开源API
        * 以最低成本实现LLM定制化功能

        ### 平台框架与技术

        * 基于Streamlit和Langchain框架构建
        * 结合大模型API，如Llamas、Qianwen、Mistrial等，实现多种功能。

        ### 支持功能与语言

        * 支持多种语言，包括中文、英文、日文等
        * 支持对话、检索、解析等多种功能。

        ### 功能概览

        * 聊天机器人
        * 在线聊天
        * URL检索
        * PDF解析

        ### 相关技术参考

        * [Selenium](https://selenium-python.readthedocs.io/)
        * [Playwright](https://playwright.dev/python/docs/intro)
        * [基于Langchain的DuckDuckGo](https://api.python.langchain.com/en/latest/tools/langchain_community.tools.ddg_search.tool.DuckDuckGoSearchResults.html)
        * [Rag-Langchain](https://python.langchain.com/v0.1/docs/get_started/introduction/)
        * [Streamlit文档](https://docs.streamlit.io/)
        * [Bootstrap官网](https://getbootstrap.com/)

        作者：Boomm-shakalaka  
        版本：1.0  
        Github项目地址：[AIBot-LLM](https://github.com/Boomm-shakalaka/AIBot-LLM)  
        '报告Bug'：[Github Issues](https://github.com/Boomm-shakalaka/AIBot-LLM/issues)
        """
    )
            
    
