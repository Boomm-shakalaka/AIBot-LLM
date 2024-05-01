# 设置基础镜像，这里选择Python 3.8
FROM python:3.8.19

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中的工作目录
COPY . /app

# 安装依赖
##这是 pip 安装时的一个选项，用于禁用缓存。当使用 --no-cache-dir 选项时，pip 将不会使用本地缓存，从而确保每次安装都是最新的包。这对于 Docker 镜像的构建是很有用的，因为可以避免缓存导致的问题。
RUN pip install --no-cache-dir -r /app/requirements.txt   

# 暴露端口
EXPOSE 8501

# 运行streamlit应用
CMD ["streamlit", "run", "web_ui.py", "--server.port", "8501"]
