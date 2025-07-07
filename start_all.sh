#!/bin/bash
# 一键启动AI Chat生产环境服务
set -e

WORKDIR=$(cd "$(dirname "$0")" && pwd)
cd "$WORKDIR"
LOGDIR="$WORKDIR/logs"
mkdir -p "$LOGDIR"

# 启动后端（gunicorn+eventlet）
echo "[后端] 启动中..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 检查 requirements.txt 是否还包含 openai
if grep -q "^openai" requirements.txt; then
  echo "警告：requirements.txt 仍包含 openai，请手动移除以避免无用依赖。"
fi

if [ ! -d "migrations" ]; then
  flask db init
fi
flask db migrate || echo "无数据库变更"
flask db upgrade
if pgrep -f "gunicorn.*app:app" > /dev/null; then
  pkill -f "gunicorn.*app:app"
fi
gunicorn -w 2 -k eventlet -b 0.0.0.0:5000 app:app --daemon --log-file "$LOGDIR/gunicorn.log"
cd "$WORKDIR"

# 构建前端
cd frontend
echo "[前端] 构建中..."
npm install --force
npm run build
cd "$WORKDIR"

# 重载nginx
echo "[nginx] 重载..."
sudo nginx -s reload || sudo systemctl restart nginx

echo "所有服务已启动。后端日志: $LOGDIR/gunicorn.log"
echo "注意：如调用 stepchat、deepseek、step_star 相关 AI 服务，未补充实现时会抛出 NotImplementedError。" 