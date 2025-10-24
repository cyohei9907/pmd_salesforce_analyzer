#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "================================================================"
echo "   PMD Salesforce Analyzer - 快速启动"
echo "================================================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"

# 检查虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}❌ 错误: Python 虚拟环境不存在${NC}"
    echo "   请先运行 ./setup_environment.sh 安装环境"
    exit 1
fi

# 检查 node_modules
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${RED}❌ 错误: 前端依赖未安装${NC}"
    echo "   请先运行 ./setup_environment.sh 安装环境"
    exit 1
fi

echo "选择启动模式:"
echo ""
echo "[1] 启动后端服务 (Django)"
echo "[2] 启动前端服务 (Vue)"
echo "[3] 同时启动前后端服务"
echo "[4] 运行环境检查"
echo "[5] 退出"
echo ""
read -p "请选择 (1-5): " CHOICE

case $CHOICE in
    1)
        echo ""
        echo "================================================================"
        echo "启动后端服务..."
        echo "================================================================"
        echo ""
        cd "$BACKEND_DIR"
        source venv/bin/activate
        echo "运行 Django 开发服务器..."
        echo -e "${GREEN}访问地址: http://localhost:8000${NC}"
        echo ""
        python manage.py runserver
        ;;
    2)
        echo ""
        echo "================================================================"
        echo "启动前端服务..."
        echo "================================================================"
        echo ""
        cd "$FRONTEND_DIR"
        echo "运行 Vite 开发服务器..."
        echo -e "${GREEN}访问地址: http://localhost:5173${NC}"
        echo ""
        npm run dev
        ;;
    3)
        echo ""
        echo "================================================================"
        echo "同时启动前后端服务..."
        echo "================================================================"
        echo ""
        
        # 检查是否有 tmux
        if command -v tmux >/dev/null 2>&1; then
            echo "使用 tmux 启动服务..."
            
            # 创建新的 tmux 会话
            tmux new-session -d -s pmd_analyzer
            
            # 后端窗口
            tmux send-keys -t pmd_analyzer "cd $BACKEND_DIR && source venv/bin/activate && python manage.py runserver" C-m
            
            # 创建新窗口用于前端
            tmux new-window -t pmd_analyzer
            tmux send-keys -t pmd_analyzer "cd $FRONTEND_DIR && npm run dev" C-m
            
            echo -e "${GREEN}✅ 服务已在 tmux 会话中启动${NC}"
            echo ""
            echo "后端服务: http://localhost:8000"
            echo "前端服务: http://localhost:5173"
            echo ""
            echo "使用以下命令管理:"
            echo "  查看服务: tmux attach -t pmd_analyzer"
            echo "  切换窗口: Ctrl+b 然后按数字键"
            echo "  停止服务: tmux kill-session -t pmd_analyzer"
            
        else
            echo "正在启动后端服务 (后台)..."
            cd "$BACKEND_DIR"
            source venv/bin/activate
            python manage.py runserver > backend.log 2>&1 &
            BACKEND_PID=$!
            sleep 2
            
            echo "正在启动前端服务 (后台)..."
            cd "$FRONTEND_DIR"
            npm run dev > frontend.log 2>&1 &
            FRONTEND_PID=$!
            
            echo ""
            echo -e "${GREEN}✅ 服务已启动${NC}"
            echo ""
            echo "后端服务: http://localhost:8000 (PID: $BACKEND_PID)"
            echo "前端服务: http://localhost:5173 (PID: $FRONTEND_PID)"
            echo ""
            echo "日志文件:"
            echo "  后端: $BACKEND_DIR/backend.log"
            echo "  前端: $FRONTEND_DIR/frontend.log"
            echo ""
            echo "停止服务:"
            echo "  kill $BACKEND_PID $FRONTEND_PID"
            echo ""
            
            # 保存 PID 到文件
            echo "$BACKEND_PID" > "$SCRIPT_DIR/.backend.pid"
            echo "$FRONTEND_PID" > "$SCRIPT_DIR/.frontend.pid"
            
            echo "提示: 安装 tmux 可以获得更好的体验"
            echo "  Ubuntu/Debian: sudo apt-get install tmux"
            echo "  macOS: brew install tmux"
        fi
        ;;
    4)
        echo ""
        echo "================================================================"
        echo "运行环境检查..."
        echo "================================================================"
        echo ""
        cd "$SCRIPT_DIR"
        python3 check_environment.py
        echo ""
        ;;
    5)
        echo "退出"
        exit 0
        ;;
    *)
        echo ""
        echo -e "${RED}❌ 无效的选择${NC}"
        exit 1
        ;;
esac
