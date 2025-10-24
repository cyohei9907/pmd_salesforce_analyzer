"""
环境检查使用示例
演示如何在代码中使用环境检查功能
"""

# 示例1: 基本使用 - 检查Java环境
def example_check_java():
    """检查Java环境的基本示例"""
    print("=" * 60)
    print("示例1: 检查Java环境")
    print("=" * 60)
    
    from environment_check import check_java_environment
    
    result = check_java_environment()
    
    if result["available"]:
        print(f"✅ Java可用")
        print(f"   版本: {result['version']}")
        print(f"   JAVA_HOME: {result['java_home']}")
        return True
    else:
        print(f"❌ Java不可用")
        print(f"   错误: {result['error']}")
        return False


# 示例2: 基本使用 - 检查Neo4j连接
def example_check_neo4j():
    """检查Neo4j连接的基本示例"""
    print("\n" + "=" * 60)
    print("示例2: 检查Neo4j连接")
    print("=" * 60)
    
    from environment_check import check_neo4j_connection
    import os
    
    # 从环境变量获取配置
    uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    user = os.getenv('NEO4J_USER', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', 'password')
    
    print(f"连接到: {uri}")
    result = check_neo4j_connection(uri, user, password)
    
    if result["connected"]:
        print(f"✅ Neo4j连接成功")
        print(f"   版本: {result['version']}")
        return True
    else:
        print(f"❌ Neo4j连接失败")
        print(f"   错误: {result['error']}")
        return False


# 示例3: 应用启动前检查
def example_startup_check():
    """应用启动前的环境检查"""
    print("\n" + "=" * 60)
    print("示例3: 应用启动前检查")
    print("=" * 60)
    
    from environment_check import check_all_environment
    
    print("正在执行启动前环境检查...")
    result = check_all_environment()
    
    # 检查必需组件
    if not result["java"]["available"]:
        raise RuntimeError(
            f"Java环境不可用，无法启动应用\n"
            f"错误: {result['java']['error']}"
        )
    
    # 检查可选组件
    if not result["neo4j"]["connected"]:
        print(f"\n⚠️  警告: Neo4j不可用，图形功能将被禁用")
        print(f"   原因: {result['neo4j']['error']}")
    
    print("\n✅ 环境检查通过，可以启动应用")
    return result


# 示例4: 使用PMD环境检查
def example_pmd_check():
    """使用PMD环境检查功能"""
    print("\n" + "=" * 60)
    print("示例4: PMD环境检查")
    print("=" * 60)
    
    from pmd_check import check_pmd_environment
    
    env = check_pmd_environment()
    
    print(f"操作系统: {env['os']}")
    print(f"Java: {'✅' if env['java_available'] else '❌'}")
    print(f"Neo4j: {'✅' if env['neo4j_connected'] else '⚠️'}")
    print(f"PMD命令: {'✅' if env['command_exists'] else '❌'}")
    print(f"PMD就绪: {'✅' if env['ready'] else '❌'}")
    
    if env['ready']:
        print("\n✅ 可以执行PMD分析")
    else:
        print("\n❌ 无法执行PMD分析，请检查环境")
    
    return env


# 示例5: 错误处理
def example_error_handling():
    """演示错误处理"""
    print("\n" + "=" * 60)
    print("示例5: 错误处理")
    print("=" * 60)
    
    from environment_check import check_java_environment, check_neo4j_connection
    
    # 检查Java（带错误处理）
    try:
        java_result = check_java_environment()
        if not java_result["available"]:
            print(f"Java检查失败: {java_result['error']}")
            print("建议: 请安装JDK 8或更高版本")
    except Exception as e:
        print(f"检查Java时发生异常: {e}")
    
    # 检查Neo4j（带错误处理）
    try:
        neo4j_result = check_neo4j_connection()
        if not neo4j_result["connected"]:
            error = neo4j_result["error"]
            if "未安装neo4j Python包" in error:
                print("Neo4j驱动未安装")
                print("建议: 运行 pip install neo4j")
            elif "无法连接" in error or "refused" in error:
                print("Neo4j服务未启动")
                print("建议: 启动Neo4j Desktop或服务")
            elif "认证失败" in error:
                print("Neo4j认证失败")
                print("建议: 检查用户名和密码")
    except Exception as e:
        print(f"检查Neo4j时发生异常: {e}")


# 示例6: 条件性功能启用
def example_conditional_features():
    """根据环境检查结果启用/禁用功能"""
    print("\n" + "=" * 60)
    print("示例6: 条件性功能启用")
    print("=" * 60)
    
    from environment_check import check_java_environment, check_neo4j_connection
    
    features = {
        "pmd_analysis": False,
        "graph_visualization": False,
        "ast_parsing": False
    }
    
    # 检查Java - PMD分析必需
    java_result = check_java_environment()
    if java_result["available"]:
        features["pmd_analysis"] = True
        features["ast_parsing"] = True
        print("✅ 启用PMD分析功能")
        print("✅ 启用AST解析功能")
    else:
        print("❌ 禁用PMD分析功能（Java不可用）")
    
    # 检查Neo4j - 图形化功能可选
    neo4j_result = check_neo4j_connection()
    if neo4j_result["connected"]:
        features["graph_visualization"] = True
        print("✅ 启用图形可视化功能")
    else:
        print("⚠️  禁用图形可视化功能（Neo4j不可用）")
    
    print(f"\n可用功能: {features}")
    return features


# 示例7: 自定义Neo4j配置
def example_custom_neo4j_config():
    """使用自定义Neo4j配置"""
    print("\n" + "=" * 60)
    print("示例7: 自定义Neo4j配置")
    print("=" * 60)
    
    from environment_check import check_neo4j_connection
    
    # 自定义配置
    custom_configs = [
        {
            "uri": "bolt://localhost:7687",
            "user": "neo4j",
            "password": "password",
            "name": "本地开发环境"
        },
        {
            "uri": "bolt://prod-server:7687",
            "user": "admin",
            "password": "prod_password",
            "name": "生产环境"
        }
    ]
    
    for config in custom_configs:
        print(f"\n测试 {config['name']}...")
        print(f"  URI: {config['uri']}")
        
        result = check_neo4j_connection(
            uri=config['uri'],
            user=config['user'],
            password=config['password']
        )
        
        if result["connected"]:
            print(f"  ✅ 连接成功 (版本: {result['version']})")
        else:
            print(f"  ❌ 连接失败: {result['error']}")


# 示例8: 完整的应用初始化流程
def example_full_initialization():
    """完整的应用初始化流程示例"""
    print("\n" + "=" * 60)
    print("示例8: 完整应用初始化")
    print("=" * 60)
    
    from environment_check import check_all_environment
    import sys
    
    print("步骤1: 环境检查...")
    env_result = check_all_environment()
    
    print("\n步骤2: 验证必需组件...")
    if not env_result["java"]["available"]:
        print("❌ 致命错误: Java环境不可用")
        sys.exit(1)
    
    print("\n步骤3: 检查可选组件...")
    graph_enabled = env_result["neo4j"]["connected"]
    if graph_enabled:
        print("✅ 图形功能已启用")
    else:
        print("⚠️  图形功能已禁用（Neo4j不可用）")
    
    print("\n步骤4: 配置应用...")
    config = {
        "java_available": env_result["java"]["available"],
        "java_version": env_result["java"]["version"],
        "neo4j_enabled": graph_enabled,
        "features": {
            "pmd_analysis": True,
            "graph_visualization": graph_enabled,
            "ast_export": True
        }
    }
    
    print(f"\n应用配置: {config}")
    print("\n✅ 初始化完成，应用已就绪")
    
    return config


# 主函数 - 运行所有示例
def main():
    """运行所有示例"""
    print("\n" + "🚀" * 30)
    print("环境检查功能使用示例")
    print("🚀" * 30)
    
    try:
        # 运行所有示例
        example_check_java()
        example_check_neo4j()
        # example_startup_check()  # 这个会打印很多输出
        example_pmd_check()
        example_error_handling()
        example_conditional_features()
        example_custom_neo4j_config()
        # example_full_initialization()  # 这个也会打印很多输出
        
        print("\n" + "=" * 60)
        print("✅ 所有示例执行完成")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
