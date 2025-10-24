"""
测试Neo4j连接和基本操作
"""
import sys
import os

# 添加Django项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apex_graph.settings')

import django
django.setup()

from ast_api.neo4j_service import neo4j_service

def test_connection():
    """测试Neo4j连接"""
    print("测试Neo4j连接...")
    try:
        # 测试查询
        stats = neo4j_service.get_statistics()
        print(f"✅ Neo4j连接成功!")
        print(f"当前数据: {stats}")
        return True
    except Exception as e:
        print(f"❌ Neo4j连接失败: {e}")
        return False

def test_create_node():
    """测试创建节点"""
    print("\n测试创建类节点...")
    try:
        with neo4j_service.driver.session() as session:
            class_data = {
                'name': 'TestClass',
                'simpleName': 'TestClass',
                'definingType': 'TestClass',
                'public': True,
                'withSharing': True,
                'fileName': 'test.cls'
            }
            result = session.execute_write(neo4j_service.create_class_node, class_data)
            print(f"✅ 节点创建成功: {result}")
            
            # 清理测试数据
            session.run("MATCH (c:ApexClass {name: 'TestClass'}) DELETE c")
            print("✅ 测试数据已清理")
            return True
    except Exception as e:
        print(f"❌ 节点创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("Neo4j服务测试")
    print("=" * 50)
    
    if test_connection():
        test_create_node()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
