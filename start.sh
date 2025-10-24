#!/bin/bash

echo "========================================"
echo "Apex AST Graph Viewer - 启动脚本"
echo "========================================"
echo

echo "[1/3] 启动Neo4j..."
echo "请确保Neo4j已安装并配置"
echo "如果使用Docker: docker start neo4j"
echo

echo "[2/3] 启动Django后端..."
cd backend
source venv/bin/activate
python manage.py runserver &
BACKEND_PID=$!
echo "后端服务: http://localhost:8000"
echo "PID: $BACKEND_PID"
echo

sleep 3

echo "[3/3] 启动Vue前端..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "前端服务: http://localhost:3000"
echo "PID: $FRONTEND_PID"
echo

echo "========================================"
echo "启动完成！"
echo "========================================"
echo
echo "请在浏览器中访问: http://localhost:3000"
echo
echo "按Ctrl+C停止所有服务"

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
