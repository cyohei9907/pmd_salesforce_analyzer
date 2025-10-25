"""
AST API URL配置
"""
from django.urls import path
from . import views

urlpatterns = [
    # 导入相关
    path('import/file/', views.import_ast_file, name='import_ast_file'),
    path('import/directory/', views.import_ast_directory, name='import_ast_directory'),
    
    # Git仓库相关
    path('git/clone/', views.clone_repository, name='clone_repository'),
    path('git/analyze/', views.analyze_repository, name='analyze_repository'),
    path('git/clone-and-analyze/', views.clone_and_analyze, name='clone_and_analyze'),
    path('git/repositories/', views.list_repositories, name='list_repositories'),
    path('git/repositories/<str:repo_name>/', views.delete_repository, name='delete_repository'),
    
    # 图数据查询
    path('graph/', views.get_graph_data, name='get_graph_data'),
    path('graph/class/<str:class_name>/', views.get_class_graph, name='get_class_graph'),
    path('graph/layout/', views.save_graph_layout, name='save_graph_layout'),
    path('graph/layout/load/', views.load_graph_layout, name='load_graph_layout'),
    
    # 统计和管理
    path('statistics/', views.get_statistics, name='get_statistics'),
    path('files/', views.list_imported_files, name='list_imported_files'),
    path('clear/', views.clear_database, name='clear_database'),
]
