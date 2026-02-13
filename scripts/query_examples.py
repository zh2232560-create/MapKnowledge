"""
知识图谱查询示例
展示常见的图查询场景
"""
import os
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "5211314zhg")


class KnowledgeGraphQuery:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def execute_query(self, query, params=None):
        """执行查询并返回结果"""
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]
    
    def find_person_by_name(self, name):
        """1. 查找特定人物"""
        query = """
        MATCH (p:Person {name: $name})
        RETURN p.id as id, p.name as name, p.occupation as occupation, p.description as description
        """
        return self.execute_query(query, {"name": name})
    
    def find_person_colleagues(self, person_name):
        """2. 查找某人的同事（同公司工作的人）"""
        query = """
        MATCH (p:Person {name: $name})-[:WORKS_FOR]->(o:Organization)<-[:WORKS_FOR]-(colleague:Person)
        WHERE p <> colleague
        RETURN colleague.name as name, colleague.occupation as occupation, o.name as company
        """
        return self.execute_query(query, {"name": person_name})
    
    def find_person_network(self, person_name, depth=2):
        """3. 查找某人的社交网络（多跳关系）"""
        query = f"""
        MATCH path = (p:Person {{name: $name}})-[:KNOWS*1..{depth}]-(friend:Person)
        RETURN DISTINCT friend.name as name, length(path) as distance
        ORDER BY distance
        """
        return self.execute_query(query, {"name": person_name})
    
    def find_related_concepts(self, concept_name):
        """4. 查找相关概念"""
        query = """
        MATCH (c:Concept {name: $name})-[r:RELATED_TO]-(related:Concept)
        RETURN related.name as concept, r.type as relationship_type, related.category as category
        """
        return self.execute_query(query, {"name": concept_name})
    
    def find_concept_experts(self, concept_name):
        """5. 查找某概念的专家（创建相关文档的人）"""
        query = """
        MATCH (c:Concept {name: $name})<-[:MENTIONS]-(d:Document)<-[:CREATED]-(p:Person)
        RETURN p.name as expert, p.occupation as occupation, count(d) as documents_count
        ORDER BY documents_count DESC
        """
        return self.execute_query(query, {"name": concept_name})
    
    def find_shortest_path(self, person1, person2):
        """6. 查找两人之间的最短路径"""
        query = """
        MATCH path = shortestPath((p1:Person {name: $name1})-[*]-(p2:Person {name: $name2}))
        RETURN [node in nodes(path) | node.name] as path,
               [rel in relationships(path) | type(rel)] as relationships,
               length(path) as distance
        """
        return self.execute_query(query, {"name1": person1, "name2": person2})
    
    def find_organization_people(self, org_name):
        """7. 查找组织的所有员工"""
        query = """
        MATCH (p:Person)-[r:WORKS_FOR]->(o:Organization {name: $name})
        RETURN p.name as name, p.occupation as occupation, r.position as position, r.start_date as start_date
        ORDER BY r.start_date
        """
        return self.execute_query(query, {"name": org_name})
    
    def find_event_participants(self, event_name):
        """8. 查找事件的所有参与者"""
        query = """
        MATCH (p:Person)-[r:PARTICIPATED_IN]->(e:Event {name: $name})
        RETURN p.name as participant, r.role as role, p.occupation as occupation
        """
        return self.execute_query(query, {"name": event_name})
    
    def search_fulltext(self, search_term):
        """9. 全文搜索"""
        query = """
        CALL db.index.fulltext.queryNodes('person_fulltext', $term)
        YIELD node, score
        RETURN node.name as name, labels(node)[0] as type, score
        ORDER BY score DESC
        LIMIT 10
        """
        return self.execute_query(query, {"term": search_term})
    
    def get_graph_stats(self):
        """10. 获取图谱统计信息"""
        query = """
        MATCH (n)
        RETURN labels(n)[0] as label, count(*) as count
        ORDER BY count DESC
        """
        return self.execute_query(query)


def print_results(title, results):
    """格式化打印结果"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)
    if results:
        for i, record in enumerate(results, 1):
            print(f"{i}. {record}")
    else:
        print("(无结果)")


def main():
    print("=" * 60)
    print("知识图谱查询示例")
    print("=" * 60)
    
    kg = KnowledgeGraphQuery(URI, USER, PASSWORD)
    
    # 示例查询
    print_results("1. 查找人物：张三", kg.find_person_by_name("张三"))
    
    print_results("2. 查找张三的同事", kg.find_person_colleagues("张三"))
    
    print_results("3. 查找张三的社交网络", kg.find_person_network("张三", depth=3))
    
    print_results("4. 查找与'知识图谱'相关的概念", kg.find_related_concepts("知识图谱"))
    
    print_results("5. 查找'知识图谱'领域的专家", kg.find_concept_experts("知识图谱"))
    
    print_results("6. 查找张三和王五之间的最短路径", kg.find_shortest_path("张三", "王五"))
    
    print_results("7. 查找 TechCorp 的所有员工", kg.find_organization_people("TechCorp"))
    
    print_results("8. 查找'2024知识图谱技术峰会'的参与者", 
                  kg.find_event_participants("2024知识图谱技术峰会"))
    
    print_results("9. 图谱统计信息", kg.get_graph_stats())
    
    kg.close()
    
    print("\n" + "=" * 60)
    print("✅ 查询示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
