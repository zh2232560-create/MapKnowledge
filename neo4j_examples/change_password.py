"""
Neo4j 初次密码修改脚本
使用默认密码 neo4j/neo4j 登录并修改为新密码
"""
from neo4j import GraphDatabase

OLD_PASSWORD = "neo4j"
NEW_PASSWORD = "5211314zhg"
URI = "bolt://localhost:7687"

try:
    driver = GraphDatabase.driver(URI, auth=("neo4j", OLD_PASSWORD))
    # 使用 system 数据库修改密码（适用于密码过期情况）
    with driver.session(database="system") as session:
        session.run(f"ALTER CURRENT USER SET PASSWORD FROM '{OLD_PASSWORD}' TO '{NEW_PASSWORD}'")
    driver.close()
    print(f"✅ 密码已成功修改为: {NEW_PASSWORD}")
    print("现在可以运行 neo4j_test.py 了")
except Exception as e:
    print(f"❌ 密码修改失败: {e}")
    print("\n可能原因:")
    print("1. 密码已经修改过（直接运行 neo4j_test.py 试试）")
    print("2. Neo4j 服务未启动（运行 start_neo4j.bat）")
    print("3. 需要在浏览器手动修改: http://localhost:7474")
