"""
Django内からグラフAPIをテスト
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

from ast_api.views import get_graph_data
from rest_framework.test import APIRequestFactory
import json

def test_graph_api():
    """グラフAPIをテスト"""
    
    print("="*60)
    print("グラフAPI レスポンステスト")
    print("="*60)
    
    # APIRequestFactoryでリクエストをシミュレート
    factory = APIRequestFactory()
    request = factory.get('/api/ast/graph/')
    
    # APIを呼び出し
    response = get_graph_data(request)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.data
        print(f"Total nodes: {len(data['nodes'])}")
        print(f"Total edges: {len(data['edges'])}")
        
        # ノードタイプ別カウント
        node_types = {}
        for node in data['nodes']:
            node_type = node.get('type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        print("\nノードタイプ別内訳:")
        for node_type, count in sorted(node_types.items()):
            print(f"  {node_type}: {count}")
        
        # LWC関連ノードの詳細表示
        lwc_node_types = ['LWCComponent', 'JavaScriptClass', 'JavaScriptMethod', 'JavaScriptFunction', 'Dependency']
        
        print(f"\nLWC関連ノード詳細:")
        for node_type in lwc_node_types:
            nodes = [n for n in data['nodes'] if n.get('type') == node_type]
            print(f"\n{node_type} ({len(nodes)} 個):")
            for node in nodes[:3]:  # 最初の3個を表示
                name = node.get('name', 'no name')
                print(f"  - {node.get('id')}: {name}")
            if len(nodes) > 3:
                print(f"  ... and {len(nodes) - 3} more")
        
        # エッジの詳細確認
        print(f"\nエッジの詳細:")
        edge_types = {}
        for edge in data['edges']:
            edge_type = edge.get('type', 'unknown')
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        for edge_type, count in sorted(edge_types.items()):
            print(f"  {edge_type}: {count}")
            
    else:
        print(f"Error response: {response.data}")

if __name__ == '__main__':
    test_graph_api()