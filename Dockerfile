# 设置基础镜像，这里选择 Python 3.8
FROM python:3.8.19

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中的工作目录
COPY . /app

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt   

# 安装 Node.js 和 npm
RUN curl -fsSL https://deb.nodesource.com/setup_14.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# 安装 npm 依赖和 Playwright 浏览器
RUN npm install && npx playwright install

# 暴露端口
EXPOSE 8501

# 运行 Streamlit 应用
CMD ["streamlit", "run", "web_ui.py", "--server.port", "8501"]
