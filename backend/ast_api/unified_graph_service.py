"""
统一图数据库服务
自动在 Neo4j 和本地图数据库之间切换
"""
import logging
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class UnifiedGraphService:
    """统一图数据库服务"""
    
    def __init__(self):
        self.neo4j_service = None
        self.local_service = None
        self.use_neo4j = False
        self.use_local = False
        
        self._init_services()
    
    def _init_services(self):
        """初始化服务"""
        # 检查是否启用 Neo4j
        use_neo4j_enabled = getattr(settings, 'USE_NEO4J', False)
        
        # 尝试初始化 Neo4j（仅当配置启用时）
        if use_neo4j_enabled:
            try:
                from .neo4j_service import neo4j_service
                if neo4j_service.driver is not None:
                    self.neo4j_service = neo4j_service
                    self.use_neo4j = True
                    logger.info("Neo4j service initialized successfully")
            except Exception as e:
                logger.warning(f"Neo4j service not available: {e}")
        else:
            logger.info("Neo4j disabled in settings (USE_NEO4J=False)")
        
        # 初始化本地图服务（始终可用）
        try:
            from .local_graph_service import local_graph_service
            if local_graph_service.connected:
                self.local_service = local_graph_service
                self.use_local = True
                logger.info("Local graph service initialized successfully")
        except Exception as e:
            logger.error(f"Local graph service initialization failed: {e}")
    
    @property
    def is_connected(self) -> bool:
        """检查是否有可用的图数据库"""
        return self.use_neo4j or self.use_local
    
    @property
    def backend_type(self) -> str:
        """返回当前使用的后端类型"""
        if self.use_neo4j and self.use_local:
            return "both"
        elif self.use_neo4j:
            return "neo4j"
        elif self.use_local:
            return "local"
        else:
            return "none"
    
    def clear_database(self):
        """清空所有数据库"""
        if self.use_neo4j:
            self.neo4j_service.clear_database()
            logger.info("Neo4j database cleared")
        
        if self.use_local:
            self.local_service.clear_database()
            logger.info("Local database cleared")
    
    def create_class_node(self, tx_or_data, class_data=None):
        """
        创建类节点
        支持两种调用方式：
        1. Neo4j 事务方式: create_class_node(tx, class_data)
        2. 直接调用方式: create_class_node(class_data)
        """
        # 判断调用方式
        if class_data is None:
            # 直接调用方式
            class_data = tx_or_data
            tx = None
        else:
            # Neo4j 事务方式
            tx = tx_or_data
        
        results = {}
        
        # Neo4j 存储
        if self.use_neo4j:
            try:
                if tx is not None:
                    # 在事务中调用
                    result = self.neo4j_service.create_class_node(tx, class_data)
                else:
                    # 直接调用，需要创建会话
                    with self.neo4j_service.driver.session() as session:
                        result = session.execute_write(
                            self.neo4j_service.create_class_node, 
                            class_data
                        )
                results['neo4j'] = result
            except Exception as e:
                logger.error(f"Failed to create class node in Neo4j: {e}")
                results['neo4j'] = {'error': str(e)}
        
        # 本地存储
        if self.use_local:
            try:
                result = self.local_service.create_class_node(class_data)
                results['local'] = result
            except Exception as e:
                logger.error(f"Failed to create class node locally: {e}")
                results['local'] = {'error': str(e)}
        
        return results
    
    def create_method_node(self, method_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建方法节点"""
        results = {}
        
        if self.use_local:
            try:
                result = self.local_service.create_method_node(method_data)
                results['local'] = result
            except Exception as e:
                logger.error(f"Failed to create method node locally: {e}")
                results['local'] = {'error': str(e)}
        
        # Neo4j 的方法节点创建逻辑在 import_service 中处理
        
        return results
    
    def create_relationship(self, from_node: str, to_node: str, 
                          rel_type: str, properties: Optional[Dict] = None) -> Dict[str, Any]:
        """创建节点关系"""
        results = {}
        
        if self.use_local:
            try:
                result = self.local_service.create_relationship(
                    from_node, to_node, rel_type, properties
                )
                results['local'] = result
            except Exception as e:
                logger.error(f"Failed to create relationship locally: {e}")
                results['local'] = {'error': str(e)}
        
        return results
    
    def get_class_graph(self, class_name: str) -> Dict[str, Any]:
        """获取类的图数据"""
        # 优先使用 Neo4j
        if self.use_neo4j:
            try:
                return self.neo4j_service.get_class_graph(class_name)
            except Exception as e:
                logger.warning(f"Failed to get class graph from Neo4j: {e}")
        
        # 降级使用本地图数据库
        if self.use_local:
            try:
                return self.local_service.get_class_graph(class_name)
            except Exception as e:
                logger.error(f"Failed to get class graph locally: {e}")
        
        return {'nodes': [], 'edges': []}
    
    def get_full_graph(self) -> Dict[str, Any]:
        """获取完整图数据"""
        # 优先使用 Neo4j
        if self.use_neo4j:
            try:
                return self.neo4j_service.get_full_graph()
            except Exception as e:
                logger.warning(f"Failed to get full graph from Neo4j: {e}")
        
        # 降级使用本地图数据库
        if self.use_local:
            try:
                return self.local_service.get_full_graph()
            except Exception as e:
                logger.error(f"Failed to get full graph locally: {e}")
        
        return {'nodes': [], 'edges': []}
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            'backend': self.backend_type,
            'neo4j': None,
            'local': None,
        }
        
        if self.use_neo4j:
            try:
                stats['neo4j'] = self.neo4j_service.get_statistics()
            except Exception as e:
                stats['neo4j'] = {'error': str(e)}
        
        if self.use_local:
            try:
                stats['local'] = self.local_service.get_statistics()
            except Exception as e:
                stats['local'] = {'error': str(e)}
        
        return stats
    
    def save(self):
        """保存数据"""
        if self.use_local:
            self.local_service.save()
    
    def close(self):
        """关闭所有连接"""
        if self.use_neo4j:
            self.neo4j_service.close()
        
        if self.use_local:
            self.local_service.close()
    
    def export_local_graph(self, format='json', output_file=None) -> Optional[str]:
        """导出本地图数据"""
        if not self.use_local:
            logger.error("Local graph service not available")
            return None
        
        try:
            if format == 'json':
                return self.local_service.export_to_json(output_file)
            elif format == 'gexf':
                return self.local_service.export_to_gexf(output_file)
            else:
                logger.error(f"Unsupported export format: {format}")
                return None
        except Exception as e:
            logger.error(f"Failed to export graph: {e}")
            return None


# 全局统一服务实例
unified_graph_service = UnifiedGraphService()
