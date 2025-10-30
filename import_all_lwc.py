"""
すべてのLWC ASTファイルをインポート
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

def import_all_lwc():
    """すべてのLWC ASTファイルをインポート"""
    
    lwc_dir = Path("output/ast/dreamhouse-lwc/lwc")
    
    if not lwc_dir.exists():
        print(f"❌ LWC directory not found: {lwc_dir}")
        return
    
    # リポジトリを取得
    try:
        repository = Repository.objects.get(name='dreamhouse-lwc')
        print(f"✓ Using repository: {repository.name}\n")
    except Repository.DoesNotExist:
        print("  No repository found, importing without repository\n")
        repository = None
    
    # すべてのAST XMLファイルを検索
    ast_files = list(lwc_dir.glob("*_ast.xml"))
    
    print(f"Found {len(ast_files)} LWC AST files\n")
    print("="*60)
    
    success_count = 0
    failed_count = 0
    results = []
    
    for ast_file in ast_files:
        # 対応するJSファイルを探す
        js_file = ast_file.parent / ast_file.name.replace('_ast.xml', '.js')
        
        print(f"\n📥 Importing: {ast_file.name}")
        
        result = ast_import_service.import_ast_file(
            file_path=str(ast_file),
            repository=repository,
            source_code_path=str(js_file) if js_file.exists() else None
        )
        
        results.append(result)
        
        if result['success']:
            success_count += 1
            print(f"  ✅ {result['class_name']}: {result['methods_count']} methods")
        else:
            failed_count += 1
            print(f"  ❌ Error: {result.get('error', 'Unknown error')}")
    
    # サマリー
    print("\n" + "="*60)
    print("IMPORT SUMMARY:")
    print("="*60)
    print(f"  Total files: {len(ast_files)}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {failed_count}")
    
    if success_count > 0:
        print(f"\n✅ Successfully imported {success_count} LWC components to graph!")
        
        # グラフ統計
        print("\n📊 Graph Statistics:")
        from ast_api.local_graph_service import local_graph_service
        
        lwc_nodes = [n for n in local_graph_service.graph.nodes() if n.startswith('lwc:')]
        js_class_nodes = [n for n in local_graph_service.graph.nodes() if n.startswith('jsclass:')]
        js_method_nodes = [n for n in local_graph_service.graph.nodes() if n.startswith('jsmethod:')]
        dep_nodes = [n for n in local_graph_service.graph.nodes() if n.startswith('dep:')]
        
        print(f"  LWC Components: {len(lwc_nodes)}")
        print(f"  JavaScript Classes: {len(js_class_nodes)}")
        print(f"  JavaScript Methods: {len(js_method_nodes)}")
        print(f"  Dependencies: {len(dep_nodes)}")
        print(f"  Total edges: {local_graph_service.graph.number_of_edges()}")

if __name__ == '__main__':
    import_all_lwc()
