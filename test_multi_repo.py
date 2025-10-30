"""
多仓库功能测试脚本
"""
import requests
import json

BASE_URL = 'http://localhost:8000/api'

def test_list_repositories():
    """测试获取仓库列表"""
    print("\n=== 测试: 获取仓库列表 ===")
    response = requests.get(f'{BASE_URL}/repositories/')
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

def test_clone_repository():
    """测试克隆仓库"""
    print("\n=== 测试: 克隆并注册仓库 ===")
    data = {
        'repo_url': 'https://github.com/trailheadapps/lwc-recipes.git',
        'branch': 'main',
        'apex_dir': 'force-app/main/default/classes',
        'force': False,
        'auto_import': True,
        'set_active': True
    }
    print(f"请求数据: {json.dumps(data, indent=2)}")
    
    response = requests.post(f'{BASE_URL}/repositories/clone/', json=data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"错误: {response.text}")
    return response.json() if response.status_code in [200, 201] else None

def test_switch_repository(repo_id):
    """测试切换仓库"""
    print(f"\n=== 测试: 切换到仓库 {repo_id} ===")
    data = {'repo_id': repo_id}
    
    response = requests.post(f'{BASE_URL}/repositories/switch/', json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

def test_get_repository_graph(repo_id):
    """测试获取仓库图数据"""
    print(f"\n=== 测试: 获取仓库 {repo_id} 的图数据 ===")
    response = requests.get(f'{BASE_URL}/repositories/{repo_id}/graph/')
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"节点数量: {len(data['graph']['nodes'])}")
        print(f"关系数量: {len(data['graph']['relationships'])}")
        
        # 显示前3个节点
        if data['graph']['nodes']:
            print("\n前3个节点:")
            for node in data['graph']['nodes'][:3]:
                print(f"  - {node['labels']}: {node['properties'].get('name', 'N/A')}")
    else:
        print(f"错误: {response.text}")
    
    return response.json() if response.status_code == 200 else None

def test_delete_repository(repo_id):
    """测试删除仓库"""
    print(f"\n=== 测试: 删除仓库 {repo_id} ===")
    response = requests.delete(f'{BASE_URL}/repositories/{repo_id}/')
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

if __name__ == '__main__':
    print("=" * 60)
    print("多仓库功能API测试")
    print("=" * 60)
    
    # 1. 获取当前仓库列表
    repos_data = test_list_repositories()
    
    # 2. 如果没有仓库,克隆一个测试仓库
    if repos_data.get('count', 0) == 0:
        print("\n⚠️  当前没有仓库,尝试克隆测试仓库...")
        clone_result = test_clone_repository()
        
        if clone_result and clone_result.get('success'):
            print("\n✅ 仓库克隆成功!")
            # 重新获取仓库列表
            repos_data = test_list_repositories()
    
    # 3. 如果有仓库,进行其他测试
    if repos_data.get('count', 0) > 0:
        first_repo = repos_data['repositories'][0]
        repo_id = first_repo['id']
        
        # 测试切换仓库
        test_switch_repository(repo_id)
        
        # 测试获取图数据
        test_get_repository_graph(repo_id)
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
