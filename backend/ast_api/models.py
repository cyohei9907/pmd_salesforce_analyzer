from django.db import models


class Repository(models.Model):
    """Git仓库管理"""
    name = models.CharField(max_length=255, unique=True, help_text="仓库名称")
    url = models.URLField(max_length=500, help_text="Git仓库URL")
    branch = models.CharField(max_length=100, default='main', help_text="分支名称")
    local_path = models.TextField(help_text="本地克隆路径")
    apex_dir = models.CharField(
        max_length=500, 
        default='force-app/main/default/classes',
        help_text="Apex代码相对目录"
    )
    is_active = models.BooleanField(default=False, help_text="是否为当前活动仓库")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'repositories'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} ({'active' if self.is_active else 'inactive'})"


class ASTFile(models.Model):
    """记录已导入的AST文件"""
    repository = models.ForeignKey(
        Repository, 
        on_delete=models.CASCADE, 
        related_name='ast_files',
        null=True,  # 兼容旧数据
        blank=True
    )
    filename = models.CharField(max_length=255)
    class_name = models.CharField(max_length=255)
    imported_at = models.DateTimeField(auto_now_add=True)
    file_path = models.TextField()
    source_code_path = models.TextField(blank=True, null=True, help_text="源代码文件路径")
    
    class Meta:
        db_table = 'ast_files'
        ordering = ['-imported_at']
        # 同一仓库中文件名唯一
        unique_together = [['repository', 'filename']]
    
    def __str__(self):
        repo_name = self.repository.name if self.repository else "N/A"
        return f"[{repo_name}] {self.class_name} ({self.filename})"
