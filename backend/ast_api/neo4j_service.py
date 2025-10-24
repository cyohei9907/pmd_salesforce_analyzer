"""
Neo4j图数据库服务
用于将AST数据存储到图数据库
"""
from neo4j import GraphDatabase
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Neo4jService:
    """Neo4j数据库连接和操作服务"""
    
    def __init__(self):
        self.driver = None
        self.connect()
    
    def connect(self):
        """连接到Neo4j数据库"""
        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            logger.info("Successfully connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.driver:
            self.driver.close()
    
    def clear_database(self):
        """清空数据库（谨慎使用）"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
    
    def create_class_node(self, tx, class_data):
        """创建类节点"""
        query = """
        MERGE (c:ApexClass {name: $name})
        SET c.simpleName = $simpleName,
            c.definingType = $definingType,
            c.public = $public,
            c.withSharing = $withSharing,
            c.fileName = $fileName
        RETURN c
        """
        return tx.run(query, class_data).single()
    
    def create_method_node(self, tx, method_data):
        """创建方法节点"""
        query = """
        MERGE (m:Method {canonicalName: $canonicalName, className: $className})
        SET m.name = $name,
            m.returnType = $returnType,
            m.arity = $arity,
            m.public = $public,
            m.static = $static,
            m.constructor = $constructor
        RETURN m
        """
        return tx.run(query, method_data).single()
    
    def create_soql_node(self, tx, soql_data):
        """创建SOQL查询节点"""
        query = """
        CREATE (s:SOQLQuery {query: $query})
        SET s.canonicalQuery = $canonicalQuery,
            s.className = $className,
            s.methodName = $methodName
        RETURN s
        """
        return tx.run(query, soql_data).single()
    
    def create_dml_node(self, tx, dml_data):
        """创建DML操作节点"""
        query = """
        CREATE (d:DMLOperation {type: $type})
        SET d.className = $className,
            d.methodName = $methodName,
            d.operationType = $operationType
        RETURN d
        """
        return tx.run(query, dml_data).single()
    
    def create_relationship(self, tx, from_node_label, from_property, from_value,
                          to_node_label, to_property, to_value, rel_type):
        """创建节点关系"""
        query = f"""
        MATCH (a:{from_node_label} {{{from_property}: $from_value}})
        MATCH (b:{to_node_label} {{{to_property}: $to_value}})
        MERGE (a)-[r:{rel_type}]->(b)
        RETURN r
        """
        return tx.run(query, {"from_value": from_value, "to_value": to_value}).single()
    
    def get_class_graph(self, class_name=None):
        """获取类的图数据"""
        with self.driver.session() as session:
            if class_name:
                query = """
                MATCH (c:ApexClass {name: $class_name})
                OPTIONAL MATCH (c)-[r1:HAS_METHOD]->(m:Method)
                OPTIONAL MATCH (m)-[r2:CONTAINS_SOQL]->(s:SOQLQuery)
                OPTIONAL MATCH (m)-[r3:CONTAINS_DML]->(d:DMLOperation)
                RETURN c, collect(DISTINCT m) as methods, 
                       collect(DISTINCT s) as soqls,
                       collect(DISTINCT d) as dmls
                """
                result = session.run(query, {"class_name": class_name})
            else:
                query = """
                MATCH (c:ApexClass)
                OPTIONAL MATCH (c)-[r:HAS_METHOD]->(m:Method)
                RETURN c, collect(m) as methods
                """
                result = session.run(query)
            
            return [record.data() for record in result]
    
    def get_full_graph(self):
        """获取完整的图数据用于可视化"""
        with self.driver.session() as session:
            # 获取所有节点
            nodes_query = """
            MATCH (n)
            RETURN id(n) as id, labels(n) as labels, properties(n) as properties
            """
            nodes = session.run(nodes_query)
            
            # 获取所有关系
            edges_query = """
            MATCH (a)-[r]->(b)
            RETURN id(a) as source, id(b) as target, type(r) as type, properties(r) as properties
            """
            edges = session.run(edges_query)
            
            return {
                'nodes': [record.data() for record in nodes],
                'edges': [record.data() for record in edges]
            }
    
    def get_statistics(self):
        """获取数据库统计信息"""
        with self.driver.session() as session:
            query = """
            MATCH (c:ApexClass)
            OPTIONAL MATCH (c)-[:HAS_METHOD]->(m:Method)
            OPTIONAL MATCH (m)-[:CONTAINS_SOQL]->(s:SOQLQuery)
            OPTIONAL MATCH (m)-[:CONTAINS_DML]->(d:DMLOperation)
            RETURN count(DISTINCT c) as classes,
                   count(DISTINCT m) as methods,
                   count(DISTINCT s) as soqls,
                   count(DISTINCT d) as dmls
            """
            result = session.run(query)
            return result.single().data()


# 全局服务实例
neo4j_service = Neo4jService()
