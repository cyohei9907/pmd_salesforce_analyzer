@echo off
echo ========================================
echo Apex AST Graph Viewer - 启动脚本
echo ========================================
echo.

echo [1/3] 启动Neo4j...
echo 请确保Neo4j已安装并配置
echo 如果使用Docker: docker start neo4j
echo.

echo [2/3] 启动Django后端...
cd backend
start cmd /k "venv\Scripts\activate && python manage.py runserver"
echo 后端服务: http://localhost:8000
echo.

timeout /t 3

echo [3/3] 启动Vue前端...
cd ..\frontend
start cmd /k "npm run dev"
echo 前端服务: http://localhost:3000
echo.

echo ========================================
echo 启动完成！
echo ========================================
echo.
echo 请在浏览器中访问: http://localhost:3000
echo.
pause
