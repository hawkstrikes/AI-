#!/bin/bash
# 一键部署AI Chat项目脚本，适配Ubuntu服务器
set -e

# 1. 拉取/更新代码
echo "[1/7] 拉取/更新代码..."
git pull || echo "未初始化git仓库，跳过git pull"

# 2. 安装后端依赖
echo "[2/7] 安装后端依赖..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. 数据库自动迁移（Flask-Migrate）
echo "[3/7] 数据库自动迁移..."
if [ ! -d "migrations" ]; then
    flask db init
fi
flask db migrate || echo "无数据库变更"
flask db upgrade

# 4. 启动/重启后端服务（使用gunicorn后台）
echo "[4/7] 启动/重启后端服务..."
if pgrep -f "gunicorn.*app:app" > /dev/null; then
    pkill -f "gunicorn.*app:app"
fi
gunicorn -w 2 -k eventlet -b 0.0.0.0:5000 app:app --daemon
cd ..

# 5. 安装前端依赖并构建
echo "[5/7] 安装前端依赖并构建..."
cd frontend
npm install --force
npm run build
cd ..

# 6. 重载nginx
echo "[6/7] 重载nginx..."
sudo nginx -s reload || sudo systemctl restart nginx

# 7. 健康检查
echo "[7/7] 健康检查..."
curl -f http://localhost/api/health && echo "后端健康检查通过" || echo "后端健康检查失败"

if curl -sI "http://localhost/socket.io/?EIO=4&transport=websocket" | grep -q 'HTTP/1.1 101'; then
    echo "WebSocket健康检查通过"
else
    echo "WebSocket健康检查失败"
fi

echo "部署完成！可访问 http://<你的服务器IP或域名> 体验AI聊天。" 