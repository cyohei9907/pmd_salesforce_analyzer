#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "================================================================"
echo "   PMD Salesforce Analyzer - 一键环境安装脚本"
echo "================================================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "[1/6] 检查 Python 环境..."
echo "----------------------------------------------------------------"
if ! command_exists python3; then
    echo -e "${RED}❌ 错误: 未找到 Python3，请先安装 Python 3.8 或更高版本${NC}"
    echo "   Ubuntu/Debian: sudo apt-get install python3 python3-venv python3-pip"
    echo "   macOS: brew install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo -e "${GREEN}✅ Python 已安装: $PYTHON_VERSION${NC}"
echo ""

echo "[2/6] 检查 Node.js 环境..."
echo "----------------------------------------------------------------"
if ! command_exists node; then
    echo -e "${RED}❌ 错误: 未找到 Node.js，请先安装 Node.js 16 或更高版本${NC}"
    echo "   Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs"
    echo "   macOS: brew install node"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Node.js 已安装: $NODE_VERSION${NC}"
echo ""

echo "[3/6] 创建 Python 虚拟环境..."
echo "----------------------------------------------------------------"
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}⚠️  虚拟环境已存在: $VENV_DIR${NC}"
    read -p "是否重新创建? (y/N): " RECREATE
    if [[ "$RECREATE" =~ ^[Yy]$ ]]; then
        echo "删除现有虚拟环境..."
        rm -rf "$VENV_DIR"
        echo "创建新的虚拟环境..."
        python3 -m venv "$VENV_DIR"
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ 创建虚拟环境失败${NC}"
            exit 1
        fi
        echo -e "${GREEN}✅ 虚拟环境已重新创建${NC}"
    else
        echo -e "${BLUE}ℹ️  使用现有虚拟环境${NC}"
    fi
else
    echo "创建虚拟环境: $VENV_DIR"
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 创建虚拟环境失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ 虚拟环境创建成功${NC}"
fi
echo ""

echo "[4/6] 安装 Python 依赖包..."
echo "----------------------------------------------------------------"
echo "激活虚拟环境..."
source "$VENV_DIR/bin/activate"

echo "升级 pip..."
pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  升级 pip 失败，继续使用当前版本${NC}"
fi

echo ""
echo "安装依赖包 (从 $BACKEND_DIR/requirements.txt)..."
pip install -r "$BACKEND_DIR/requirements.txt"
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 安装 Python 依赖包失败${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 依赖包安装成功${NC}"
echo ""

echo "[5/6] 安装 Node.js 依赖包..."
echo "----------------------------------------------------------------"
cd "$FRONTEND_DIR"
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ 错误: 找不到 package.json 文件${NC}"
    exit 1
fi

echo "检查 npm..."
if ! command_exists npm; then
    echo -e "${RED}❌ 错误: npm 不可用${NC}"
    exit 1
fi

echo "安装前端依赖包 (可能需要几分钟)..."
npm install
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 安装 Node.js 依赖包失败${NC}"
    echo ""
    echo "提示: 如果遇到网络问题，可以尝试:"
    echo "  1. 使用淘宝镜像: npm config set registry https://registry.npmmirror.com"
    echo "  2. 或使用 cnpm: npm install -g cnpm --registry=https://registry.npmmirror.com"
    exit 1
fi
echo -e "${GREEN}✅ Node.js 依赖包安装成功${NC}"
echo ""

echo "[6/6] 验证安装..."
echo "----------------------------------------------------------------"
cd "$SCRIPT_DIR"

# 验证 Python 环境
echo "验证 Python 环境..."
source "$VENV_DIR/bin/activate"
python -c "import django; print('  Django:', django.VERSION)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Django 导入失败${NC}"
else
    echo -e "${GREEN}✅ Django 可用${NC}"
fi

python -c "import neo4j; print('  Neo4j Driver: 已安装')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Neo4j 驱动导入失败${NC}"
else
    echo -e "${GREEN}✅ Neo4j 驱动可用${NC}"
fi

echo ""
echo "验证 Node.js 环境..."
cd "$FRONTEND_DIR"
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✅ node_modules 目录存在${NC}"
else
    echo -e "${YELLOW}⚠️  node_modules 目录不存在${NC}"
fi

echo ""
echo "================================================================"
echo "   安装完成！"
echo "================================================================"
echo ""
echo "📁 Python 虚拟环境位置:"
echo "   $VENV_DIR"
echo ""
echo "📁 前端依赖位置:"
echo "   $FRONTEND_DIR/node_modules"
echo ""
echo "🚀 后续步骤:"
echo ""
echo "1. 启动后端服务:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python manage.py runserver"
echo ""
echo "2. 启动前端开发服务器:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. 运行环境检查:"
echo "   python3 check_environment.py"
echo ""
echo "💡 提示:"
echo "   - 后端服务默认运行在: http://localhost:8000"
echo "   - 前端服务默认运行在: http://localhost:5173"
echo "   - 需要先启动 Neo4j 数据库才能使用图形功能"
echo ""
echo "================================================================"

cd "$SCRIPT_DIR"
