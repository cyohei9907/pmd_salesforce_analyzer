"""
REST API序列化器
"""
from rest_framework import serializers
from .models import Repository, ASTFile


class RepositorySerializer(serializers.ModelSerializer):
    """仓库序列化器"""
    ast_files_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Repository
        fields = [
            'id', 'name', 'url', 'branch', 'local_path', 
            'apex_dir', 'is_active', 'created_at', 'updated_at',
            'ast_files_count'
        ]
        read_only_fields = ['local_path', 'created_at', 'updated_at']
    
    def get_ast_files_count(self, obj):
        """获取AST文件数量"""
        return obj.ast_files.count()


class ASTFileSerializer(serializers.ModelSerializer):
    """AST文件序列化器"""
    repository_name = serializers.CharField(source='repository.name', read_only=True)
    
    class Meta:
        model = ASTFile
        fields = [
            'id', 'repository', 'repository_name', 'filename', 
            'class_name', 'imported_at', 'file_path'
        ]
        read_only_fields = ['imported_at']
