"""
迁移脚本：将 graph_data.json 拆分为 entities.json 和 relations.json
"""
import json
from pathlib import Path
from datetime import datetime

def migrate_graph_data():
    """将统一的 graph_data.json 拆分为独立的实体和关系文件"""
    
    graphdata_dir = Path('backend/graphdata')
    unified_file = graphdata_dir / 'graph_data.json'
    entities_file = graphdata_dir / 'entities.json'
    relations_file = graphdata_dir / 'relations.json'
    
    # 检查统一文件是否存在
    if not unified_file.exists():
        print(f"❌ 未找到 {unified_file}")
        return
    
    print(f"📖 读取统一文件: {unified_file}")
    with open(unified_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 提取实体和关系
    entities = data.get('entities', {})
    relations = data.get('relations', [])
    
    print(f"✅ 找到 {len(entities)} 个实体")
    print(f"✅ 找到 {len(relations)} 个关系")
    
    # 保存实体文件
    entities_output = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'total_entities': len(entities),
            'migrated_from': 'graph_data.json'
        },
        'entities': entities
    }
    
    with open(entities_file, 'w', encoding='utf-8') as f:
        json.dump(entities_output, f, indent=2, ensure_ascii=False)
    
    print(f"💾 已保存实体到: {entities_file}")
    print(f"   文件大小: {entities_file.stat().st_size / 1024:.2f} KB")
    
    # 保存关系文件
    relations_output = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'total_relations': len(relations),
            'migrated_from': 'graph_data.json'
        },
        'relations': relations
    }
    
    with open(relations_file, 'w', encoding='utf-8') as f:
        json.dump(relations_output, f, indent=2, ensure_ascii=False)
    
    print(f"💾 已保存关系到: {relations_file}")
    print(f"   文件大小: {relations_file.stat().st_size / 1024:.2f} KB")
    
    # 备份原文件
    backup_file = graphdata_dir / f'graph_data.json.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    unified_file.rename(backup_file)
    print(f"📦 原文件已备份为: {backup_file}")
    
    print("\n✨ 迁移完成！")
    print(f"\n文件结构：")
    print(f"  - entities.json  : {len(entities)} 个实体")
    print(f"  - relations.json : {len(relations)} 个关系")

if __name__ == '__main__':
    migrate_graph_data()
