"""
快速环境检查脚本
用于快速检查Java和Neo4j环境
"""

# 导入环境检查模块
from environment_check import check_java_environment, check_neo4j_connection, check_all_environment
import os

def quick_check():
    """快速环境检查"""
    print("快速环境检查\n")
    
    # 检查Java
    print("检查Java环境...")
    java_result = check_java_environment()
    if java_result["available"]:
        print(f"✅ Java可用: {java_result['version']}")
    else:
        print(f"❌ Java不可用: {java_result['error']}")
    
    # 检查Neo4j
    print("\n检查Neo4j连接...")
    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')
    
    neo4j_result = check_neo4j_connection(neo4j_uri, neo4j_user, neo4j_password)
    if neo4j_result["connected"]:
        print(f"✅ Neo4j连接成功: {neo4j_result['version']}")
    else:
        print(f"❌ Neo4j连接失败: {neo4j_result['error']}")
    
    print("\n" + "="*60)
    return java_result["available"] and neo4j_result["connected"]


if __name__ == "__main__":
    import sys
    
    # 可以选择快速检查或完整检查
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        # 完整检查
        check_all_environment()
    else:
        # 快速检查
        all_ok = quick_check()
        if not all_ok:
            print("\n提示: 使用 'python check_environment.py --full' 查看详细信息")
            sys.exit(1)
