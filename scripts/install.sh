#!/bin/bash

echo "=== Installing Multi-AI Chat Dependencies ==="

# 更新包管理器
echo "Updating package manager..."
sudo apt update

# 安装Python环境
echo "Installing Python environment..."
sudo apt install -y python3 python3-venv python3-pip

# 安装Node.js
echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安装PostgreSQL
echo "Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

# 安装Redis（可选）
echo "Installing Redis..."
sudo apt install -y redis-server

# 安装Nginx（可选）
echo "Installing Nginx..."
sudo apt install -y nginx

# 创建Python虚拟环境
echo "Creating Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# 安装前端依赖
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# 创建数据库用户和数据库
echo "Setting up database..."
sudo -u postgres psql -c "CREATE USER aichat_user WITH PASSWORD '123.Wmk123';"
sudo -u postgres psql -c "CREATE DATABASE aichat OWNER aichat_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE aichat TO aichat_user;"

# 启动Redis服务
echo "Starting Redis service..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

echo ""
echo "=== Installation completed successfully! ==="
echo "Next steps:"
echo "1. Copy backend/env.example to backend/.env and configure your API keys"
echo "2. Copy frontend/env.example to frontend/.env and configure API URL"
echo "3. Run ./scripts/start.sh to start the application"