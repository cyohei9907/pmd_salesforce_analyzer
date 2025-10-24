"""
环境检查工具
用于检查本地是否连接了Neo4j数据库和是否有Java环境
"""
import os
import sys
import subprocess
import platform
from pathlib import Path


def check_java_environment():
    """
    检查Java环境是否可用
    
    Returns:
        dict: Java环境检查结果
            - available: bool - Java是否可用
            - version: str - Java版本信息
            - java_home: str - JAVA_HOME环境变量
            - error: str - 错误信息（如果有）
    """
    result = {
        "available": False,
        "version": None,
        "java_home": os.getenv('JAVA_HOME', '未设置'),
        "error": None
    }
    
    try:
        # 尝试执行 java -version 命令
        java_check = subprocess.run(
            ["java", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            timeout=5
        )
        
        if java_check.returncode == 0:
            result["available"] = True
            # Java版本信息通常输出到stderr
            version_output = java_check.stderr if java_check.stderr else java_check.stdout
            if version_output:
                # 提取第一行作为版本信息
                result["version"] = version_output.split('\n')[0].strip()
            else:
                result["version"] = "未知版本"
        else:
            result["error"] = "Java命令执行失败"
            
    except FileNotFoundError:
        result["error"] = "未找到Java命令，请确保已安装Java并配置了环境变量"
    except subprocess.TimeoutExpired:
        result["error"] = "Java命令执行超时"
    except Exception as e:
        result["error"] = f"检查Java环境时发生错误: {str(e)}"
    
    return result


def check_neo4j_connection(uri='bolt://localhost:7687', user='neo4j', password='password'):
    """
    检查Neo4j数据库连接是否可用
    
    Args:
        uri: Neo4j数据库URI
        user: 用户名
        password: 密码
        
    Returns:
        dict: Neo4j连接检查结果
            - connected: bool - 是否连接成功
            - uri: str - 连接URI
            - version: str - Neo4j版本信息
            - database: str - 数据库名称
            - error: str - 错误信息（如果有）
    """
    result = {
        "connected": False,
        "uri": uri,
        "version": None,
        "database": None,
        "error": None
    }
    
    try:
        # 尝试导入neo4j模块
        from neo4j import GraphDatabase
        
        # 尝试连接数据库
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # 验证连接
        with driver.session() as session:
            # 执行一个简单的查询来验证连接
            db_result = session.run("CALL dbms.components() YIELD name, versions, edition RETURN name, versions[0] as version, edition")
            record = db_result.single()
            
            if record:
                result["connected"] = True
                result["version"] = record.get("version", "未知版本")
                result["database"] = record.get("name", "Neo4j")
                
            # 获取当前数据库名称
            db_name_result = session.run("CALL db.info() YIELD name RETURN name")
            db_name_record = db_name_result.single()
            if db_name_record:
                result["database"] = db_name_record.get("name", result["database"])
        
        driver.close()
        
    except ImportError:
        result["error"] = "未安装neo4j Python包，请运行: pip install neo4j"
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower():
            result["error"] = f"Neo4j认证失败，请检查用户名和密码: {error_msg}"
        elif "connection" in error_msg.lower() or "refused" in error_msg.lower():
            result["error"] = f"无法连接到Neo4j数据库，请确保Neo4j服务已启动: {error_msg}"
        else:
            result["error"] = f"连接Neo4j时发生错误: {error_msg}"
    
    return result


def check_networkx():
    """
    检查NetworkX是否已安装（用于本地图数据库）
    
    Returns:
        dict: NetworkX检查结果
            - available: bool - NetworkX是否可用
            - version: str - NetworkX版本信息
            - error: str - 错误信息（如果有）
    """
    result = {
        "available": False,
        "version": None,
        "error": None
    }
    
    try:
        import networkx as nx
        result["available"] = True
        result["version"] = nx.__version__
    except ImportError:
        result["error"] = "未安装networkx Python包，请运行: pip install networkx"
    except Exception as e:
        result["error"] = f"检查NetworkX时发生错误: {str(e)}"
    
    return result


def check_all_environment():
    """
    检查所有环境依赖
    
    Returns:
        dict: 包含所有检查结果的字典
    """
    print("=" * 60)
    print("环境检查工具")
    print("=" * 60)
    
    # 检查操作系统
    print(f"\n操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version.split()[0]}")
    
    # 检查Java环境
    print("\n" + "-" * 60)
    print("1. 检查Java环境")
    print("-" * 60)
    java_result = check_java_environment()
    
    if java_result["available"]:
        print(f"✅ Java环境可用")
        print(f"   版本: {java_result['version']}")
        print(f"   JAVA_HOME: {java_result['java_home']}")
    else:
        print(f"❌ Java环境不可用")
        print(f"   错误: {java_result['error']}")
    
    # 检查Neo4j连接
    print("\n" + "-" * 60)
    print("2. 检查Neo4j数据库连接（可选）")
    print("-" * 60)
    
    # 从环境变量或默认值获取Neo4j配置
    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')
    
    print(f"连接URI: {neo4j_uri}")
    neo4j_result = check_neo4j_connection(neo4j_uri, neo4j_user, neo4j_password)
    
    if neo4j_result["connected"]:
        print(f"✅ Neo4j数据库连接成功")
        print(f"   版本: {neo4j_result['version']}")
        print(f"   数据库: {neo4j_result['database']}")
    else:
        print(f"⚠️  Neo4j数据库连接失败（将使用本地图数据库）")
        print(f"   错误: {neo4j_result['error']}")
    
    # 检查NetworkX
    print("\n" + "-" * 60)
    print("3. 检查NetworkX（本地图数据库）")
    print("-" * 60)
    networkx_result = check_networkx()
    
    if networkx_result["available"]:
        print(f"✅ NetworkX可用")
        print(f"   版本: {networkx_result['version']}")
    else:
        print(f"❌ NetworkX不可用")
        print(f"   错误: {networkx_result['error']}")
    
    # 总结
    print("\n" + "=" * 60)
    print("环境检查总结")
    print("=" * 60)
    
    # 至少需要Java和NetworkX（Neo4j是可选的）
    graph_db_available = neo4j_result["connected"] or networkx_result["available"]
    all_ready = java_result["available"] and graph_db_available
    
    if all_ready:
        print("✅ 所有必需环境检查通过，系统可以正常运行")
        if neo4j_result["connected"] and networkx_result["available"]:
            print("   - 图数据库: Neo4j + 本地存储（双后端模式）")
        elif neo4j_result["connected"]:
            print("   - 图数据库: Neo4j（推荐用于生产环境）")
        elif networkx_result["available"]:
            print("   - 图数据库: 本地存储（适合开发和测试）")
    else:
        print("❌ 环境检查未通过，请解决以下问题:")
        if not java_result["available"]:
            print("   - Java环境不可用（必需）")
        if not graph_db_available:
            print("   - 图数据库不可用（至少需要Neo4j或NetworkX之一）")
    
    print("=" * 60)
    
    return {
        "os": platform.system(),
        "python_version": sys.version.split()[0],
        "java": java_result,
        "neo4j": neo4j_result,
        "networkx": networkx_result,
        "graph_db_available": graph_db_available,
        "all_ready": all_ready
    }


def main():
    """主函数"""
    try:
        result = check_all_environment()
        
        # 根据检查结果返回退出码
        if result["all_ready"]:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n用户中断检查")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
