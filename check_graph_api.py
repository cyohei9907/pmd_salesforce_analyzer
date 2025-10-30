import requests
import json

try:
    response = requests.get('http://localhost:8000/api/ast/graph/')
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Total nodes: {len(data.get("nodes", []))}')
        print(f'Total edges: {len(data.get("edges", []))}')
        
        # Check node types
        node_types = {}
        for node in data.get('nodes', []):
            node_type = node.get('type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        print('\nNode types breakdown:')
        for node_type, count in sorted(node_types.items()):
            print(f'  {node_type}: {count}')
            
        # Check for LWC nodes specifically
        lwc_nodes = [n for n in data.get('nodes', []) if n.get('type') in ['LWCComponent', 'JavaScriptClass', 'JavaScriptMethod']]
        print(f'\nLWC-related nodes: {len(lwc_nodes)}')
        
        if lwc_nodes:
            print('LWC nodes found:')
            for node in lwc_nodes[:5]:  # Show first 5
                print(f'  - {node.get("id")}: {node.get("type")} ({node.get("name", "no name")})')
    else:
        print(f'Error: {response.status_code}')
        print(response.text)
        
except Exception as e:
    print(f'Request failed: {e}')