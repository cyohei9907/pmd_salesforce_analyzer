"""
AST API URL配置
"""
from django.urls import path
from . import views

urlpatterns = [
    # 导入相关
    path('import/file/', views.import_ast_file, name='import_ast_file'),
    path('import/directory/', views.import_ast_directory, name='import_ast_directory'),
    
    # Git仓库相关(旧接口,保持兼容)
    path('git/clone/', views.clone_repository, name='clone_repository'),
    path('git/analyze/', views.analyze_repository, name='analyze_repository'),
    path('git/clone-and-analyze/', views.clone_and_analyze, name='clone_and_analyze'),
    path('git/detect-structure/', views.detect_repository_structure, name='detect_repository_structure'),
    path('git/repositories/', views.list_repositories, name='list_repositories'),
    path('git/repositories/<str:repo_name>/', views.delete_repository, name='delete_repository'),
    
    # 进度跟踪
    path('progress/<str:task_id>/', views.get_analysis_progress, name='get_analysis_progress'),
    
    # 新增：多仓库管理API
    path('repositories/', views.manage_repositories, name='manage_repositories'),
    path('repositories/<int:repo_id>/', views.manage_repository_detail, name='manage_repository_detail'),
    path('repositories/switch/', views.switch_active_repository, name='switch_active_repository'),
    path('repositories/clone/', views.clone_and_register_repository, name='clone_and_register_repository'),
    path('repositories/<int:repo_id>/graph/', views.get_repository_graph_data, name='get_repository_graph_data'),
    
    # 图数据查询
    path('graph/', views.get_graph_data, name='get_graph_data'),
    path('graph/class/<str:class_name>/', views.get_class_graph, name='get_class_graph'),
    path('graph/layout/', views.save_graph_layout, name='save_graph_layout'),
    path('graph/layout/load/', views.load_graph_layout, name='load_graph_layout'),
    
    # 源代码查询
    path('source/<str:class_name>/', views.get_source_code, name='get_source_code'),
    
    # 统计和管理
    path('statistics/', views.get_statistics, name='get_statistics'),
    path('files/', views.list_imported_files, name='list_imported_files'),
    path('clear/', views.clear_database, name='clear_database'),
]
