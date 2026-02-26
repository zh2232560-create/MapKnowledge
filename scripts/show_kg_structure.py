#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""查询 Neo4j 知识图谱的完整结构"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', '5211314zhg'))

with driver.session() as s:
    # 1. 节点标签统计
    print('=== 节点标签统计 ===')
    for r in s.run('MATCH (n) WITH labels(n) AS lbls UNWIND lbls AS l RETURN l, count(*) AS c ORDER BY c DESC'):
        print(f'  {r["l"]:<25} {r["c"]:>5}')

    # 2. 关系类型统计
    print('\n=== 关系类型统计 ===')
    for r in s.run('MATCH ()-[r]->() RETURN type(r) AS t, count(*) AS c ORDER BY c DESC'):
        print(f'  {r["t"]:<40} {r["c"]:>5}')

    # 3. Chapter 节点
    print('\n=== Chapter 节点 ===')
    for r in s.run('MATCH (c:Chapter) RETURN c.name AS name, c.id AS id ORDER BY c.name'):
        print(f'  {r["name"]}')

    # 4. 每个 Chapter 下的 Topic / KP / Question 数量
    print('\n=== 每个科目的数据量 ===')
    results = s.run('''
        MATCH (c:Chapter)<-[:BELONGS_TO_CHAPTER]-(t:Topic)
        OPTIONAL MATCH (t)<-[:BELONGS_TO_TOPIC]-(kp:KnowledgePoint)
        OPTIONAL MATCH (t)<-[:BELONGS_TO_TOPIC]-(q:Question)
        WITH c.name AS chapter, 
             count(DISTINCT t) AS topics, 
             count(DISTINCT kp) AS kps, 
             count(DISTINCT q) AS qs
        RETURN chapter, topics, kps, qs
        ORDER BY chapter
    ''')
    print(f'  {"科目":<20} {"主题":>6} {"知识点":>8} {"题目":>6}')
    print(f'  {"-"*20} {"-"*6} {"-"*8} {"-"*6}')
    for r in results:
        print(f'  {r["chapter"]:<20} {r["topics"]:>6} {r["kps"]:>8} {r["qs"]:>6}')

    # 5. 关系模式
    print('\n=== 关系模式 ===')
    for r in s.run('''
        MATCH (a)-[r]->(b)
        WITH labels(a)[0] AS from_l, type(r) AS rel, labels(b)[0] AS to_l, count(*) AS cnt
        RETURN from_l, rel, to_l, cnt
        ORDER BY cnt DESC
    '''):
        print(f'  ({r["from_l"]}) --[{r["rel"]}]--> ({r["to_l"]})  x{r["cnt"]}')

    # 6. 节点属性
    print('\n=== 各节点类型的属性字段 ===')
    for label in ['Chapter', 'Topic', 'KnowledgePoint', 'Question']:
        r = s.run(f'MATCH (n:{label}) RETURN keys(n) AS k LIMIT 1').single()
        if r:
            print(f'  {label}: {sorted(r["k"])}')

    # 7. 样例 Topic
    print('\n=== Topic 样例（每科取2个）===')
    for r in s.run('''
        MATCH (t:Topic)-[:BELONGS_TO_CHAPTER]->(c:Chapter)
        WITH c.name AS ch, collect(t.name)[..2] AS samples
        RETURN ch, samples ORDER BY ch
    '''):
        for t in r["samples"]:
            print(f'  [{r["ch"]}] {t}')

    # 8. 样例 KnowledgePoint
    print('\n=== KnowledgePoint 样例（前5个）===')
    for r in s.run('''
        MATCH (kp:KnowledgePoint)-[:BELONGS_TO_TOPIC]->(t:Topic)
        RETURN t.name AS topic, kp.name AS name, kp.difficulty AS diff, kp.importance AS imp
        LIMIT 5
    '''):
        print(f'  [{r["topic"]}] {r["name"]}  难度:{r["diff"]} 重要性:{r["imp"]}')

    # 9. 样例 Question
    print('\n=== Question 样例（前3个）===')
    for r in s.run('''
        MATCH (q:Question)-[:BELONGS_TO_TOPIC]->(t:Topic)
        RETURN t.name AS topic, q.content AS content, q.answer AS ans, q.difficulty AS diff
        LIMIT 3
    '''):
        content = r['content'][:100] + '...' if r['content'] and len(r['content']) > 100 else r['content']
        print(f'  [{r["topic"]}] 答案:{r["ans"]} 难度:{r["diff"]}')
        print(f'    {content}')

    # 10. 题目-知识点关联
    print('\n=== 题目-知识点关联情况 ===')
    r1 = s.run('MATCH (q:Question)-[r:RELATED_TO_KNOWLEDGE_POINT]->(kp) RETURN count(r) AS c').single()
    print(f'  总关联数:       {r1["c"]}')
    r2 = s.run('MATCH (q:Question) RETURN count(q) AS c').single()
    print(f'  总题目数:       {r2["c"]}')
    r3 = s.run('MATCH (q:Question) WHERE (q)-[:RELATED_TO_KNOWLEDGE_POINT]->() RETURN count(q) AS c').single()
    print(f'  已关联题目数:   {r3["c"]}')
    r4 = s.run('MATCH (q:Question) WHERE NOT (q)-[:RELATED_TO_KNOWLEDGE_POINT]->() RETURN count(q) AS c').single()
    print(f'  未关联题目数:   {r4["c"]}')

    # 11. 样例关联路径
    print('\n=== 关联路径样例 ===')
    for r in s.run('''
        MATCH (q:Question)-[:RELATED_TO_KNOWLEDGE_POINT]->(kp:KnowledgePoint)-[:BELONGS_TO_TOPIC]->(t:Topic)-[:BELONGS_TO_CHAPTER]->(c:Chapter)
        RETURN c.name AS chapter, t.name AS topic, kp.name AS kp, q.content AS q_content
        LIMIT 3
    '''):
        qc = r['q_content'][:60] + '...' if r['q_content'] and len(r['q_content']) > 60 else r['q_content']
        print(f'  Chapter: {r["chapter"]}')
        print(f'    └─ Topic: {r["topic"]}')
        print(f'        └─ KP: {r["kp"]}')
        print(f'            └─ Q: {qc}')
        print()

driver.close()
