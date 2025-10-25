#!/usr/bin/env python
"""
将分散的entities和relations文件合并到一个统一的JSON文件中
"""
import json
from pathlib import Path
from datetime import datetime
import sys

def migrate_to_unified_file(graphdata_dir='backend/graphdata'):
    """合并所有实体和关系文件到一个统一文件"""
    graphdata_path = Path(graphdata_dir)
    
    print("=" * 60)
    print("开始迁移图数据到统一文件")
    print("=" * 60)
    
    # 初始化数据结构
    unified_data = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'migration_version': '1.0',
            'total_entities': 0,
            'total_relations': 0
        },
        'entities': {},
        'relations': []
    }
    
    # 1. 读取所有实体文件
    entities_dir = graphdata_path / 'entities'
    if entities_dir.exists():
        print(f"\n正在读取实体文件...")
        entity_files = list(entities_dir.glob('*.json'))
        print(f"找到 {len(entity_files)} 个实体文件")
        
        for entity_file in entity_files:
            try:
                with open(entity_file, 'r', encoding='utf-8') as f:
                    entity_data = json.load(f)
                    node_id = entity_data.get('node_id')
                    if node_id:
                        unified_data['entities'][node_id] = entity_data
                        print(f"  ✓ {entity_file.name}")
            except Exception as e:
                print(f"  ✗ 失败: {entity_file.name} - {e}")
        
        unified_data['metadata']['total_entities'] = len(unified_data['entities'])
        print(f"成功读取 {len(unified_data['entities'])} 个实体")
    else:
        print("未找到entities目录")
    
    # 2. 读取所有关系文件
    relations_dir = graphdata_path / 'relations'
    if relations_dir.exists():
        print(f"\n正在读取关系文件...")
        relation_files = list(relations_dir.glob('*.json'))
        print(f"找到 {len(relation_files)} 个关系文件")
        
        for relation_file in relation_files:
            try:
                with open(relation_file, 'r', encoding='utf-8') as f:
                    relation_data = json.load(f)
                    # 确保关系数据包含必要字段
                    if 'from' in relation_data or 'from_node' in relation_data:
                        # 标准化字段名
                        normalized_relation = {
                            'from': relation_data.get('from') or relation_data.get('from_node'),
                            'to': relation_data.get('to') or relation_data.get('to_node'),
                            'type': relation_data.get('type'),
                            'properties': relation_data.get('properties', {})
                        }
                        unified_data['relations'].append(normalized_relation)
                        print(f"  ✓ {relation_file.name}")
            except Exception as e:
                print(f"  ✗ 失败: {relation_file.name} - {e}")
        
        unified_data['metadata']['total_relations'] = len(unified_data['relations'])
        print(f"成功读取 {len(unified_data['relations'])} 个关系")
    else:
        print("未找到relations目录")
    
    # 3. 保存到统一文件
    unified_file = graphdata_path / 'graph_data.json'
    print(f"\n正在保存到统一文件: {unified_file}")
    
    try:
        with open(unified_file, 'w', encoding='utf-8') as f:
            json.dump(unified_data, f, indent=2, ensure_ascii=False)
        
        file_size = unified_file.stat().st_size / 1024  # KB
        print(f"✓ 成功保存! 文件大小: {file_size:.2f} KB")
    except Exception as e:
        print(f"✗ 保存失败: {e}")
        return False
    
    # 4. 显示统计信息
    print("\n" + "=" * 60)
    print("迁移完成统计:")
    print("=" * 60)
    print(f"总实体数: {unified_data['metadata']['total_entities']}")
    print(f"总关系数: {unified_data['metadata']['total_relations']}")
    
    # 按类型统计实体
    entity_types = {}
    for entity in unified_data['entities'].values():
        entity_type = entity.get('attributes', {}).get('type', 'Unknown')
        entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
    
    print("\n实体类型分布:")
    for entity_type, count in sorted(entity_types.items()):
        print(f"  {entity_type}: {count}")
    
    # 按类型统计关系
    relation_types = {}
    for relation in unified_data['relations']:
        rel_type = relation.get('type', 'Unknown')
        relation_types[rel_type] = relation_types.get(rel_type, 0) + 1
    
    print("\n关系类型分布:")
    for rel_type, count in sorted(relation_types.items()):
        print(f"  {rel_type}: {count}")
    
    print("\n" + "=" * 60)
    print("迁移完成!")
    print("=" * 60)
    print(f"\n统一数据文件: {unified_file}")
    print("\n提示:")
    print("- 旧的entities和relations目录已不再使用")
    print("- 可以选择删除或保留作为备份")
    print("- 新系统将使用 graph_data.json 文件")
    
    return True

if __name__ == "__main__":
    # 从命令行参数获取路径，或使用默认路径
    graphdata_dir = sys.argv[1] if len(sys.argv) > 1 else 'backend/graphdata'
    
    success = migrate_to_unified_file(graphdata_dir)
    sys.exit(0 if success else 1)
