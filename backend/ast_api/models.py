from django.db import models


class ASTFile(models.Model):
    """记录已导入的AST文件"""
    filename = models.CharField(max_length=255, unique=True)
    class_name = models.CharField(max_length=255)
    imported_at = models.DateTimeField(auto_now_add=True)
    file_path = models.TextField()
    
    class Meta:
        db_table = 'ast_files'
        ordering = ['-imported_at']
    
    def __str__(self):
        return f"{self.class_name} ({self.filename})"
