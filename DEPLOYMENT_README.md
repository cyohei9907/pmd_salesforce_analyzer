# Apex AST Graph Viewer

一个用于可视化Salesforce Apex AST（抽象语法树）的Web应用，使用Neo4j图数据库存储和Django + Vue.js构建。

## 🏗️ 架构

### 后端 (Django)
- Django REST Framework - API服务
- Neo4j - 图数据库
- AST解析器 - 解析PMD生成的AST XML

### 前端 (Vue 3)
- Vue 3 + Vite
- Element Plus - UI组件库
- vis-network - 图可视化

## 📋 前提条件

### 必需软件
- Python 3.8+
- Node.js 16+
- Neo4j 4.0+ (图数据库)

## 🚀 快速开始

### 1. 安装Neo4j

#### Windows (使用Docker)
```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

#### 或下载桌面版
访问: https://neo4j.com/download/

### 2. 设置后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑.env文件，设置Neo4j连接信息

# 运行数据库迁移
python manage.py migrate

# 启动Django服务器
python manage.py runserver
```

后端将在 http://localhost:8000 运行

### 3. 设置前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:3000 运行

## 📖 使用指南

### 1. 访问Web界面
打开浏览器访问: http://localhost:3000

### 2. 导入AST数据
1. 进入"导入数据"页面
2. 输入AST文件目录路径（默认: `D:\workspace\project018_pmd\pmd_analyzer\output\ast`）
3. 点击"开始导入"
4. 等待导入完成

### 3. 查看图可视化
1. 进入"图可视化"页面
2. 自动加载并显示图关系
3. 可以：
   - 拖拽节点
   - 缩放视图
   - 点击节点查看详情
   - 适应窗口

### 4. 查看统计信息
1. 进入"统计信息"页面
2. 查看代码统计数据
3. 查看图表分布

## 🔌 API端点

### 导入相关
- `POST /api/import/file/` - 导入单个AST文件
- `POST /api/import/directory/` - 导入目录中的所有AST文件

### 图数据查询
- `GET /api/graph/` - 获取完整图数据
- `GET /api/graph/class/<class_name>/` - 获取特定类的图数据

### 统计和管理
- `GET /api/statistics/` - 获取统计信息
- `GET /api/files/` - 列出已导入的文件
- `DELETE /api/clear/` - 清空数据库

## 📊 数据模型

### 节点类型
- **ApexClass** - Apex类
  - 属性: name, simpleName, public, withSharing, fileName
  
- **Method** - 方法
  - 属性: name, returnType, arity, public, static, constructor
  
- **SOQLQuery** - SOQL查询
  - 属性: query, canonicalQuery, className, methodName
  
- **DMLOperation** - DML操作
  - 属性: type, className, methodName, operationType

### 关系类型
- `HAS_METHOD` - 类拥有方法
- `CONTAINS_SOQL` - 方法包含SOQL查询
- `CONTAINS_DML` - 方法包含DML操作

## 🛠️ 开发

### 后端开发
```bash
cd backend

# 创建新应用
python manage.py startapp <app_name>

# 创建迁移
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

### 前端开发
```bash
cd frontend

# 安装新包
npm install <package-name>

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 📁 项目结构

```
pmd_analyzer/
├── backend/                    # Django后端
│   ├── apex_graph/            # Django项目配置
│   ├── ast_api/               # AST API应用
│   │   ├── ast_parser.py      # AST解析器
│   │   ├── neo4j_service.py   # Neo4j服务
│   │   ├── import_service.py  # 导入服务
│   │   ├── views.py           # API视图
│   │   └── urls.py            # URL配置
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/                   # Vue前端
│   ├── src/
│   │   ├── api/               # API调用
│   │   ├── views/             # 页面组件
│   │   │   ├── Home.vue
│   │   │   ├── GraphView.vue
│   │   │   ├── ImportData.vue
│   │   │   └── Statistics.vue
│   │   ├── router/            # 路由配置
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
│
└── output/
    └── ast/                    # AST文件目录
```

## 🔧 配置

### Neo4j配置
在 `backend/.env` 文件中配置：
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
```

### CORS配置
默认允许所有来源，生产环境请修改 `backend/apex_graph/settings.py`:
```python
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

## 🐛 故障排除

### Neo4j连接失败
1. 确保Neo4j正在运行
2. 检查连接配置是否正确
3. 验证防火墙设置

### 前端无法连接后端
1. 确保Django服务器正在运行
2. 检查CORS配置
3. 检查代理配置 (vite.config.js)

### 导入失败
1. 确保文件路径正确
2. 检查文件格式是否为PMD生成的AST XML
3. 查看Django日志获取详细错误信息

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📧 联系方式

如有问题，请创建Issue。
