# 基于LLM大模型的AI机器人 AI-Robot Based on LLM
一款开源的AI语言模型机器人，集成人机对话，信息检索生成，PDF和URL解析对话等功能。该平台优势为全部采用免费开源API，以最低成本实现LLM定制化功能。

An open source AI language model robot that integrates human-machine dialogue, information retrieval generation, PDF and URL parsing and other functions. The advantage of the platform is that all the free open source apis are used to achieve LLM customization functions at the lowest cost.

## 工具和平台 Tools and Platform
Langchain, Streamlit, Oracle Cloud, Groq,Google cloud, Baidu Cloud, Docker

## 展示链接 Demo Link
[Link](http://168.138.28.54:8501)

## 文件结构描述 File Structure Description
<pre>
.
├── ansible-script/        #Automation Orchestration
│   ├── host_vars/
│   │   └── config.yaml #Variable name
|   ├── inventory/
│   │   └── hosts.ini #host name
│   ├── roles/ 
│   │   ├── deploy-docker/tasks    #deploy docker yaml file  
│   └── └── pre-install/tasks   #deploy related environment yaml file 
├── README.md
├── .gitgnore
├── config_setting/
│   ├── model_config.py  #all models
│   └── prompt_config.py  #all prompts
├── test.py   #test cases
├── cralwer_modules.py
├── ui_images
├── web_pages/
│   ├── about_page.py
│   ├── chat_page.py
│   ├── online_chat_page.py
│   ├── pdf_page.py
│   └── url_page.py
├── Dockerfile
├── requirements.txt
├── web_ui.py   # main interface
</pre>


## 功能描述 functional Description

### 爬虫模块 Crawler Modules


*  该模块主要包含三种爬虫方法: [Selenium](https://selenium-python.readthedocs.io/)，[Playwright](https://playwright.dev/python/docs/intro)，[基于Langchain的DuckDuckGo](https://api.python.langchain.com/en/latest/tools/langchain_community.tools.ddg_search.tool.DuckDuckGoSearchResults.html)。

*  实验显示，Playwright的耗时只有Selenium的一半：
    | 模块              | 时间          |
    |-------------------|---------------|
    | selenium_url_crawler   | 27s       |
    | playwright_url_crawler | 11s       |

*  由于Streamlit和Playwright的同步方式会产生冲突，所以应使用异步方法。[参考](https://discuss.streamlit.io/t/using-playwright-with-streamlit/28380/5)


### 对话模块 (基于在线和离线两种方式) Chat Modules (Online and Offline)

1. 离线对话
   - 调用LLM大模型
   - 保留对话记录，便于后续分析与应用

2. 在线对话流程
   - 判断是否需要搜索引擎
     - 如果不需要，直接执行离线对话流程
     - 如果需要，则继续下一步
   - 生成用于搜索的query
     - 调用DuckDuckGo或使用自动化爬虫爬取Google搜索页面内容
     - 基于对话记录和搜索结果，综合分析并回答问题

### 大语言模型模块 Large Language Model Modules

以下是支持的LLM大模型：

| 模型名称                 | tokens  | 开发者   |   平台|
|-------------------------|---------|----------| ----------|   
| ERNIE-Lite-8K           | 8192    | Baidu    | Baidu Cloud    |
| ERNIE-speed-128K        | 128k  | Baidu    | Baidu Cloud     |
| Gemma-7B-IT             | 8192    | Google   | Groq    |
| Gemini-1.5-Flash-Latest | 8192    | Google   | Google Cloud    |
| Llama3-70B-8192         | 8192    | Meta     | Groq    |
| Llama3-8B-8192          | 8192    | Meta     | Groq    |
| Mixtral-8x7B-32768      | 32768   | Mistral  | Groq    |

### URL检索模块 URL Retrieval Modules
 
1. 基于 [Langchain-RAG检索生成方法](https://python.langchain.com/v0.1/docs/get_started/introduction/)。
2. 检索流程:
    1. 输入URL并判断是否正确。
    2. 爬虫URL网页内容，生成向量嵌入（当前使用CohereEmbeddings嵌入API）。
    3. 根据问题检索top_k个相关文档。
    4. 基于文档内容回答问题。

### PDF解析模块 PDF Parsing Modules
1. 基于[Streamlit-PDF-API](https://discuss.streamlit.io/t/display-pdf-in-streamlit/62274)和[Langchain-PDFMinerLoader](https://api.python.langchain.com/en/latest/document_loaders/langchain_community.document_loaders.pdf.PDFMinerLoader.html)
2. 使用流程:
    1. 上传PDF
    2. 解析PDF内容大模型基于prompt总结PDF
    3. 根据问题和PDF内容进行回答

## 使用教程 Tutorial

### 本地部署 Local Deployment
1. 下载依赖库
    ```bash
    pip install -r requirements.txt
    ```

2. 申请API key
    
    | API Key         | 网址                                            |
    |----------------|-------------------------------------------------|
    | Groq API KEY   | [Groq网页](https://console.groq.com/playground) |
    | COHERE API KEY | [COHERE网页](https://dashboard.cohere.com/)     |
    | Gemini API KEY | [谷歌云网页](https://ai.google.dev/) |
    | BaiduQianfan API KEY | [百度智能云网页](https://cloud.baidu.com/) |

3. 项目根目录建立.env
    ```bash
    GROQ_API_KEY= <Groq-API-KEY>
    COHERE_API_KEY= <COHERE-API-KEY>
    GOOGLE_API_KEY= <GOOGLE-API-KEY>
    QIANFAN_AK= <QIANFAN-AK>
    QIANFAN_SK= <QIANFAN-SK>
    ```
4. 运行
    ```bash
    play playwright install
    ```
    ```bash
    streamlit run web_ui.py
    ```
### 服务器部署 Server Deployment
方法一:  Linux环境本地安装和执行Docker
* 服务器拉取github仓库
* 构建镜像

方法二:  Docker Hub拉取和执行镜像
* [Docker Hub链接](https://hub.docker.com/repository/docker/jiyuanc1/aibot/general)

部署教程 
* 服务器部署教程：[wiki链接](https://github.com/Boomm-shakalaka/AIBot-LLM/wiki/Oracle%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%90%AD%E5%BB%BA%E6%95%99%E7%A8%8B)

## Docker构建镜像已知问题 The Known Issues with Building Docker Images 
1. Google-genai打包失败,没有找到该问题原因
    ```bash
    ERROR: Could not find a version that satisfies the requirement langchain-google-genai (from -r requirements.txt (line 11)) (from >versions: none) 
    ERROR: No matching distribution found for langchain-google-genai (from -r requirements.txt (line 11))
    ```
2. 对于windows和linux 不同操作系统，异步方法也不同 [参考](https://stackoverflow.com/questions/67964463/what-are-selectoreventloop-and-proactoreventloop-in-python-asyncio)
    ```python
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop() #windows系统
    else:
        loop = asyncio.SelectorEventLoop()#linux系统
    ```
3. playwright无法直接打包进Docker! 需要基于Ubuntu镜像环境[参考](https://stackoverflow.com/questions/72181737/issue-running-playwright-python-in-docker-container)


## 版本更新 Version Update Records
<details>
<summary>📈 更新记录</summary>

v1.0.1 (oracle)
1. 解决Docker构建镜像问题，解决不同操作系统存在的异步方法
2. 更新Readme

v1.0.0 
1. 优化pdf chat功能中的简历评估功能，增加对话
2. 新增playwright爬虫模块，优化异步调用
3. 新增url chat爬虫模块调用和来源检索选择功能
4. 实现基于playwright在线搜索功能
5. 优化chat history
6. 整合cralwer模块
7. 整合prompt配置内容
8. 页面美化
9. 新增about页面
10. 更新Dockerfile

v0.0.5
1. 新增百度千帆大模型(ERNIE-Lite-8K和ERNIE-Speed-128K免费开放)
2. 新增gemini模型(gemini模型不支持streaming输出，暂未开放)
3. 新增online chat功能，使用duckduck-search进行在线搜索
4. 优化在线搜索调用方式
5. 实现pdf chat功能中的简历评估功能

v0.0.4.1
1. 新增selenium爬虫，优化网页解析能力
2. 优化urlbot架构
3. 增加url_page参考内容来源
4. 新增headers内容，防止反爬
5. 新增max tokens限制
6. Gemma存在输出乱码问题

v0.0.4
1. 使用streamlit_option_menu框架重构界面
2. 新增在线搜索功能，基于duckduckDuckDuckGoSearch
3. 优化异步方法处理搜索功能
4. 新增搜索agent提示词

v0.0.3
1. 优化和完善URLBot检索能力
2. 优化和完善URLPage网页架构
3. 使用Cohere API进行Embedding

v0.0.2.1
1. 优化侧边栏架构
2. 优化chatbot对话能力，优化prompt
3. 优化chatbot对话体验，更改为streaming输出流模式
4. 由于服务器memory限制，暂时关闭URL检索功能
5. 新增docker文件
6. 修改页面布局默认为wide

v0.0.2
1. chatbot新增聊天记录功能
2. 新增prompt_config，优化prompt
3. 构建URLPage网页基本框架
4. 新增URLBot，可以根据URL进行检索
5. 优化URL解析动画

v0.0.1
1. 构建Streamlit网页基本框架
2. 新增chatBot页面，编辑聊天窗口及侧边栏
3. 添加Groq API，新增5种LLM模型
4. 添加大模型于chatBot页面，完成聊天对话基本功能
5. 新增模型选择功能

</details>