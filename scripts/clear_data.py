"""
清空 Neo4j 数据库脚本
删除所有节点和关系，但保留 Schema（约束和索引）
"""
import os
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "5211314zhg")


def clear_all_data(driver):
    """删除所有节点和关系"""
    with driver.session() as session:
        # 获取当前节点和关系数量
        result = session.run("MATCH (n) RETURN count(n) as node_count")
        node_count = result.single()["node_count"]
        
        result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
        rel_count = result.single()["rel_count"]
        
        print(f"\n当前数据库状态:")
        print(f"  节点数: {node_count}")
        print(f"  关系数: {rel_count}")
        
        if node_count == 0 and rel_count == 0:
            print("\n✓ 数据库已经是空的")
            return
        
        # 确认删除
        print(f"\n⚠️  即将删除所有数据（{node_count} 个节点，{rel_count} 个关系）")
        confirm = input("确认删除？(yes/no): ")
        
        if confirm.lower() != 'yes':
            print("✗ 操作已取消")
            return
        
        # 删除所有节点和关系
        print("\n正在删除数据...")
        session.run("MATCH (n) DETACH DELETE n")
        
        # 验证删除
        result = session.run("MATCH (n) RETURN count(n) as count")
        final_count = result.single()["count"]
        
        if final_count == 0:
            print("✓ 所有数据已成功删除")
        else:
            print(f"✗ 删除未完成，剩余 {final_count} 个节点")


def show_schema_info(driver):
    """显示保留的 Schema 信息"""
    print("\n保留的 Schema 信息:")
    
    with driver.session() as session:
        # 查看约束
        result = session.run("SHOW CONSTRAINTS")
        constraints = [record for record in result]
        print(f"\n  约束数量: {len(constraints)}")
        for i, constraint in enumerate(constraints[:5], 1):
            print(f"    {i}. {constraint.get('name', 'N/A')}")
        if len(constraints) > 5:
            print(f"    ... 还有 {len(constraints) - 5} 个约束")
        
        # 查看索引
        result = session.run("SHOW INDEXES")
        indexes = [record for record in result]
        print(f"\n  索引数量: {len(indexes)}")
        for i, index in enumerate(indexes[:5], 1):
            print(f"    {i}. {index.get('name', 'N/A')}")
        if len(indexes) > 5:
            print(f"    ... 还有 {len(indexes) - 5} 个索引")


def main():
    print("=" * 60)
    print("Neo4j 数据库清空工具")
    print("=" * 60)
    
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    
    try:
        # 清空数据
        clear_all_data(driver)
        
        # 显示保留的 Schema
        show_schema_info(driver)
        
    finally:
        driver.close()
    
    print("\n" + "=" * 60)
    print("✅ 操作完成！")
    print("=" * 60)
    print("\n提示:")
    print("  - Schema（约束和索引）已保留")
    print("  - 可以重新导入数据: python .\\scripts\\import_data.py .\\data\\exam_data.json")


if __name__ == "__main__":
    main()
