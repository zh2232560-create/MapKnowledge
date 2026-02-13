import os
import random
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "5211314zhg")

LABEL = "DemoNode"


def main():
    if not PASSWORD:
        raise SystemExit("环境变量 NEO4J_PASSWORD 未设置，请先设置再运行。")

    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    suffix = random.randint(1000, 999999)
    name = f"sample-{suffix}"

    with driver.session() as session:
        # 创建一个演示节点
        session.execute_write(lambda tx: tx.run(
            f"CREATE (n:{LABEL} {{name: $name}}) RETURN n",
            name=name,
        ).consume())

        # 统计该标签下的节点数量
        result = session.execute_read(lambda tx: tx.run(
            f"MATCH (n:{LABEL}) RETURN count(n) AS cnt"
        ).single())

        print(f"{LABEL} 节点数量: {result['cnt']}")

        # 清理刚创建的演示节点
        session.execute_write(lambda tx: tx.run(
            f"MATCH (n:{LABEL} {{name: $name}}) DETACH DELETE n",
            name=name,
        ).consume())

    driver.close()
    print("连接测试完成 ✅")


if __name__ == "__main__":
    main()
