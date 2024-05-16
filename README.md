### 基于LLM大模型的AI机器人
一套基于开源框架、平台的AI语言模型机器人，集成人机对话，信息检索生成，PDF和URL解析对话等功能。

## 工具和平台
Langchain, Streamlit, Oracle Cloud, Groq, Docker

## 文件结构描述
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
│   ├── model_config.py
│   └── prompt_config.py
├── about_page.py
├── chat_page.py
├── Dockerfile
├── pdf_page.py
├── requirements.txt
├── summary_page.py
├── url_page.py
</pre>

## 使用教程
### 本地部署
1. 下载依赖库
    ```bash
    pip install -r requirements.txt
    ```

2. 申请API key
    
    | API Key         | 网址                                            |
    |----------------|-------------------------------------------------|
    | Groq API KEY   | [Groq网页](https://console.groq.com/playground) |
    | COHERE API KEY | [COHERE网页](https://dashboard.cohere.com/)     |

3. 项目根目录建立.env
    ```bash
    GROQ_API_KEY=<Groq-API-KEY>
    COHERE_API_KEY= <COHERE-API-KEY>
    ```
4. 运行
    ```bash
    streamlit run chat_page.py
    ```
### 服务器部署
[wiki链接](https://github.com/Boomm-shakalaka/AIBot-LLM/wiki/Oracle%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%90%AD%E5%BB%BA%E6%95%99%E7%A8%8B)



## 版本更新
v0.0.4.1
1. 新增selenium爬虫，优化网页解析能力
2. 优化urlbot架构
3. 增加url_page参考内容来源
4. 新增headers内容，防止反爬
5. 新增max tokens限制

v0.0.4 (oracle cloud)
1. 使用streamlit_option_menu框架重构界面
2. 新增在线搜索功能，基于duckduckDuckDuckGoSearch
3. 优化异步方法处理搜索功能
4. 新增搜索agent提示词

v0.0.3 (oracle cloud)
1. 优化和完善URLBot检索能力
2. 优化和完善URLPage网页架构
3. 使用Cohere API进行Embedding

v0.0.2.1 (oracle cloud)
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

