"""
简易图谱可视化工具（文本版）
在命令行中以 ASCII 图形显示节点和关系
"""
import os
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "5211314zhg")


class TextGraphVisualizer:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def visualize_person_network(self, person_name):
        """可视化某人的社交网络"""
        query = """
        MATCH path = (p:Person {name: $name})-[:KNOWS*1..2]-(friend:Person)
        RETURN p, friend, length(path) as distance
        """
        
        with self.driver.session() as session:
            result = session.run(query, name=person_name)
            
            print(f"\n{'='*60}")
            print(f"{person_name} 的社交网络")
            print('='*60)
            
            direct = []
            indirect = []
            
            for record in result:
                friend = record["friend"]["name"]
                distance = record["distance"]
                
                if distance == 1:
                    direct.append(friend)
                else:
                    indirect.append(friend)
            
            # 绘制
            print(f"\n        {person_name}")
            print("          |")
            
            if direct:
                print("    ┌─────┴─────┐")
                for i, friend in enumerate(direct):
                    if i < len(direct) - 1:
                        print(f"    {friend}     ", end="")
                    else:
                        print(friend)
            
            if indirect:
                print("\n  间接联系（2度）:")
                for friend in indirect:
                    print(f"    → {friend}")
    
    def visualize_org_structure(self, org_name):
        """可视化组织结构"""
        query = """
        MATCH (p:Person)-[r:WORKS_FOR]->(o:Organization {name: $name})
        RETURN p.name as name, r.position as position
        ORDER BY r.start_date
        """
        
        with self.driver.session() as session:
            result = session.run(query, name=org_name)
            
            print(f"\n{'='*60}")
            print(f"{org_name} 组织架构")
            print('='*60)
            print(f"\n    ┌─ {org_name} ─┐")
            
            for record in result:
                name = record["name"]
                position = record["position"]
                print(f"    │")
                print(f"    ├─ {name} ({position})")
    
    def visualize_concept_relations(self, concept_name):
        """可视化概念关系图"""
        query = """
        MATCH (c:Concept {name: $name})-[r:RELATED_TO]-(related:Concept)
        RETURN related.name as concept, type(r) as rel_type, r.type as description
        """
        
        with self.driver.session() as session:
            result = session.run(query, name=concept_name)
            
            print(f"\n{'='*60}")
            print(f"{concept_name} 相关概念图")
            print('='*60)
            
            print(f"\n        {concept_name}")
            
            for record in result:
                concept = record["concept"]
                desc = record["description"]
                print(f"          |")
                print(f"          | ({desc})")
                print(f"          ↓")
                print(f"        {concept}")
    
    def show_full_graph_summary(self):
        """显示完整图谱摘要"""
        with self.driver.session() as session:
            # 节点统计
            nodes_result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(*) as count
                ORDER BY count DESC
            """)
            
            # 关系统计
            rels_result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(*) as count
                ORDER BY count DESC
            """)
            
            print(f"\n{'='*60}")
            print("知识图谱概览")
            print('='*60)
            
            print("\n📊 节点类型:")
            for record in nodes_result:
                label = record["label"]
                count = record["count"]
                bar = "█" * min(count * 5, 40)
                print(f"  {label:15} {bar} {count}")
            
            print("\n🔗 关系类型:")
            for record in rels_result:
                rel_type = record["type"]
                count = record["count"]
                bar = "─" * min(count * 5, 40)
                print(f"  {rel_type:15} {bar} {count}")
    
    def show_menu(self):
        """显示交互菜单"""
        while True:
            print("\n" + "="*60)
            print("知识图谱可视化工具")
            print("="*60)
            print("1. 查看图谱概览")
            print("2. 查看人物社交网络")
            print("3. 查看组织架构")
            print("4. 查看概念关系图")
            print("5. 退出")
            print("="*60)
            
            choice = input("\n请选择 (1-5): ").strip()
            
            if choice == '1':
                self.show_full_graph_summary()
            
            elif choice == '2':
                name = input("输入人物姓名: ").strip()
                self.visualize_person_network(name)
            
            elif choice == '3':
                org = input("输入组织名称: ").strip()
                self.visualize_org_structure(org)
            
            elif choice == '4':
                concept = input("输入概念名称: ").strip()
                self.visualize_concept_relations(concept)
            
            elif choice == '5':
                print("再见！")
                break
            
            else:
                print("无效选择，请重试")


def main():
    viz = TextGraphVisualizer(URI, USER, PASSWORD)
    
    # 快速演示
    print("="*60)
    print("知识图谱快速预览")
    print("="*60)
    
    viz.show_full_graph_summary()
    viz.visualize_person_network("张三")
    viz.visualize_org_structure("TechCorp")
    viz.visualize_concept_relations("知识图谱")
    
    # 交互模式
    print("\n按回车继续进入交互模式，或 Ctrl+C 退出...")
    try:
        input()
        viz.show_menu()
    except KeyboardInterrupt:
        print("\n再见！")
    
    viz.close()


if __name__ == "__main__":
    main()
