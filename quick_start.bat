@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================================
echo    PMD Salesforce Analyzer - 快速启动
echo ================================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"
set "VENV_DIR=%BACKEND_DIR%\venv"

REM 检查虚拟环境
if not exist "%VENV_DIR%" (
    echo ❌ 错误: Python 虚拟环境不存在
    echo    请先运行 setup_environment.bat 安装环境
    pause
    exit /b 1
)

REM 检查 node_modules
if not exist "%FRONTEND_DIR%\node_modules" (
    echo ❌ 错误: 前端依赖未安装
    echo    请先运行 setup_environment.bat 安装环境
    pause
    exit /b 1
)

echo 选择启动模式:
echo.
echo [1] 启动后端服务 (Django)
echo [2] 启动前端服务 (Vue)
echo [3] 同时启动前后端服务
echo [4] 运行环境检查
echo [5] 退出
echo.
set /p "CHOICE=请选择 (1-5): "

if "%CHOICE%"=="1" goto START_BACKEND
if "%CHOICE%"=="2" goto START_FRONTEND
if "%CHOICE%"=="3" goto START_BOTH
if "%CHOICE%"=="4" goto CHECK_ENV
if "%CHOICE%"=="5" goto END
goto INVALID_CHOICE

:START_BACKEND
echo.
echo ================================================================
echo 启动后端服务...
echo ================================================================
echo.
cd /d "%BACKEND_DIR%"
call venv\Scripts\activate.bat
echo 运行 Django 开发服务器...
echo 访问地址: http://localhost:8000
echo.
python manage.py runserver
goto END

:START_FRONTEND
echo.
echo ================================================================
echo 启动前端服务...
echo ================================================================
echo.
cd /d "%FRONTEND_DIR%"
echo 运行 Vite 开发服务器...
echo 访问地址: http://localhost:5173
echo.
call npm run dev
goto END

:START_BOTH
echo.
echo ================================================================
echo 同时启动前后端服务...
echo ================================================================
echo.
echo 正在启动后端服务 (在新窗口)...
start "PMD Backend" cmd /k "cd /d %BACKEND_DIR% && venv\Scripts\activate.bat && python manage.py runserver"
timeout /t 2 >nul

echo 正在启动前端服务 (在新窗口)...
start "PMD Frontend" cmd /k "cd /d %FRONTEND_DIR% && npm run dev"

echo.
echo ✅ 服务已启动
echo.
echo 后端服务: http://localhost:8000
echo 前端服务: http://localhost:5173
echo.
echo 关闭此窗口不会停止服务，请在各自的窗口中使用 Ctrl+C 停止
echo.
pause
goto END

:CHECK_ENV
echo.
echo ================================================================
echo 运行环境检查...
echo ================================================================
echo.
cd /d "%SCRIPT_DIR%"
python check_environment.py
echo.
pause
goto END

:INVALID_CHOICE
echo.
echo ❌ 无效的选择，请重新运行
pause
goto END

:END
