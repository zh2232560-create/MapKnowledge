"""
公考知识图谱 Schema 初始化脚本

功能:
1. 创建所有实体类型的唯一性约束
2. 创建常用属性的索引
3. 创建全文搜索索引
"""

from neo4j import GraphDatabase
import sys

# 数据库连接配置
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "5211314zhg"


class SchemaInitializer:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def close(self):
        self.driver.close()
    
    def create_constraints(self):
        """创建唯一性约束"""
        constraints = [
            "CREATE CONSTRAINT category_id IF NOT EXISTS FOR (c:Category) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT subject_id IF NOT EXISTS FOR (s:Subject) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT module_id IF NOT EXISTS FOR (m:Module) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT chapter_id IF NOT EXISTS FOR (c:Chapter) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT topic_id IF NOT EXISTS FOR (t:Topic) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT knowledge_id IF NOT EXISTS FOR (k:KnowledgePoint) REQUIRE k.id IS UNIQUE",
            "CREATE CONSTRAINT skill_id IF NOT EXISTS FOR (s:Skill) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT question_id IF NOT EXISTS FOR (q:Question) REQUIRE q.id IS UNIQUE",
            "CREATE CONSTRAINT resource_id IF NOT EXISTS FOR (r:Resource) REQUIRE r.id IS UNIQUE",
            "CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT testpoint_id IF NOT EXISTS FOR (t:TestPoint) REQUIRE t.id IS UNIQUE",
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    print(f"✓ 创建约束成功: {constraint.split('FOR')[1].split('REQUIRE')[0].strip()}")
                except Exception as e:
                    print(f"✗ 创建约束失败: {str(e)}")
    
    def create_indexes(self):
        """创建属性索引"""
        indexes = [
            "CREATE INDEX category_code IF NOT EXISTS FOR (c:Category) ON (c.code)",
            "CREATE INDEX category_name IF NOT EXISTS FOR (c:Category) ON (c.name)",
            "CREATE INDEX subject_code IF NOT EXISTS FOR (s:Subject) ON (s.code)",
            "CREATE INDEX subject_name IF NOT EXISTS FOR (s:Subject) ON (s.name)",
            "CREATE INDEX module_name IF NOT EXISTS FOR (m:Module) ON (m.name)",
            "CREATE INDEX module_code IF NOT EXISTS FOR (m:Module) ON (m.code)",
            "CREATE INDEX chapter_name IF NOT EXISTS FOR (c:Chapter) ON (c.name)",
            "CREATE INDEX chapter_code IF NOT EXISTS FOR (c:Chapter) ON (c.code)",
            "CREATE INDEX topic_name IF NOT EXISTS FOR (t:Topic) ON (t.name)",
            "CREATE INDEX topic_code IF NOT EXISTS FOR (t:Topic) ON (t.code)",
            "CREATE INDEX topic_difficulty IF NOT EXISTS FOR (t:Topic) ON (t.difficulty)",
            "CREATE INDEX knowledge_name IF NOT EXISTS FOR (k:KnowledgePoint) ON (k.name)",
            "CREATE INDEX knowledge_difficulty IF NOT EXISTS FOR (k:KnowledgePoint) ON (k.difficulty)",
            "CREATE INDEX knowledge_importance IF NOT EXISTS FOR (k:KnowledgePoint) ON (k.importance)",
            "CREATE INDEX knowledge_frequency IF NOT EXISTS FOR (k:KnowledgePoint) ON (k.frequency)",
            "CREATE INDEX skill_name IF NOT EXISTS FOR (s:Skill) ON (s.name)",
            "CREATE INDEX question_year IF NOT EXISTS FOR (q:Question) ON (q.year)",
            "CREATE INDEX question_exam_type IF NOT EXISTS FOR (q:Question) ON (q.exam_type)",
            "CREATE INDEX question_province IF NOT EXISTS FOR (q:Question) ON (q.province)",
            "CREATE INDEX question_difficulty IF NOT EXISTS FOR (q:Question) ON (q.difficulty)",
            "CREATE INDEX resource_type IF NOT EXISTS FOR (r:Resource) ON (r.type)",
            "CREATE INDEX resource_quality IF NOT EXISTS FOR (r:Resource) ON (r.quality)",
            "CREATE INDEX concept_name IF NOT EXISTS FOR (c:Concept) ON (c.name)",
            "CREATE INDEX testpoint_frequency IF NOT EXISTS FOR (t:TestPoint) ON (t.frequency)",
            "CREATE INDEX testpoint_importance IF NOT EXISTS FOR (t:TestPoint) ON (t.importance)",
        ]
        
        with self.driver.session() as session:
            for index in indexes:
                try:
                    session.run(index)
                    print(f"✓ 创建索引成功: {index.split('FOR')[1].split('ON')[0].strip()}")
                except Exception as e:
                    print(f"✗ 创建索引失败: {str(e)}")
    
    def create_fulltext_indexes(self):
        """创建全文搜索索引"""
        fulltext_indexes = [
            """
            CREATE FULLTEXT INDEX knowledge_content IF NOT EXISTS
            FOR (k:KnowledgePoint) ON EACH [k.name, k.content, k.definition]
            """,
            """
            CREATE FULLTEXT INDEX question_content IF NOT EXISTS
            FOR (q:Question) ON EACH [q.content, q.analysis]
            """,
            """
            CREATE FULLTEXT INDEX resource_content IF NOT EXISTS
            FOR (r:Resource) ON EACH [r.title]
            """,
            """
            CREATE FULLTEXT INDEX concept_content IF NOT EXISTS
            FOR (c:Concept) ON EACH [c.name, c.definition, c.explanation]
            """,
        ]
        
        with self.driver.session() as session:
            for index in fulltext_indexes:
                try:
                    session.run(index)
                    index_name = index.split("INDEX")[1].split("IF")[0].strip()
                    print(f"✓ 创建全文索引成功: {index_name}")
                except Exception as e:
                    print(f"✗ 创建全文索引失败: {str(e)}")
    
    def get_schema_info(self):
        """获取当前 Schema 信息"""
        with self.driver.session() as session:
            # 获取约束数量
            constraints_result = session.run("SHOW CONSTRAINTS")
            constraints = list(constraints_result)
            
            # 获取索引数量
            indexes_result = session.run("SHOW INDEXES")
            indexes = list(indexes_result)
            
            print("\n" + "="*50)
            print("当前 Schema 信息:")
            print("="*50)
            print(f"约束数量: {len(constraints)}")
            print(f"索引数量: {len(indexes)}")
            print("="*50)
    
    def initialize_all(self):
        """执行完整的 Schema 初始化"""
        print("开始初始化公考知识图谱 Schema...")
        print("\n[1/3] 创建唯一性约束...")
        self.create_constraints()
        
        print("\n[2/3] 创建属性索引...")
        self.create_indexes()
        
        print("\n[3/3] 创建全文搜索索引...")
        self.create_fulltext_indexes()
        
        print("\n初始化完成!")
        self.get_schema_info()


def main():
    initializer = SchemaInitializer(URI, USERNAME, PASSWORD)
    
    try:
        initializer.initialize_all()
    except Exception as e:
        print(f"\n❌ 初始化失败: {str(e)}")
        sys.exit(1)
    finally:
        initializer.close()


if __name__ == "__main__":
    main()
