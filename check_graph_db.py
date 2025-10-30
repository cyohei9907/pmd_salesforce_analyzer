"""
グラフデータベースの内容確認
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

from ast_api.local_graph_service import local_graph_service
import json

def check_graph_content():
    """グラフデータベースの内容を確認"""
    
    print("="*60)
    print("グラフデータベース内容確認")
    print("="*60)
    
    graph = local_graph_service.graph
    
    print(f"総ノード数: {graph.number_of_nodes()}")
    print(f"総エッジ数: {graph.number_of_edges()}")
    
    # ノードタイプ別カウント
    node_types = {}
    for node_id in graph.nodes():
        node_data = graph.nodes[node_id]
        node_type = node_data.get('type', 'unknown')
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    print("\nノードタイプ別内訳:")
    for node_type, count in sorted(node_types.items()):
        print(f"  {node_type}: {count}")
    
    # LWC関連ノードを詳細確認
    lwc_node_types = ['LWCComponent', 'JavaScriptClass', 'JavaScriptMethod', 'JavaScriptFunction', 'Dependency']
    
    print(f"\nLWC関連ノード詳細:")
    for node_type in lwc_node_types:
        nodes = [n for n in graph.nodes() if graph.nodes[n].get('type') == node_type]
        print(f"\n{node_type} ({len(nodes)} 個):")
        for node_id in nodes[:3]:  # 最初の3個を表示
            node_data = graph.nodes[node_id]
            name = node_data.get('name', 'no name')
            print(f"  - {node_id}: {name}")
        if len(nodes) > 3:
            print(f"  ... and {len(nodes) - 3} more")
    
    # エッジの詳細確認
    print(f"\nエッジの詳細:")
    edge_types = {}
    for source, target, data in graph.edges(data=True):
        edge_type = data.get('type', 'unknown')
        edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
    
    for edge_type, count in sorted(edge_types.items()):
        print(f"  {edge_type}: {count}")
    
    # LWC関連エッジを確認
    lwc_edges = []
    for source, target, data in graph.edges(data=True):
        source_type = graph.nodes[source].get('type', '')
        target_type = graph.nodes[target].get('type', '')
        if any(t.startswith(('LWC', 'JavaScript', 'Dependency')) for t in [source_type, target_type]):
            lwc_edges.append((source, target, data.get('type', 'unknown')))
    
    print(f"\nLWC関連エッジ ({len(lwc_edges)} 個):")
    for source, target, edge_type in lwc_edges[:10]:  # 最初の10個を表示
        print(f"  {source} -> {target} [{edge_type}]")
    if len(lwc_edges) > 10:
        print(f"  ... and {len(lwc_edges) - 10} more")

if __name__ == '__main__':
    check_graph_content()