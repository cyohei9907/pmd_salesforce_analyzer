"""
本地图数据库服务
使用 NetworkX 作为轻量级的图数据库替代方案
支持将 AST 数据存储到本地文件系统
"""
import os
import json
import pickle
from pathlib import Path
from datetime import datetime
import networkx as nx
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LocalGraphService:
    """本地图数据库服务"""
    
    def __init__(self, graph_data_dir='graphdata'):
        """
        初始化本地图数据库服务
        
        Args:
            graph_data_dir: 图数据存储目录
        """
        self.graph_data_dir = Path(graph_data_dir)
        self.graph = nx.MultiDiGraph()  # 支持多重有向图
        self.connected = False
        
        # 创建必要的目录结构
        self._init_directories()
        
        # 尝试加载已存在的图数据
        self._load_graph()
    
    def _init_directories(self):
        """初始化目录结构"""
        try:
            # 创建主目录
            self.graph_data_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建子目录
            (self.graph_data_dir / 'entities').mkdir(exist_ok=True)
            (self.graph_data_dir / 'relations').mkdir(exist_ok=True)
            (self.graph_data_dir / 'graphs').mkdir(exist_ok=True)
            (self.graph_data_dir / 'exports').mkdir(exist_ok=True)
            
            self.connected = True
            logger.info(f"Local graph database initialized at: {self.graph_data_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize directories: {e}")
            self.connected = False
    
    def _load_graph(self):
        """从文件加载图数据"""
        graph_file = self.graph_data_dir / 'graphs' / 'main_graph.gpickle'
        if graph_file.exists():
            try:
                self.graph = nx.read_gpickle(graph_file)
                logger.info(f"Loaded graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
            except Exception as e:
                logger.warning(f"Failed to load graph: {e}, starting with empty graph")
    
    def _save_graph(self):
        """保存图数据到文件"""
        try:
            graph_file = self.graph_data_dir / 'graphs' / 'main_graph.gpickle'
            nx.write_gpickle(self.graph, graph_file)
            logger.info(f"Saved graph with {self.graph.number_of_nodes()} nodes")
        except Exception as e:
            logger.error(f"Failed to save graph: {e}")
    
    def clear_database(self):
        """清空数据库"""
        self.graph.clear()
        self._save_graph()
        logger.info("Database cleared")
    
    def create_class_node(self, class_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建类节点
        
        Args:
            class_data: 类数据字典
        
        Returns:
            创建的节点信息
        """
        node_id = f"class:{class_data['name']}"
        
        # 添加节点属性
        node_attrs = {
            'type': 'ApexClass',
            'name': class_data['name'],
            'simpleName': class_data.get('simpleName', ''),
            'definingType': class_data.get('definingType', ''),
            'public': class_data.get('public', False),
            'withSharing': class_data.get('withSharing', False),
            'fileName': class_data.get('fileName', ''),
            'created_at': datetime.now().isoformat(),
        }
        
        self.graph.add_node(node_id, **node_attrs)
        
        # 保存实体文件
        self._save_entity(node_id, node_attrs)
        
        return {'node_id': node_id, 'attributes': node_attrs}
    
    def create_method_node(self, method_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建方法节点
        
        Args:
            method_data: 方法数据字典
        
        Returns:
            创建的节点信息
        """
        node_id = f"method:{method_data['canonicalName']}"
        
        node_attrs = {
            'type': 'ApexMethod',
            'canonicalName': method_data['canonicalName'],
            'className': method_data.get('className', ''),
            'name': method_data['name'],
            'public': method_data.get('public', False),
            'static': method_data.get('static', False),
            'returnType': method_data.get('returnType', 'void'),
            'arity': method_data.get('arity', 0),
            'created_at': datetime.now().isoformat(),
        }
        
        self.graph.add_node(node_id, **node_attrs)
        self._save_entity(node_id, node_attrs)
        
        return {'node_id': node_id, 'attributes': node_attrs}
    
    def create_relationship(self, from_node: str, to_node: str, 
                          rel_type: str, properties: Optional[Dict] = None) -> Dict[str, Any]:
        """
        创建节点之间的关系
        
        Args:
            from_node: 起始节点ID
            to_node: 目标节点ID
            rel_type: 关系类型
            properties: 关系属性
        
        Returns:
            创建的关系信息
        """
        if properties is None:
            properties = {}
        
        properties['type'] = rel_type
        properties['created_at'] = datetime.now().isoformat()
        
        self.graph.add_edge(from_node, to_node, key=rel_type, **properties)
        
        # 保存关系文件
        self._save_relation(from_node, to_node, rel_type, properties)
        
        return {
            'from': from_node,
            'to': to_node,
            'type': rel_type,
            'properties': properties
        }
    
    def _save_entity(self, node_id: str, attributes: Dict[str, Any]):
        """保存实体到文件"""
        try:
            # 使用节点类型和名称创建文件名
            node_type = attributes.get('type', 'Unknown')
            safe_name = node_id.replace(':', '_').replace('/', '_')
            
            entity_file = self.graph_data_dir / 'entities' / f"{node_type}_{safe_name}.json"
            
            with open(entity_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'node_id': node_id,
                    'attributes': attributes
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save entity {node_id}: {e}")
    
    def _save_relation(self, from_node: str, to_node: str, 
                      rel_type: str, properties: Dict[str, Any]):
        """保存关系到文件"""
        try:
            safe_from = from_node.replace(':', '_').replace('/', '_')
            safe_to = to_node.replace(':', '_').replace('/', '_')
            
            relation_file = self.graph_data_dir / 'relations' / \
                           f"{safe_from}__{rel_type}__{safe_to}.json"
            
            with open(relation_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'from_node': from_node,
                    'to_node': to_node,
                    'type': rel_type,
                    'properties': properties
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save relation: {e}")
    
    def get_class_graph(self, class_name: str) -> Dict[str, Any]:
        """获取特定类的图数据"""
        class_node = f"class:{class_name}"
        
        if class_node not in self.graph:
            return {'nodes': [], 'edges': []}
        
        # 获取类节点和其所有相关节点
        nodes = []
        edges = []
        
        # 添加类节点
        nodes.append({
            'id': class_node,
            **self.graph.nodes[class_node]
        })
        
        # 获取所有相关节点和边
        for neighbor in self.graph.neighbors(class_node):
            nodes.append({
                'id': neighbor,
                **self.graph.nodes[neighbor]
            })
            
            # 获取所有边
            for key, edge_data in self.graph[class_node][neighbor].items():
                edges.append({
                    'source': class_node,
                    'target': neighbor,
                    'type': edge_data.get('type', key),
                    **edge_data
                })
        
        return {'nodes': nodes, 'edges': edges}
    
    def get_full_graph(self) -> Dict[str, Any]:
        """获取完整图数据"""
        nodes = []
        edges = []
        
        # 获取所有节点
        for node_id, node_data in self.graph.nodes(data=True):
            nodes.append({
                'id': node_id,
                **node_data
            })
        
        # 获取所有边
        for source, target, key, edge_data in self.graph.edges(keys=True, data=True):
            edges.append({
                'source': source,
                'target': target,
                'type': edge_data.get('type', key),
                **edge_data
            })
        
        return {'nodes': nodes, 'edges': edges}
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取图数据库统计信息"""
        class_count = sum(1 for n, d in self.graph.nodes(data=True) 
                         if d.get('type') == 'ApexClass')
        method_count = sum(1 for n, d in self.graph.nodes(data=True) 
                          if d.get('type') == 'ApexMethod')
        
        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'class_count': class_count,
            'method_count': method_count,
            'is_connected': nx.is_weakly_connected(self.graph) if self.graph.number_of_nodes() > 0 else False,
            'storage_path': str(self.graph_data_dir.absolute()),
        }
    
    def export_to_json(self, output_file: Optional[str] = None) -> str:
        """导出图数据为JSON格式"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.graph_data_dir / 'exports' / f'graph_export_{timestamp}.json'
        else:
            output_file = Path(output_file)
        
        graph_data = self.get_full_graph()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported graph to: {output_file}")
        return str(output_file)
    
    def export_to_gexf(self, output_file: Optional[str] = None) -> str:
        """导出图数据为GEXF格式（可用于Gephi等工具）"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.graph_data_dir / 'exports' / f'graph_export_{timestamp}.gexf'
        else:
            output_file = Path(output_file)
        
        nx.write_gexf(self.graph, output_file)
        logger.info(f"Exported graph to GEXF: {output_file}")
        return str(output_file)
    
    def import_from_json(self, json_file: str):
        """从JSON文件导入图数据"""
        with open(json_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
        
        # 添加节点
        for node in graph_data.get('nodes', []):
            node_id = node.pop('id')
            self.graph.add_node(node_id, **node)
        
        # 添加边
        for edge in graph_data.get('edges', []):
            source = edge.pop('source')
            target = edge.pop('target')
            edge_type = edge.pop('type', 'RELATES_TO')
            self.graph.add_edge(source, target, key=edge_type, **edge)
        
        self._save_graph()
        logger.info(f"Imported graph from: {json_file}")
    
    def save(self):
        """手动保存图数据"""
        self._save_graph()
    
    def close(self):
        """关闭服务，保存数据"""
        self._save_graph()
        logger.info("Local graph service closed")


# 全局实例
local_graph_service = LocalGraphService()
