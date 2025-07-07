# 使用Python 3.11官方镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir \
        eventlet==0.33.3 \
        psycopg2-binary==2.9.7 \
        gunicorn==21.2.0 \
        redis==4.6.0 \
        prometheus-client==0.17.1

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p /app/logs

# 创建非root用户
RUN groupadd -r aichat && useradd -r -g aichat aichat
RUN chown -R aichat:aichat /app
USER aichat

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 启动命令
CMD ["python", "app.py"] 