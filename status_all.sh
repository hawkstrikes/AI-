#!/bin/bash

# 一键查看AI Chat生产环境服务状态

# 检查后端（gunicorn）
PIDS=$(pgrep -f "gunicorn.*app:app")
if [ -n "$PIDS" ]; then
  echo "[后端] 运行中，进程号: $PIDS"
else
  echo "[后端] 未在运行。"
fi

# 检查nginx
if pgrep -x nginx > /dev/null; then
  echo "[nginx] 运行中。"
else
  echo "[nginx] 未在运行。"
fi

# 检查健康接口
if curl -sf http://localhost/api/health > /dev/null; then
  echo "[健康检查] /api/health 正常。"
else
  echo "[健康检查] /api/health 异常！"
fi 