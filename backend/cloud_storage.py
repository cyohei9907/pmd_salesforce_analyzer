"""
Cloud Storage Configuration for GCP
管理Cloud Storage的挂载和数据持久化
"""
import os
from pathlib import Path
from django.conf import settings

# Cloud Storage bucket name (需要在GCP中创建)
BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', 'pmd-salesforce-data')

# 本地数据目录 (在生产环境中会被挂载为Cloud Storage volume)
DATA_DIR = Path('/data')

# 数据子目录
AST_DIR = DATA_DIR / 'ast'
DATABASE_DIR = DATA_DIR / 'database'
GRAPH_DIR = DATA_DIR / 'graph'

# 兼容旧路径的映射
LEGACY_PATHS = {
    'output/ast': AST_DIR,
    'graphdata/exports': GRAPH_DIR / 'exports',
    'graphdata/graphs': GRAPH_DIR / 'graphs',
}


def ensure_directories():
    """确保所有必要的目录存在"""
    directories = [
        AST_DIR,
        DATABASE_DIR,
        GRAPH_DIR,
        GRAPH_DIR / 'exports',
        GRAPH_DIR / 'graphs',
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        os.chmod(directory, 0o755)


def get_data_path(path_type):
    """
    获取数据路径
    
    Args:
        path_type: 'ast', 'database', 'graph', 'graph_exports', 'graph_data'
    
    Returns:
        Path对象
    """
    paths = {
        'ast': AST_DIR,
        'database': DATABASE_DIR,
        'graph': GRAPH_DIR,
        'graph_exports': GRAPH_DIR / 'exports',
        'graph_data': GRAPH_DIR / 'graphs',
    }
    
    return paths.get(path_type, DATA_DIR)


def get_db_path():
    """获取数据库文件路径"""
    return DATABASE_DIR / 'db.sqlite3'


# 初始化目录（在模块导入时执行）
if os.environ.get('USE_CLOUD_STORAGE', 'false').lower() == 'true':
    ensure_directories()
