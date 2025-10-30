"""
全LWCファイルをApex依存関係付きで再インポート
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

def reimport_all_lwc_with_apex():
    """全LWCファイルをApex依存関係付きで再インポート"""
    
    lwc_dir = Path("output/ast/dreamhouse-lwc/lwc")
    
    if not lwc_dir.exists():
        print(f"❌ LWC directory not found: {lwc_dir}")
        return
    
    # リポジトリを取得
    try:
        repository = Repository.objects.get(name='dreamhouse-lwc')
        print(f"✓ Using repository: {repository.name}")
    except Repository.DoesNotExist:
        print("  No repository found")
        repository = None
    
    # 既存のLWCノードを削除（再インポート用）
    print("\n🗑️ Removing existing LWC nodes...")
    lwc_nodes_to_remove = []
    for node_id in list(local_graph_service.graph.nodes()):
        if any(prefix in node_id for prefix in ['lwc:', 'jsclass:', 'jsmethod:', 'jsfunc:']):
            lwc_nodes_to_remove.append(node_id)
    
    for node_id in lwc_nodes_to_remove:
        local_graph_service.graph.remove_node(node_id)
    
    print(f"  Removed {len(lwc_nodes_to_remove)} LWC nodes")
    
    # すべてのAST XMLファイルを検索
    ast_files = list(lwc_dir.glob("*_ast.xml"))
    
    print(f"\n📁 Found {len(ast_files)} LWC AST files")
    print("="*60)
    
    success_count = 0
    failed_count = 0
    apex_relationships = 0
    
    for ast_file in ast_files:
        js_file = ast_file.parent / ast_file.name.replace('_ast.xml', '.js')
        
        print(f"\n📥 Processing: {ast_file.name}")
        
        result = ast_import_service.import_ast_file(
            file_path=str(ast_file),
            repository=repository,
            source_code_path=str(js_file) if js_file.exists() else None
        )
        
        if result['success']:
            success_count += 1
            component_name = result['class_name']
            component_node_id = f"lwc:{component_name}"
            
            # Apex関係をカウント
            edges = list(local_graph_service.graph.edges(component_node_id, data=True))
            apex_edge_count = sum(1 for _, _, data in edges if 'APEX' in data.get('type', '').upper())
            
            if apex_edge_count > 0:
                apex_relationships += apex_edge_count
                print(f"  ✅ {component_name}: {result['methods_count']} methods, {apex_edge_count} Apex relationships")
            else:
                print(f"  ✅ {component_name}: {result['methods_count']} methods")
        else:
            failed_count += 1
            print(f"  ❌ Error: {result.get('error', 'Unknown error')}")
    
    # 最終統計
    print("\n" + "="*60)
    print("FINAL STATISTICS:")
    print("="*60)
    print(f"  Total files: {len(ast_files)}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Apex relationships: {apex_relationships}")
    
    # グラフ統計
    graph = local_graph_service.graph
    node_types = {}
    for node_id in graph.nodes():
        node_data = graph.nodes[node_id]
        node_type = node_data.get('type', 'unknown')
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    print(f"\n📊 Graph Statistics:")
    print(f"  Total nodes: {graph.number_of_nodes()}")
    print(f"  Total edges: {graph.number_of_edges()}")
    
    print(f"\nNode types:")
    for node_type, count in sorted(node_types.items()):
        print(f"  {node_type}: {count}")
    
    # Apex関係の詳細
    apex_edge_types = {}
    for _, _, data in graph.edges(data=True):
        edge_type = data.get('type', 'unknown')
        if 'APEX' in edge_type.upper():
            apex_edge_types[edge_type] = apex_edge_types.get(edge_type, 0) + 1
    
    if apex_edge_types:
        print(f"\nApex relationship types:")
        for edge_type, count in apex_edge_types.items():
            print(f"  {edge_type}: {count}")

if __name__ == '__main__':
    reimport_all_lwc_with_apex()