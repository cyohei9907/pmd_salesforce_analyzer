@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================================
echo    PMD Salesforce Analyzer - 一键环境安装脚本
echo ================================================================
echo.

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"
set "VENV_DIR=%BACKEND_DIR%\venv"

echo [1/6] 检查 Python 环境...
echo ----------------------------------------------------------------
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Python，请先安装 Python 3.8 或更高版本
    echo    下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python 已安装: %PYTHON_VERSION%
echo.

echo [2/6] 检查 Node.js 环境...
echo ----------------------------------------------------------------
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Node.js，请先安装 Node.js 16 或更高版本
    echo    下载地址: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=1" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js 已安装: %NODE_VERSION%
echo.

echo [3/6] 创建 Python 虚拟环境...
echo ----------------------------------------------------------------
if exist "%VENV_DIR%" (
    echo ⚠️  虚拟环境已存在: %VENV_DIR%
    set /p "RECREATE=是否重新创建? (y/N): "
    if /i "!RECREATE!"=="y" (
        echo 删除现有虚拟环境...
        rmdir /s /q "%VENV_DIR%"
        echo 创建新的虚拟环境...
        python -m venv "%VENV_DIR%"
        if %errorlevel% neq 0 (
            echo ❌ 创建虚拟环境失败
            pause
            exit /b 1
        )
        echo ✅ 虚拟环境已重新创建
    ) else (
        echo ℹ️  使用现有虚拟环境
    )
) else (
    echo 创建虚拟环境: %VENV_DIR%
    python -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建成功
)
echo.

echo [4/6] 安装 Python 依赖包...
echo ----------------------------------------------------------------
echo 激活虚拟环境...
call "%VENV_DIR%\Scripts\activate.bat"

echo 升级 pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ⚠️  升级 pip 失败，继续使用当前版本
)

echo.
echo 安装依赖包 (从 %BACKEND_DIR%\requirements.txt)...
pip install -r "%BACKEND_DIR%\requirements.txt"
if %errorlevel% neq 0 (
    echo ❌ 安装 Python 依赖包失败
    pause
    exit /b 1
)
echo ✅ Python 依赖包安装成功
echo.

echo [5/6] 安装 Node.js 依赖包...
echo ----------------------------------------------------------------
cd /d "%FRONTEND_DIR%"
if not exist "package.json" (
    echo ❌ 错误: 找不到 package.json 文件
    pause
    exit /b 1
)

echo 检查 npm...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: npm 不可用
    pause
    exit /b 1
)

echo 安装前端依赖包 (可能需要几分钟)...
call npm install
if %errorlevel% neq 0 (
    echo ❌ 安装 Node.js 依赖包失败
    echo.
    echo 提示: 如果遇到网络问题，可以尝试:
    echo   1. 使用淘宝镜像: npm config set registry https://registry.npmmirror.com
    echo   2. 或使用 cnpm: npm install -g cnpm --registry=https://registry.npmmirror.com
    pause
    exit /b 1
)
echo ✅ Node.js 依赖包安装成功
echo.

echo [6/6] 验证安装...
echo ----------------------------------------------------------------
cd /d "%SCRIPT_DIR%"

REM 验证 Python 环境
echo 验证 Python 环境...
call "%VENV_DIR%\Scripts\activate.bat"
python -c "import django; print('  Django:', django.VERSION)" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Django 导入失败
) else (
    echo ✅ Django 可用
)

python -c "import neo4j; print('  Neo4j Driver: 已安装')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Neo4j 驱动导入失败
) else (
    echo ✅ Neo4j 驱动可用
)

echo.
echo 验证 Node.js 环境...
cd /d "%FRONTEND_DIR%"
if exist "node_modules" (
    echo ✅ node_modules 目录存在
) else (
    echo ⚠️  node_modules 目录不存在
)

echo.
echo ================================================================
echo    安装完成！
echo ================================================================
echo.
echo 📁 Python 虚拟环境位置:
echo    %VENV_DIR%
echo.
echo 📁 前端依赖位置:
echo    %FRONTEND_DIR%\node_modules
echo.
echo 🚀 后续步骤:
echo.
echo 1. 启动后端服务:
echo    cd backend
echo    venv\Scripts\activate
echo    python manage.py runserver
echo.
echo 2. 启动前端开发服务器:
echo    cd frontend
echo    npm run dev
echo.
echo 3. 运行环境检查:
echo    python check_environment.py
echo.
echo 💡 提示:
echo    - 后端服务默认运行在: http://localhost:8000
echo    - 前端服务默认运行在: http://localhost:5173
echo    - 需要先启动 Neo4j 数据库才能使用图形功能
echo.
echo ================================================================

cd /d "%SCRIPT_DIR%"
pause
