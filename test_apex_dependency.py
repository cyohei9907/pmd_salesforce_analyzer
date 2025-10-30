"""
Apex依存関係機能のテスト
"""
import os
import sys
import django

# Django設定
project_root = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apex_graph.settings')
django.setup()

from ast_api.import_service import ast_import_service
from ast_api.models import Repository
from ast_api.local_graph_service import local_graph_service
from pathlib import Path

def test_apex_dependency():
    """Apex依存関係のテスト"""
    
    print("="*60)
    print("Apex依存関係テスト")
    print("="*60)
    
    # テスト用のLWCファイル（Apexインポートがあるもの）
    ast_file = Path("output/ast/dreamhouse-lwc/lwc/propertyListMap_ast.xml")
    source_file = Path("output/ast/dreamhouse-lwc/lwc/propertyListMap.js")
    
    if not ast_file.exists():
        print(f"❌ AST file not found: {ast_file}")
        return
    
    print(f"📄 Testing file: {ast_file.name}")
    
    # リポジトリを取得
    try:
        repository = Repository.objects.get(name='dreamhouse-lwc')
        print(f"✓ Repository: {repository.name}")
    except Repository.DoesNotExist:
        print("  No repository found")
        repository = None
    
    # まず、既存のpropertyListMapノードを削除（再テスト用）
    component_nodes_to_remove = [
        node_id for node_id in local_graph_service.graph.nodes() 
        if 'propertyListMap' in node_id.lower()
    ]
    for node_id in component_nodes_to_remove:
        local_graph_service.graph.remove_node(node_id)
        print(f"  Removed existing node: {node_id}")
    
    # インポート実行
    print(f"\n📥 Importing with Apex dependency detection...")
    result = ast_import_service.import_ast_file(
        file_path=str(ast_file),
        repository=repository,
        source_code_path=str(source_file) if source_file.exists() else None
    )
    
    print(f"\nResult: {result}")
    
    if result['success']:
        print(f"\n✅ Import successful!")
        
        # Apex関連の関係を確認
        component_name = result['class_name']
        component_node_id = f"lwc:{component_name}"
        
        print(f"\n🔗 Checking Apex relationships for: {component_node_id}")
        
        # このコンポーネントからの全エッジを確認
        edges = list(local_graph_service.graph.edges(component_node_id, data=True))
        
        apex_edges = []
        for src, dst, data in edges:
            edge_type = data.get('type', 'unknown')
            if 'APEX' in edge_type.upper():
                apex_edges.append((src, dst, edge_type, data))
        
        print(f"Found {len(apex_edges)} Apex-related edges:")
        for src, dst, edge_type, data in apex_edges:
            print(f"  {src} -> {dst} [{edge_type}]")
            print(f"    Data: {data}")
        
        # Apexクラス・メソッドノードの確認
        apex_nodes = [
            node_id for node_id in local_graph_service.graph.nodes() 
            if any(keyword in node_id for keyword in ['PropertyController', 'class:Property', 'method:Property'])
        ]
        
        print(f"\nApex nodes found: {len(apex_nodes)}")
        for node_id in apex_nodes:
            node_data = local_graph_service.graph.nodes[node_id]
            node_type = node_data.get('type', 'unknown')
            is_placeholder = node_data.get('placeholder', False)
            placeholder_info = " (PLACEHOLDER)" if is_placeholder else ""
            print(f"  {node_id}: {node_type}{placeholder_info}")
    
    else:
        print(f"❌ Import failed: {result.get('error', 'Unknown error')}")

if __name__ == '__main__':
    test_apex_dependency()