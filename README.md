# AI聊天系统

一个基于Vue3 + Flask的现代化AI聊天系统，支持多种AI模型集成。

## 🚀 快速开始

### 端口配置
- **后端服务**: 5000端口 (Flask + SocketIO)
- **前端服务**: 5173端口 (Vite开发服务器)

### 一键启动

#### Linux/macOS
```bash
# 给脚本添加执行权限
chmod +x *.sh

# 启动服务
./start.sh

# 或者使用简化版本
./start_simple.sh
```

#### Windows
```bash
# 直接运行批处理文件
start.bat
```

### 手动启动

#### 1. 启动后端
```bash
cd backend
python app.py
```

#### 2. 启动前端
```bash
cd frontend
npm run dev
```

## 📋 系统要求

- Python 3.8+
- Node.js 18+
- PostgreSQL数据库

## 🔧 配置

### 环境变量
在 `backend/config.env` 中配置：
```
DATABASE_URL=postgresql://postgres:123.Wmk123@81.70.190.70:5432/aichat
DEEPSEEK_API_KEY=your_deepseek_key
MINIMAX_API_KEY=your_minimax_key
MINIMAX_GROUP_ID=your_group_id
STEPCHAT_API_KEY=your_stepchat_key
SECRET_KEY=your_secret_key
```

## 🌐 服务地址

- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:5000
- **健康检查**: http://localhost:5000/health

## 🛠️ 管理命令

### 查看状态
```bash
# Linux/macOS
./status.sh

# Windows
status.bat
```

### 停止服务
```bash
# Linux/macOS
./stop.sh

# Windows
stop.bat
```

### 诊断问题
```bash
# Linux/macOS
./diagnose.sh
```

## 📝 日志文件

- **后端日志**: `backend/backend.log`
- **前端日志**: `frontend/frontend.log`

## 🔍 故障排除

### 端口被占用
如果5000或5173端口被占用，脚本会自动尝试释放端口。如果仍有问题：

```bash
# 手动释放端口
# Linux/macOS
sudo lsof -ti:5000 | xargs kill -9
sudo lsof -ti:5173 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /f /pid <PID>
```

### 后端启动失败
1. 检查数据库连接
2. 检查AI服务API密钥
3. 查看后端日志：`tail -f backend/backend.log`

### 前端启动失败
1. 检查Node.js版本
2. 重新安装依赖：`cd frontend && npm install`
3. 查看前端日志：`tail -f frontend/frontend.log`

## 🏗️ 项目结构

```
ai-chat/
├── backend/                 # Flask后端
│   ├── app.py              # 主应用文件
│   ├── ai_services/        # AI服务模块
│   ├── models/             # 数据模型
│   └── requirements.txt    # Python依赖
├── frontend/               # Vue3前端
│   ├── src/                # 源代码
│   ├── package.json        # Node.js依赖
│   └── vite.config.js      # Vite配置
├── start.sh               # Linux启动脚本
├── start.bat              # Windows启动脚本
├── stop.sh                # 停止脚本
├── status.sh              # 状态检查脚本
└── diagnose.sh            # 诊断脚本
```

## 🤖 AI服务

系统支持以下AI模型：
- **DeepSeek**: 深度思考型AI，擅长逻辑分析
- **MiniMax**: 友好对话型AI，擅长日常交流
- **StepChat**: 创意灵感型AI，擅长创新思维

## �� 许可证

MIT License 