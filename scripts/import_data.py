"""
批量导入知识图谱数据
支持从 JSON/CSV 文件导入节点和关系
"""
import os
import json
from typing import List, Dict
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "5211314zhg")


class KnowledgeGraphImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def import_nodes(self, label: str, nodes: List[Dict]):
        """批量导入节点"""
        if not nodes:
            return 0
        
        # 动态构建 MERGE 语句
        query = f"""
        UNWIND $nodes AS node
        MERGE (n:{label} {{id: node.id}})
        SET n += node
        RETURN count(n) as count
        """
        
        with self.driver.session() as session:
            result = session.run(query, nodes=nodes)
            count = result.single()["count"]
            print(f"✓ 导入 {count} 个 {label} 节点")
            return count
    
    def import_relationships(self, rel_type: str, relationships: List[Dict]):
        """
        批量导入关系
        relationships 格式: [
            {"from_id": "id1", "from_label": "Person", "to_id": "id2", "to_label": "Organization", "properties": {...}},
            ...
        ]
        """
        if not relationships:
            return 0
        
        query = f"""
        UNWIND $rels AS rel
        MATCH (a {{id: rel.from_id}})
        MATCH (b {{id: rel.to_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += rel.properties
        RETURN count(r) as count
        """
        
        with self.driver.session() as session:
            result = session.run(query, rels=relationships)
            count = result.single()["count"]
            print(f"✓ 导入 {count} 个 {rel_type} 关系")
            return count
    
    def import_from_json(self, filepath: str):
        """从 JSON 文件导入数据"""
        print(f"\n从 {filepath} 导入数据...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 导入节点
        if 'nodes' in data:
            nodes_list = data['nodes']
            if isinstance(nodes_list, list):
                # 新格式: nodes是数组，每个节点有label字段
                nodes_by_label = {}
                for node in nodes_list:
                    label = node.get('label', 'Node')
                    if label not in nodes_by_label:
                        nodes_by_label[label] = []
                    nodes_by_label[label].append(node.get('properties', {}))
                
                for label, nodes in nodes_by_label.items():
                    self.import_nodes(label, nodes)
            else:
                # 旧格式: nodes是字典
                for label, nodes in nodes_list.items():
                    self.import_nodes(label, nodes)
        
        # 导入关系
        if 'relationships' in data:
            rels_list = data['relationships']
            if isinstance(rels_list, list):
                # 新格式: relationships是数组
                rels_by_type = {}
                for rel in rels_list:
                    rel_type = rel.get('type', 'RELATED_TO')
                    if rel_type not in rels_by_type:
                        rels_by_type[rel_type] = []
                    
                    # 构建关系数据
                    start_node = rel.get('start_node', {})
                    end_node = rel.get('end_node', {})
                    rel_data = {
                        'from_id': start_node.get('value'),
                        'to_id': end_node.get('value'),
                        'properties': rel.get('properties', {})
                    }
                    rels_by_type[rel_type].append(rel_data)
                
                for rel_type, rels in rels_by_type.items():
                    self.import_relationships(rel_type, rels)
            else:
                # 旧格式: relationships是字典
                for rel_type, rels in rels_list.items():
                    self.import_relationships(rel_type, rels)
    
    def clear_database(self):
        """清空数据库（谨慎使用）"""
        confirm = input("⚠️  确定要清空整个数据库吗？(yes/no): ")
        if confirm.lower() == 'yes':
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
                print("✓ 数据库已清空")
        else:
            print("✗ 操作已取消")


def main():
    import sys
    
    print("=" * 60)
    print("知识图谱数据导入工具")
    print("=" * 60)
    
    importer = KnowledgeGraphImporter(URI, USER, PASSWORD)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        if os.path.exists(json_file):
            importer.import_from_json(json_file)
        else:
            print(f"✗ 文件不存在: {json_file}")
    else:
        # 使用默认示例数据
        default_file = "data/sample_data.json"
        if os.path.exists(default_file):
            importer.import_from_json(default_file)
        else:
            print(f"✗ 未找到默认数据文件: {default_file}")
            print("使用方法: python import_data.py <json文件路径>")
    
    importer.close()
    
    print("\n" + "=" * 60)
    print("✅ 数据导入完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
