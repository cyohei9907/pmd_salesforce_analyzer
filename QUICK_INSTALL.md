# 快速安装和启动指南

## Windows 快速启动

### 1. 安装Neo4j (使用Docker)
```powershell
# 安装Docker Desktop (如未安装)
# https://www.docker.com/products/docker-desktop

# 启动Neo4j
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
```

### 2. 安装后端依赖
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 配置环境
copy .env.example .env
# 编辑.env，设置密码为: password

# 初始化数据库
python manage.py migrate
```

### 3. 安装前端依赖
```powershell
cd frontend
npm install
```

### 4. 一键启动
```powershell
# 回到根目录
cd ..

# 运行启动脚本
start.bat
```

## 快速测试

### 1. 访问Web界面
浏览器打开: http://localhost:3000

### 2. 导入数据
1. 点击"导入数据"
2. 默认路径已填写: `D:\workspace\project018_pmd\pmd_analyzer\output\ast`
3. 点击"开始导入"
4. 等待导入完成（应该看到9个文件导入成功）

### 3. 查看图
1. 点击"图可视化"
2. 看到类、方法、SOQL、DML的关系图
3. 可以拖拽、缩放、点击节点

### 4. 查看统计
1. 点击"统计信息"
2. 看到：
   - 9个类
   - 31个方法
   - 18个SOQL查询
   - 19个DML操作

## 故障排除

### Neo4j连接失败
```powershell
# 检查Neo4j是否运行
docker ps

# 如果没有运行，启动它
docker start neo4j

# 查看日志
docker logs neo4j
```

### Django启动失败
```powershell
# 检查虚拟环境
cd backend
venv\Scripts\activate
python --version

# 重新安装依赖
pip install -r requirements.txt

# 检查迁移
python manage.py migrate
```

### 前端启动失败
```powershell
# 清理并重新安装
cd frontend
rmdir /s /q node_modules
del package-lock.json
npm install
```

## 验证安装

### 检查后端
访问: http://localhost:8000/api/statistics/

应该返回JSON：
```json
{
  "classes": 0,
  "methods": 0,
  "soqls": 0,
  "dmls": 0
}
```

### 检查前端
访问: http://localhost:3000

应该看到欢迎页面

### 检查Neo4j
访问: http://localhost:7474

- 用户名: neo4j
- 密码: password

## 下一步

1. 导入AST数据
2. 探索图可视化
3. 查看代码统计
4. 尝试清空并重新导入

完成！🎉
