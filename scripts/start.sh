#!/bin/bash

echo "=== Starting Multi-AI Chat Application ==="

# 检查环境变量文件
if [ ! -f ./backend/.env ]; then
    echo "Error: backend/.env file not found. Please run ./deploy-local.sh first."
    exit 1
fi

# 启动后端
echo "Starting backend..."
cd backend
if [ ! -d "venv" ]; then
    echo "Error: Python virtual environment not found. Please run ./deploy-local.sh first."
    exit 1
fi

source venv/bin/activate
python app.py &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo "Starting frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"
cd ..

# 启动Nginx（可选）
if command -v nginx &> /dev/null; then
    echo "Starting Nginx..."
    sudo nginx -c $(pwd)/nginx/aichat.conf
    echo "Nginx started"
else
    echo "Warning: Nginx not found. Frontend will be available on port 5173"
fi

echo ""
echo "=== Application started successfully! ==="
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:5173"
echo "API: http://localhost:5000/api"
echo ""
echo "To stop the application, press Ctrl+C"

# 等待用户中断
trap "echo 'Stopping application...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait  