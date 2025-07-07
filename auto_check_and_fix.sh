#!/bin/bash

# 一键AI Chat项目全面检测与修复脚本
# 适用于 Ubuntu 服务器

set -e

WORKDIR=$(cd "$(dirname "$0")" && pwd)
cd "$WORKDIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "$YELLOW[INFO]$NC $1"; }
ok() { echo -e "$GREEN[OK]$NC $1"; }
err() { echo -e "$RED[ERR]$NC $1"; }

log "1. 检查nginx服务..."
if systemctl is-active --quiet nginx; then
  ok "nginx正在运行"
else
  err "nginx未运行，尝试启动..."
  systemctl start nginx && ok "nginx已启动" || err "nginx启动失败"
fi

log "2. 检查nginx 80端口监听..."
if ss -tuln | grep -q ':80 '; then
  ok "nginx已监听80端口"
else
  err "nginx未监听80端口，请检查配置"
fi

log "3. 检查后端5000端口监听..."
if ss -tuln | grep -q ':5000 '; then
  ok "后端已监听5000端口"
else
  err "后端未监听5000端口，请检查后端服务"
fi

log "4. 检查前端5173端口监听(仅开发用)..."
if ss -tuln | grep -q ':5173 '; then
  ok "前端开发服务器监听5173端口"
else
  log "前端开发服务器未监听5173端口（生产环境可忽略）"
fi

log "5. 检查nginx首页代理..."
if curl -sI http://localhost/ | grep -q '200 OK'; then
  ok "nginx首页可访问"
else
  err "nginx首页无法访问，请检查静态文件路径"
fi

log "6. 检查WebSocket代理..."
if curl -sI "http://localhost/socket.io/?EIO=4&transport=websocket" | grep -q 'HTTP/1.1 200'; then
  ok "WebSocket代理正常"
else
  err "WebSocket代理异常，请检查nginx配置"
fi

log "7. 检查前端依赖..."
if [ -d frontend ]; then
  cd frontend
  if [ ! -d node_modules ]; then
    log "前端依赖未安装，正在自动安装..."
    npm install && ok "前端依赖安装完成" || err "前端依赖安装失败"
  else
    ok "前端依赖已安装"
  fi
  cd "$WORKDIR"
else
  err "未找到frontend目录"
fi

log "8. 检查数据库连接..."
if command -v psql >/dev/null 2>&1; then
  if psql -h 127.0.0.1 -U postgres -d aichat -c '\q' 2>/dev/null; then
    ok "数据库连接正常"
  else
    err "数据库连接失败，请检查数据库服务和配置"
  fi
else
  err "未检测到psql命令，无法检测数据库"
fi

log "9. 检查AI服务外网连通性..."
for url in "https://api.minimax.chat/v1/text/chatcompletion_v2" "https://api.openai.com/v1/chat/completions"; do
  if curl -s --connect-timeout 5 -I "$url" | grep -q '200\|404\|401'; then
    ok "$url 可访问"
  else
    err "$url 无法访问，可能外网受限"
  fi
done

log "10. 检查后端日志关键报错..."
if [ -f logs/backend.log ]; then
  tail -n 50 logs/backend.log | grep -iE 'error|exception|fail|traceback' && err "后端日志有报错，请排查上方内容" || ok "后端日志无关键报错"
else
  log "未找到logs/backend.log"
fi

log "11. 检查前端日志关键报错..."
if [ -f logs/frontend.log ]; then
  tail -n 50 logs/frontend.log | grep -iE 'error|exception|fail' && err "前端日志有报错，请排查上方内容" || ok "前端日志无关键报错"
else
  log "未找到logs/frontend.log"
fi

echo -e "\n$GREEN[全部检测完成]$NC 如有[ERR]请根据提示修复，或将检测结果发给AI助手协助排查。" 