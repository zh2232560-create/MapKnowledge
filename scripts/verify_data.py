"""
验证数据库数据导入情况
"""
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "5211314zhg"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

with driver.session() as session:
    # 统计节点
    print("\n" + "="*50)
    print("节点统计:")
    print("="*50)
    result = session.run("MATCH (n) RETURN labels(n)[0] as label, count(n) as count ORDER BY label")
    total_nodes = 0
    for record in result:
        print(f"  {record['label']}: {record['count']}")
        total_nodes += record['count']
    print(f"\n  总计: {total_nodes} 个节点")
    
    # 统计关系
    print("\n" + "="*50)
    print("关系统计:")
    print("="*50)
    result = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(r) as count ORDER BY type")
    total_rels = 0
    for record in result:
        print(f"  {record['type']}: {record['count']}")
        total_rels += record['count']
    print(f"\n  总计: {total_rels} 个关系")
    
    # 查询示例：行测的知识树
    print("\n" + "="*50)
    print("示例查询: 行测知识树结构")
    print("="*50)
    result = session.run("""
        MATCH path = (s:Subject {name: '行测'})-[:HAS_MODULE]->(m:Module)
        RETURN s.name as subject, m.name as module
        ORDER BY m.order
    """)
    for record in result:
        print(f"  {record['subject']} -> {record['module']}")
    
    # 查询高频考点
    print("\n" + "="*50)
    print("示例查询: 高频考点")
    print("="*50)
    result = session.run("""
        MATCH (k:KnowledgePoint)-[:IS_TEST_POINT]->(tp:TestPoint)
        RETURN k.name as knowledge, tp.frequency as frequency
        ORDER BY tp.frequency DESC
        LIMIT 5
    """)
    for record in result:
        print(f"  {record['knowledge']}: 出现 {record['frequency']} 次")

driver.close()
print("\n" + "="*50)
print("验证完成!")
print("="*50)
