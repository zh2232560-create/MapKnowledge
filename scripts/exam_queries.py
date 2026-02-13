"""
公考知识图谱查询示例

展示基于新的层次化结构的各种查询功能
"""
from neo4j import GraphDatabase
from typing import List, Dict

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "5211314zhg"


class ExamKnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def query_1_subject_structure(self, subject_name: str = "行测"):
        """查询1: 查看某个科目的完整知识结构"""
        print(f"\n{'='*60}")
        print(f"查询1: {subject_name}科目的完整知识结构")
        print('='*60)
        
        query = """
        MATCH path = (s:Subject {name: $name})-[:HAS_MODULE*1..4]->(node)
        RETURN path
        LIMIT 50
        """
        
        with self.driver.session() as session:
            result = session.run(query, name=subject_name)
            paths = list(result)
            print(f"找到 {len(paths)} 条路径")
            
            # 展示树形结构
            query2 = """
            MATCH (s:Subject {name: $name})-[:HAS_MODULE]->(m:Module)
            OPTIONAL MATCH (m)-[:HAS_CHAPTER]->(c:Chapter)
            OPTIONAL MATCH (c)-[:HAS_TOPIC]->(t:Topic)
            RETURN m.name as module, m.order as order,
                   collect(DISTINCT c.name) as chapters, 
                   collect(DISTINCT t.name) as topics
            ORDER BY order
            """
            result2 = session.run(query2, name=subject_name)
            for record in result2:
                print(f"\n📌 模块: {record['module']}")
                if record['chapters'] and record['chapters'][0]:
                    print(f"   章节: {', '.join(filter(None, record['chapters']))}")
    
    def query_2_learning_path(self, topic_name: str = "实词辨析"):
        """查询2: 查询某个主题的学习路径（前置知识）"""
        print(f"\n{'='*60}")
        print(f"查询2: {topic_name}的学习路径")
        print('='*60)
        
        query = """
        MATCH (t:Topic {name: $name})-[:HAS_KNOWLEDGE]->(k:KnowledgePoint)
        OPTIONAL MATCH path = (prereq:KnowledgePoint)-[:PREREQUISITE*]->(k)
        RETURN k.name as knowledge, 
               collect(DISTINCT prereq.name) as prerequisites,
               k.difficulty as difficulty,
               k.importance as importance
        ORDER BY k.importance DESC, k.difficulty
        """
        
        with self.driver.session() as session:
            result = session.run(query, name=topic_name)
            for record in result:
                print(f"\n📖 知识点: {record['knowledge']}")
                print(f"   难度: {record['difficulty']}/5, 重要度: {record['importance']}/5")
                if record['prerequisites'] and record['prerequisites'][0]:
                    print(f"   前置知识: {', '.join(filter(None, record['prerequisites']))}")
    
    def query_3_confusable_concepts(self, knowledge_name: str = "词义侧重分析"):
        """查询3: 查询易混淆的概念"""
        print(f"\n{'='*60}")
        print(f"查询3: 与'{knowledge_name}'易混淆的概念")
        print('='*60)
        
        query = """
        MATCH (k:KnowledgePoint {name: $name})-[r:CONFUSABLE_WITH]-(confused)
        RETURN confused.name as confused_name,
               r.confusion_reason as reason,
               r.distinction as distinction
        """
        
        with self.driver.session() as session:
            result = session.run(query, name=knowledge_name)
            count = 0
            for record in result:
                count += 1
                print(f"\n⚠️  易混淆: {record['confused_name']}")
                if record['reason']:
                    print(f"   混淆原因: {record['reason']}")
                if record['distinction']:
                    print(f"   区分要点: {record['distinction']}")
            
            if count == 0:
                print("未找到易混淆的概念")
    
    def query_4_high_frequency_tests(self, min_frequency: int = 15):
        """查询4: 查询高频考点"""
        print(f"\n{'='*60}")
        print(f"查询4: 高频考点（频率≥{min_frequency}）")
        print('='*60)
        
        query = """
        MATCH (k:KnowledgePoint)
        WHERE k.frequency >= $min_freq
        OPTIONAL MATCH (k)-[:IS_TEST_POINT]->(tp:TestPoint)
        RETURN k.name as knowledge,
               k.frequency as frequency,
               tp.trend as trend,
               k.importance as importance
        ORDER BY k.frequency DESC, k.importance DESC
        """
        
        with self.driver.session() as session:
            result = session.run(query, min_freq=min_frequency)
            for idx, record in enumerate(result, 1):
                trend = record['trend'] or '稳定'
                print(f"{idx}. {record['knowledge']}")
                print(f"   出现频率: {record['frequency']}次, 趋势: {trend}, 重要度: {record['importance']}/5")
    
    def query_5_skill_applications(self, skill_name: str = "语境分析法"):
        """查询5: 查询某个技巧的应用场景"""
        print(f"\n{'='*60}")
        print(f"查询5: {skill_name}的应用场景")
        print('='*60)
        
        query = """
        MATCH (s:Skill {name: $name})
        OPTIONAL MATCH (s)-[r:APPLIES_TO]->(target)
        RETURN s.description as description,
               s.steps as steps,
               labels(target)[0] as target_type,
               target.name as target_name,
               r.effectiveness as effectiveness
        """
        
        with self.driver.session() as session:
            result = session.run(query, name=skill_name)
            records = list(result)
            if records:
                first = records[0]
                print(f"\n📝 技巧说明: {first['description']}")
                if first['steps']:
                    print(f"   应用步骤: {first['steps']}")
                
                print(f"\n   适用于:")
                for record in records:
                    if record['target_name']:
                        eff = record['effectiveness'] or 'N/A'
                        print(f"   - {record['target_name']} (有效性: {eff}/5)")
    
    def query_6_topic_resources(self, topic_name: str = "实词辨析"):
        """查询6: 查询某个主题的学习资源"""
        print(f"\n{'='*60}")
        print(f"查询6: {topic_name}的学习资源")
        print('='*60)
        
        query = """
        MATCH (t:Topic {name: $name})-[r:HAS_RESOURCE]->(res:Resource)
        RETURN res.title as title,
               res.type as type,
               res.author as author,
               res.quality as quality,
               r.recommended as recommended
        ORDER BY res.quality DESC, res.view_count DESC
        """
        
        with self.driver.session() as session:
            result = session.run(query, name=topic_name)
            count = 0
            for record in result:
                count += 1
                recommend = "⭐推荐" if record['recommended'] else ""
                print(f"\n{count}. {record['title']} {recommend}")
                print(f"   类型: {record['type']}, 作者: {record['author']}, 质量: {record['quality']}/5")
            
            if count == 0:
                print("暂无学习资源")
    
    def query_7_real_questions(self, year: int = 2023, exam_type: str = "国考"):
        """查询7: 查询某年某类考试的真题及知识点分布"""
        print(f"\n{'='*60}")
        print(f"查询7: {year}年{exam_type}真题及知识点分布")
        print('='*60)
        
        query = """
        MATCH (q:Question {year: $year, exam_type: $exam_type})
        OPTIONAL MATCH (q)-[:TESTS]->(k:KnowledgePoint)
        OPTIONAL MATCH (q)-[:BELONGS_TO_TOPIC]->(t:Topic)
        RETURN q.question_number as number,
               q.content as content,
               q.difficulty as difficulty,
               k.name as knowledge,
               t.name as topic
        ORDER BY q.question_number
        """
        
        with self.driver.session() as session:
            result = session.run(query, year=year, exam_type=exam_type)
            for record in result:
                print(f"\n第{record['number']}题 [难度: {record['difficulty']}/5]")
                content = record['content'][:50] + "..." if len(record['content']) > 50 else record['content']
                print(f"内容: {content}")
                if record['topic']:
                    print(f"题型: {record['topic']}")
                if record['knowledge']:
                    print(f"考点: {record['knowledge']}")
    
    def query_8_knowledge_network(self, knowledge_name: str = "词义侧重分析"):
        """查询8: 查询某个知识点的关联网络"""
        print(f"\n{'='*60}")
        print(f"查询8: {knowledge_name}的关联网络")
        print('='*60)
        
        query = """
        MATCH (k:KnowledgePoint {name: $name})
        OPTIONAL MATCH (k)-[r:RELATED_TO]-(related:KnowledgePoint)
        OPTIONAL MATCH (k)<-[:DEFINES]-(c:Concept)
        OPTIONAL MATCH (k)-[:IS_TEST_POINT]->(tp:TestPoint)
        RETURN k.name as name,
               k.definition as definition,
               collect(DISTINCT related.name) as related_points,
               collect(DISTINCT c.name) as concepts,
               tp.name as test_point
        """
        
        with self.driver.session() as session:
            result = session.run(query, name=knowledge_name)
            record = result.single()
            if record:
                print(f"\n📌 知识点: {record['name']}")
                if record['definition']:
                    print(f"   定义: {record['definition']}")
                if record['concepts'] and record['concepts'][0]:
                    print(f"   相关概念: {', '.join(filter(None, record['concepts']))}")
                if record['related_points'] and record['related_points'][0]:
                    print(f"   关联知识: {', '.join(filter(None, record['related_points']))}")
                if record['test_point']:
                    print(f"   对应考点: {record['test_point']}")
    
    def query_9_module_statistics(self, module_name: str = "言语理解与表达"):
        """查询9: 查询某个模块的统计信息"""
        print(f"\n{'='*60}")
        print(f"查询9: {module_name}模块统计")
        print('='*60)
        
        query = """
        MATCH (m:Module {name: $name})
        OPTIONAL MATCH (m)-[:HAS_CHAPTER]->(c:Chapter)
        OPTIONAL MATCH (c)-[:HAS_TOPIC]->(t:Topic)
        OPTIONAL MATCH (t)-[:HAS_KNOWLEDGE]->(k:KnowledgePoint)
        RETURN m.name as module,
               count(DISTINCT c) as chapters,
               count(DISTINCT t) as topics,
               count(DISTINCT k) as knowledge_points,
               avg(t.difficulty) as avg_difficulty,
               avg(k.importance) as avg_importance
        """
        
        with self.driver.session() as session:
            result = session.run(query, name=module_name)
            record = result.single()
            if record:
                print(f"\n📊 模块: {record['module']}")
                print(f"   章节数: {record['chapters']}")
                print(f"   主题数: {record['topics']}")
                print(f"   知识点数: {record['knowledge_points']}")
                if record['avg_difficulty']:
                    print(f"   平均难度: {record['avg_difficulty']:.1f}/5")
                if record['avg_importance']:
                    print(f"   平均重要度: {record['avg_importance']:.1f}/5")
    
    def query_10_complete_learning_chain(self, subject_name: str = "行测", 
                                         topic_name: str = "实词辨析"):
        """查询10: 查询完整学习链（科目→模块→章节→主题→知识点→技巧→资源）"""
        print(f"\n{'='*60}")
        print(f"查询10: {subject_name}-{topic_name}完整学习链")
        print('='*60)
        
        query = """
        MATCH (s:Subject {name: $subject})-[:HAS_MODULE]->(m:Module)
              -[:HAS_CHAPTER]->(c:Chapter)-[:HAS_TOPIC]->(t:Topic {name: $topic})
        OPTIONAL MATCH (t)-[:HAS_KNOWLEDGE]->(k:KnowledgePoint)
        OPTIONAL MATCH (sk:Skill)-[:APPLIES_TO]->(t)
        OPTIONAL MATCH (t)-[:HAS_RESOURCE]->(r:Resource)
        RETURN s.name as subject,
               m.name as module,
               c.name as chapter,
               t.name as topic,
               collect(DISTINCT k.name) as knowledge_points,
               collect(DISTINCT sk.name) as skills,
               collect(DISTINCT r.title) as resources
        """
        
        with self.driver.session() as session:
            result = session.run(query, subject=subject_name, topic=topic_name)
            record = result.single()
            if record:
                print(f"\n🎯 学习路径:")
                print(f"   科目: {record['subject']}")
                print(f"   ↓")
                print(f"   模块: {record['module']}")
                print(f"   ↓")
                print(f"   章节: {record['chapter']}")
                print(f"   ↓")
                print(f"   主题: {record['topic']}")
                
                if record['knowledge_points'] and record['knowledge_points'][0]:
                    print(f"\n   📚 包含知识点:")
                    for kp in filter(None, record['knowledge_points']):
                        print(f"      - {kp}")
                
                if record['skills'] and record['skills'][0]:
                    print(f"\n   🔧 推荐技巧:")
                    for sk in filter(None, record['skills']):
                        print(f"      - {sk}")
                
                if record['resources'] and record['resources'][0]:
                    print(f"\n   📖 学习资源:")
                    for res in filter(None, record['resources']):
                        print(f"      - {res}")


def main():
    graph = ExamKnowledgeGraph(URI, USER, PASSWORD)
    
    try:
        # 执行所有查询示例
        graph.query_1_subject_structure("行测")
        graph.query_2_learning_path("实词辨析")
        graph.query_3_confusable_concepts("词义侧重分析")
        graph.query_4_high_frequency_tests(15)
        graph.query_5_skill_applications("语境分析法")
        graph.query_6_topic_resources("实词辨析")
        graph.query_7_real_questions(2023, "国考")
        graph.query_8_knowledge_network("词义侧重分析")
        graph.query_9_module_statistics("言语理解与表达")
        graph.query_10_complete_learning_chain("行测", "实词辨析")
        
        print(f"\n{'='*60}")
        print("✅ 所有查询示例执行完成！")
        print('='*60)
        
    finally:
        graph.close()


if __name__ == "__main__":
    main()
