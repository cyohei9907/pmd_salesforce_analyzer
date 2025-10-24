"""
AST API URL配置
"""
from django.urls import path
from . import views

urlpatterns = [
    # 导入相关
    path('import/file/', views.import_ast_file, name='import_ast_file'),
    path('import/directory/', views.import_ast_directory, name='import_ast_directory'),
    
    # 图数据查询
    path('graph/', views.get_graph_data, name='get_graph_data'),
    path('graph/class/<str:class_name>/', views.get_class_graph, name='get_class_graph'),
    
    # 统计和管理
    path('statistics/', views.get_statistics, name='get_statistics'),
    path('files/', views.list_imported_files, name='list_imported_files'),
    path('clear/', views.clear_database, name='clear_database'),
]
