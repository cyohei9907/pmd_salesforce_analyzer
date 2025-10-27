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
            
            # 创建子目录（保留用于导出）
            (self.graph_data_dir / 'graphs').mkdir(exist_ok=True)
            (self.graph_data_dir / 'exports').mkdir(exist_ok=True)
            
            # 初始化分离的实体和关系文件
            self.entities_file = self.graph_data_dir / 'entities.json'
            self.relations_file = self.graph_data_dir / 'relations.json'
            
            if not self.entities_file.exists():
                self._save_entities({})
            
            if not self.relations_file.exists():
                self._save_relations([])
            
            self.connected = True
            logger.info(f"Local graph database initialized at: {self.graph_data_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize directories: {e}")
            self.connected = False
    
    def _load_graph(self):
        """从文件加载图数据"""
        # 优先尝试从分离的 JSON 文件加载
        if self.entities_file.exists() and self.relations_file.exists():
            try:
                entities = self._load_entities()
                relations = self._load_relations()
                
                # 添加所有节点
                for node_id, node_info in entities.items():
                    attrs = node_info.get('attributes', {})
                    self.graph.add_node(node_id, **attrs)
                
                # 添加所有边
                for relation in relations:
                    from_node = relation.get('from')
                    to_node = relation.get('to')
                    rel_type = relation.get('type', 'RELATED_TO')
                    properties = relation.get('properties', {})
                    
                    if from_node and to_node:
                        # 避免 type 参数冲突：从 properties 中移除 type 键
                        edge_props = {k: v for k, v in properties.items() if k != 'type'}
                        edge_props['type'] = rel_type
                        self.graph.add_edge(from_node, to_node, **edge_props)
                
                logger.info(f"Loaded graph from separate files with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
                return
            except Exception as e:
                logger.warning(f"Failed to load graph from separate files: {e}")
        
        # 降级：尝试从 gpickle 文件加载
        graph_file = self.graph_data_dir / 'graphs' / 'main_graph.gpickle'
        if graph_file.exists():
            try:
                self.graph = nx.read_gpickle(graph_file)
                logger.info(f"Loaded graph from pickle with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
            except Exception as e:
                logger.warning(f"Failed to load graph from pickle: {e}, starting with empty graph")
    
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
        # 清空分离的数据文件
        self._save_entities({})
        self._save_relations([])
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
        """保存实体到 entities.json"""
        try:
            # 读取现有实体
            entities = self._load_entities()
            
            # 更新实体
            entities[node_id] = {
                'node_id': node_id,
                'attributes': attributes
            }
            
            # 保存回文件
            self._save_entities(entities)
        except Exception as e:
            logger.error(f"Failed to save entity {node_id}: {e}")
    
    def _save_relation(self, from_node: str, to_node: str, 
                      rel_type: str, properties: Dict[str, Any]):
        """保存关系到 relations.json"""
        try:
            # 读取现有关系
            relations = self._load_relations()
            
            # 添加关系（检查是否已存在）
            relation = {
                'from': from_node,
                'to': to_node,
                'type': rel_type,
                'properties': properties
            }
            
            # 检查是否已存在相同的关系
            relation_key = f"{from_node}|{to_node}|{rel_type}"
            existing = False
            for i, rel in enumerate(relations):
                if f"{rel['from']}|{rel['to']}|{rel['type']}" == relation_key:
                    relations[i] = relation
                    existing = True
                    break
            
            if not existing:
                relations.append(relation)
            
            # 保存回文件
            self._save_relations(relations)
        except Exception as e:
            logger.error(f"Failed to save relation {from_node} -> {to_node}: {e}")
    
    def _load_entities(self) -> Dict[str, Any]:
        """从 entities.json 加载实体"""
        try:
            if self.entities_file.exists():
                with open(self.entities_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('entities', {})
        except Exception as e:
            logger.error(f"Failed to load entities: {e}")
        return {}
    
    def _save_entities(self, entities: Dict[str, Any]):
        """保存实体到 entities.json"""
        try:
            # 添加元数据
            output_data = {
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'total_entities': len(entities)
                },
                'entities': entities
            }
            
            with open(self.entities_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved {len(entities)} entities to {self.entities_file}")
        except Exception as e:
            logger.error(f"Failed to save entities: {e}")
    
    def _load_relations(self) -> List[Dict[str, Any]]:
        """从 relations.json 加载关系"""
        try:
            if self.relations_file.exists():
                with open(self.relations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('relations', [])
        except Exception as e:
            logger.error(f"Failed to load relations: {e}")
        return []
    
    def _save_relations(self, relations: List[Dict[str, Any]]):
        """保存关系到 relations.json"""
        try:
            # 添加元数据
            output_data = {
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'total_relations': len(relations)
                },
                'relations': relations
            }
            
            with open(self.relations_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved {len(relations)} relations to {self.relations_file}")
        except Exception as e:
            logger.error(f"Failed to save relations: {e}")
    
    def get_class_graph(self, class_name: str) -> Dict[str, Any]:
        """获取特定类的图数据"""
        class_node = f"class:{class_name}"
        
        if class_node not in self.graph:
            return {'nodes': [], 'edges': []}
        
        # 获取类节点和其所有相关节点
        nodes = []
        edges = []
        
        # 添加类节点，转换为统一格式
        class_node_data = self.graph.nodes[class_node]
        node_type = class_node_data.get('type', 'Unknown')
        nodes.append({
            'id': class_node,
            'labels': [node_type],
            'properties': {k: v for k, v in class_node_data.items() if k != 'type'}
        })
        
        # 获取所有相关节点和边
        for neighbor in self.graph.neighbors(class_node):
            neighbor_data = self.graph.nodes[neighbor]
            neighbor_type = neighbor_data.get('type', 'Unknown')
            nodes.append({
                'id': neighbor,
                'labels': [neighbor_type],
                'properties': {k: v for k, v in neighbor_data.items() if k != 'type'}
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
        seen_edges = set()  # 用于跟踪已见过的边，避免重复
        
        # 获取所有节点
        for node_id, node_data in self.graph.nodes(data=True):
            # 转换为统一格式，兼容 Neo4j 返回的结构
            node_type = node_data.get('type', 'Unknown')
            nodes.append({
                'id': node_id,
                'labels': [node_type],  # 统一使用 labels 列表
                'properties': {k: v for k, v in node_data.items() if k != 'type'}  # 除 type 外的所有属性
            })
        
        # 获取所有边（去重）
        for source, target, key, edge_data in self.graph.edges(keys=True, data=True):
            # 创建边的唯一标识符
            edge_type = edge_data.get('type', key)
            edge_key = (source, target, edge_type)
            
            # 如果这条边还没有添加过，则添加
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                edges.append({
                    'source': source,
                    'target': target,
                    'type': edge_type,
                    **{k: v for k, v in edge_data.items() if k != 'type'}
                })
        
        return {'nodes': nodes, 'edges': edges}
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取图数据库统计信息"""
        class_count = sum(1 for n, d in self.graph.nodes(data=True) 
                         if d.get('type') == 'ApexClass')
        method_count = sum(1 for n, d in self.graph.nodes(data=True) 
                          if d.get('type') == 'ApexMethod')
        soql_count = sum(1 for n, d in self.graph.nodes(data=True) 
                        if d.get('type') == 'SOQLQuery')
        dml_count = sum(1 for n, d in self.graph.nodes(data=True) 
                       if d.get('type') == 'DMLOperation')
        
        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'classes': class_count,
            'methods': method_count,
            'soqls': soql_count,
            'dmls': dml_count,
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
