"""
展示完整的知识图谱层次结构
"""
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "5211314zhg"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

with driver.session() as session:
    print("\n" + "="*60)
    print("公考知识图谱完整层次结构")
    print("="*60)
    
    # 查询所有类别
    categories = session.run("MATCH (c:Category) RETURN c ORDER BY c.order")
    
    for cat_record in categories:
        category = cat_record['c']
        print(f"\n📁 {category['name']} ({category.get('code', '')})")
        print(f"   {category.get('description', '')}")
        
        # 查询该类别下的所有科目
        subjects = session.run("""
            MATCH (c:Category {id: $cid})-[:HAS_SUBJECT]->(s:Subject)
            RETURN s ORDER BY s.order
        """, cid=category['id'])
        
        subject_list = list(subjects)
        for sidx, subject_record in enumerate(subject_list):
            subject = subject_record['s']
            is_last_subject = (sidx == len(subject_list) - 1)
            subject_prefix = "  └─" if is_last_subject else "  ├─"
            print(f"\n{subject_prefix} 📚 {subject['name']} ({subject.get('code', '')})")
        
            # 查询该科目的所有模块
            modules = session.run("""
                MATCH (s:Subject {id: $sid})-[:HAS_MODULE]->(m:Module)
                RETURN m ORDER BY m.order
            """, sid=subject['id'])
            
            module_list = list(modules)
            for midx, module_record in enumerate(module_list):
                module = module_record['m']
                is_last_module = (midx == len(module_list) - 1)
                
                if is_last_subject:
                    module_prefix = "      └─" if is_last_module else "      ├─"
                else:
                    module_prefix = "  │   └─" if is_last_module else "  │   ├─"
                
                print(f"{module_prefix} {module['name']}")
                
                # 查询该模块的所有章节
                chapters = session.run("""
                    MATCH (m:Module {id: $mid})-[:HAS_CHAPTER]->(c:Chapter)
                    RETURN c ORDER BY c.order
                """, mid=module['id'])
                
                chapter_list = list(chapters)
                for idx, chapter_record in enumerate(chapter_list):
                    chapter = chapter_record['c']
                    is_last_chapter = (idx == len(chapter_list) - 1)
                    
                    if is_last_subject and is_last_module:
                        chapter_prefix = "          └─" if is_last_chapter else "          ├─"
                    elif is_last_subject:
                        chapter_prefix = "      │   └─" if is_last_chapter else "      │   ├─"
                    elif is_last_module:
                        chapter_prefix = "  │       └─" if is_last_chapter else "  │       ├─"
                    else:
                        chapter_prefix = "  │   │   └─" if is_last_chapter else "  │   │   ├─"
                    
                    print(f"{chapter_prefix} {chapter['name']}")

    # 统计信息
    print("\n" + "="*60)
    print("数据统计")
    print("="*60)
    
    stats = session.run("""
        OPTIONAL MATCH (cat:Category)
        WITH count(DISTINCT cat) as categories
        OPTIONAL MATCH (s:Subject)
        WITH categories, count(DISTINCT s) as subjects
        OPTIONAL MATCH (m:Module)
        WITH categories, subjects, count(DISTINCT m) as modules
        OPTIONAL MATCH (c:Chapter)
        WITH categories, subjects, modules, count(DISTINCT c) as chapters
        OPTIONAL MATCH (t:Topic)
        WITH categories, subjects, modules, chapters, count(DISTINCT t) as topics
        OPTIONAL MATCH (k:KnowledgePoint)
        RETURN categories, subjects, modules, chapters, topics, count(DISTINCT k) as knowledge_points
    """).single()
    
    print(f"类别: {stats['categories']}")
    print(f"科目: {stats['subjects']}")
    print(f"模块: {stats['modules']}")
    print(f"章节: {stats['chapters']}")
    print(f"主题: {stats['topics']}")
    print(f"知识点: {stats['knowledge_points']}")
    
    # 其他实体统计
    other_stats = session.run("""
        OPTIONAL MATCH (q:Question) WITH count(q) as questions
        OPTIONAL MATCH (s:Skill) WITH questions, count(s) as skills
        OPTIONAL MATCH (r:Resource) WITH questions, skills, count(r) as resources
        OPTIONAL MATCH (tp:TestPoint) WITH questions, skills, resources, count(tp) as test_points
        OPTIONAL MATCH (c:Concept) 
        RETURN questions, skills, resources, test_points, count(c) as concepts
    """).single()
    
    print(f"\n真题: {other_stats['questions']}")
    print(f"技巧: {other_stats['skills']}")
    print(f"资源: {other_stats['resources']}")
    print(f"考点: {other_stats['test_points']}")
    print(f"概念: {other_stats['concepts']}")

driver.close()
print("\n" + "="*60)
