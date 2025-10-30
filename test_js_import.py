"""
テスト: JavaScript AST ファイルのインポート
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
from pathlib import Path

def test_js_import():
    """JavaScript ASTファイルのインポートテスト"""
    
    # テスト用のJavaScript ASTファイル
    ast_file = Path("output/ast/dreamhouse-lwc/lwc/barcodeScanner_ast.xml")
    source_file = Path("output/ast/dreamhouse-lwc/lwc/barcodeScanner.js")
    
    if not ast_file.exists():
        print(f"❌ AST file not found: {ast_file}")
        return
    
    print(f"✓ Testing JavaScript AST import...")
    print(f"  AST file: {ast_file}")
    print(f"  Source file: {source_file}")
    
    # リポジトリを取得（既存のdreamhouse-lwcリポジトリ）
    try:
        repository = Repository.objects.get(name='dreamhouse-lwc')
        print(f"  Repository: {repository.name}")
    except Repository.DoesNotExist:
        print("  No repository found, importing without repository")
        repository = None
    
    # インポート実行
    print("\n📥 Importing JavaScript component...")
    result = ast_import_service.import_ast_file(
        file_path=str(ast_file),
        repository=repository,
        source_code_path=str(source_file) if source_file.exists() else None
    )
    
    # 結果表示
    print("\n" + "="*60)
    print("IMPORT RESULT:")
    print("="*60)
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    if result['success']:
        print("\n✅ JavaScript component imported successfully!")
        
        # グラフデータを確認
        print("\n📊 Checking graph data...")
        from ast_api.local_graph_service import local_graph_service
        
        component_name = result['class_name']
        component_node_id = f"lwc:{component_name}"
        
        if local_graph_service.graph.has_node(component_node_id):
            print(f"  ✓ Component node found: {component_node_id}")
            node_data = local_graph_service.graph.nodes[component_node_id]
            print(f"    Node attributes: {node_data}")
            
            # エッジを確認
            edges = list(local_graph_service.graph.edges(component_node_id, data=True))
            print(f"\n  ✓ Component has {len(edges)} relationships:")
            for src, dst, data in edges[:5]:  # 最初の5個を表示
                print(f"    {src} -> {dst} [{data.get('type', 'unknown')}]")
            if len(edges) > 5:
                print(f"    ... and {len(edges) - 5} more")
        else:
            print(f"  ❌ Component node not found in graph")
    else:
        print(f"\n❌ Import failed: {result.get('error', 'Unknown error')}")

if __name__ == '__main__':
    test_js_import()
