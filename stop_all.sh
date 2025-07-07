#!/bin/bash

# 一键停止AI Chat生产环境服务

# 停止后端（gunicorn）
PIDS=$(pgrep -f "gunicorn.*app:app")
if [ -n "$PIDS" ]; then
  echo "[后端] 停止中..."
  kill $PIDS
  echo "[后端] 已停止。"
else
  echo "[后端] 未在运行。"
fi

echo "所有服务已停止。前端为静态文件由nginx服务，无需单独停止。" 