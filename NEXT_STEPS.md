# ✅ 已完成的步骤

## 1. ✅ 后端依赖安装完成
- Django 4.2.7
- Django REST Framework 3.14.0
- Neo4j driver 5.14.1
- 所有其他依赖包

## 2. ✅ 数据库迁移完成
- Django数据库已初始化
- 所有表已创建

## 3. ✅ 前端依赖安装完成
- Vue 3
- Element Plus
- vis-network
- 所有其他依赖包

---

# 🚀 接下来需要做的（3个步骤）

## 步骤1: 启动Docker Desktop和Neo4j

### 1.1 启动Docker Desktop
1. 在Windows开始菜单中找到并启动 **Docker Desktop**
2. 等待Docker完全启动（托盘图标不再显示动画）
3. 大约需要30秒到1分钟

### 1.2 启动Neo4j容器
在PowerShell中运行：
```powershell
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
```

### 1.3 验证Neo4j启动
```powershell
# 检查容器状态
docker ps

# 应该看到neo4j容器正在运行
# 状态应该是 "Up X seconds"
```

### 1.4 访问Neo4j浏览器（可选）
浏览器打开: http://localhost:7474
- 用户名: `neo4j`
- 密码: `password`

---

## 步骤2: 启动Django后端

在一个**新的PowerShell终端**中运行：

```powershell
cd D:\workspace\project018_pmd\pmd_analyzer\backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

看到以下输出表示成功：
```
Django version 4.2.7, using settings 'apex_graph.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### 验证后端API
浏览器访问: http://localhost:8000/api/statistics/

应该看到JSON响应：
```json
{
  "classes": 0,
  "methods": 0,
  "soqls": 0,
  "dmls": 0
}
```

---

## 步骤3: 启动Vue前端

在**另一个新的PowerShell终端**中运行：

```powershell
cd D:\workspace\project018_pmd\pmd_analyzer\frontend
npm run dev
```

看到以下输出表示成功：
```
VITE v5.0.0  ready in XXX ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

### 访问Web界面
浏览器打开: http://localhost:3000

你应该看到：
- 侧边栏菜单（首页、图可视化、导入数据、统计信息）
- 欢迎页面

---

# 🎯 使用系统

## 1. 导入AST数据

1. 点击侧边栏的 **"导入数据"**
2. 在"批量导入"标签页
3. 路径已自动填写：`D:\workspace\project018_pmd\pmd_analyzer\output\ast`
4. 点击 **"开始导入"** 按钮
5. 等待导入完成（应该看到9个文件成功导入）

## 2. 查看图可视化

1. 点击侧边栏的 **"图可视化"**
2. 自动加载并显示图
3. 你可以：
   - 🖱️ **拖拽节点** 重新排列
   - 🔍 **滚轮缩放** 
   - 🖐️ **拖动背景** 平移视图
   - 🖱️ **点击节点** 查看详细信息
   - 📐 **点击"适应窗口"** 查看完整图

### 节点颜色说明
- 🔵 蓝色 = ApexClass（类）
- 🟢 绿色 = Method（方法）
- 🟠 橙色 = SOQLQuery（SOQL查询）
- 🔴 红色 = DMLOperation（DML操作）

## 3. 查看统计信息

1. 点击侧边栏的 **"统计信息"**
2. 看到以下统计：
   - 类数量: 9
   - 方法数量: 31
   - SOQL查询: 18
   - DML操作: 19

---

# 🆘 故障排除

## 问题1: Neo4j连接失败

**症状**: 导入数据时提示连接错误

**解决方法**:
```powershell
# 检查Neo4j是否运行
docker ps

# 如果没有看到neo4j，启动它
docker start neo4j

# 如果容器不存在，重新创建
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
```

## 问题2: 后端端口已被占用

**症状**: `Error: That port is already in use`

**解决方法**:
```powershell
# 使用不同端口启动
python manage.py runserver 8001

# 然后修改前端配置
# frontend/vite.config.js 中的 target 改为 'http://localhost:8001'
```

## 问题3: 前端端口已被占用

**症状**: Port 3000 is already in use

**解决方法**:
```powershell
# 前端会自动尝试下一个可用端口 (3001, 3002等)
# 直接按提示访问新端口即可
```

---

# 📊 预期结果

完成所有步骤后，你应该能够：

✅ 看到9个Apex类的完整关系图
✅ 查看31个方法的定义
✅ 看到18个SOQL查询的使用位置
✅ 看到19个DML操作的调用关系
✅ 交互式探索代码结构

---

# 🎉 完成！

系统现在完全可用了！你可以：
- 🔍 探索Apex代码的AST结构
- 📊 分析代码复杂度和依赖关系
- 🔗 追踪SOQL和DML的使用
- 📈 可视化代码架构

有任何问题随时告诉我！
