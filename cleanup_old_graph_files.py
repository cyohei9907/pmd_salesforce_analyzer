#!/usr/bin/env python
"""
清理旧的entities和relations目录
在确认统一文件正常工作后，使用此脚本清理旧文件
"""
import shutil
from pathlib import Path
import sys

def cleanup_old_files(graphdata_dir='backend/graphdata', confirm=True):
    """删除旧的entities和relations目录"""
    graphdata_path = Path(graphdata_dir)
    
    print("=" * 60)
    print("清理旧的图数据文件")
    print("=" * 60)
    
    # 检查统一文件是否存在
    unified_file = graphdata_path / 'graph_data.json'
    if not unified_file.exists():
        print("❌ 错误: 统一文件 graph_data.json 不存在!")
        print("请先运行 migrate_graph_data.py 进行迁移")
        return False
    
    # 显示统一文件信息
    file_size = unified_file.stat().st_size / 1024  # KB
    print(f"\n✓ 统一文件已存在: {unified_file}")
    print(f"  文件大小: {file_size:.2f} KB")
    
    # 检查要删除的目录
    entities_dir = graphdata_path / 'entities'
    relations_dir = graphdata_path / 'relations'
    
    dirs_to_remove = []
    total_files = 0
    
    if entities_dir.exists():
        entity_count = len(list(entities_dir.glob('*.json')))
        dirs_to_remove.append(('entities', entities_dir, entity_count))
        total_files += entity_count
    
    if relations_dir.exists():
        relation_count = len(list(relations_dir.glob('*.json')))
        dirs_to_remove.append(('relations', relations_dir, relation_count))
        total_files += relation_count
    
    if not dirs_to_remove:
        print("\n✓ 没有需要清理的旧文件")
        return True
    
    print(f"\n准备删除的目录:")
    for name, path, count in dirs_to_remove:
        print(f"  - {name}/: {count} 个文件")
    print(f"\n总计: {total_files} 个文件将被删除")
    
    # 确认删除
    if confirm:
        print("\n⚠️  警告: 此操作不可恢复!")
        response = input("确认删除? (输入 yes 继续): ").strip().lower()
        if response != 'yes':
            print("取消操作")
            return False
    
    # 执行删除
    print("\n开始删除...")
    success_count = 0
    
    for name, path, count in dirs_to_remove:
        try:
            shutil.rmtree(path)
            print(f"  ✓ 删除 {name}/ ({count} 个文件)")
            success_count += 1
        except Exception as e:
            print(f"  ✗ 删除失败 {name}/: {e}")
    
    print("\n" + "=" * 60)
    if success_count == len(dirs_to_remove):
        print("✓ 清理完成!")
        print("=" * 60)
        print("\n当前图数据结构:")
        print("  backend/graphdata/")
        print("    ├── graph_data.json     (统一数据文件)")
        print("    ├── graphs/             (NetworkX图缓存)")
        print("    └── exports/            (导出文件)")
        return True
    else:
        print("⚠️  部分清理失败")
        return False

if __name__ == "__main__":
    # 从命令行参数获取路径，或使用默认路径
    graphdata_dir = sys.argv[1] if len(sys.argv) > 1 else 'backend/graphdata'
    
    # 检查是否跳过确认（用于自动化脚本）
    skip_confirm = '--yes' in sys.argv or '-y' in sys.argv
    
    success = cleanup_old_files(graphdata_dir, confirm=not skip_confirm)
    sys.exit(0 if success else 1)
