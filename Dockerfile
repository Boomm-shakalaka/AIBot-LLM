# 使用 Ubuntu 22.04 作为基础镜像
FROM ubuntu:22.04

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中的工作目录
COPY . /app

# 安装系统依赖项
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx libpython3-dev

# 安装 Python 3.9
RUN apt-get install -y python3.9 

# 安装 pip
RUN apt-get install -y python3-pip

# 安装 Python 依赖项
RUN pip3 install --no-cache-dir -r requirements.txt

# 安装 Playwright 及其依赖项
RUN playwright install --with-deps chromium 

# 暴露端口
EXPOSE 8501

# 设置环境变量以指定操作系统
ENV OS_TYPE="linux"

# 运行 Streamlit 应用
CMD ["python3", "-m", "streamlit", "run", "web_ui.py", "--server.port", "8501"]

