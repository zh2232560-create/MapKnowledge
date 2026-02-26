#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复 Chapter 名称不一致问题"""

import sys, json, glob, os
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', '5211314zhg'))

# 修复映射
FIXES = {
    "第一章 图形推理": "判断推理",
    "第一章 文字资料": "资料分析",
}

with driver.session() as s:
    print("=== 修复前 Chapter 列表 ===")
    for r in s.run("MATCH (c:Chapter) RETURN c.name AS name, c.id AS id ORDER BY c.name"):
        print(f"  {r['name']}")

    for old_name, new_name in FIXES.items():
        # 检查目标 Chapter 是否已存在
        existing = s.run("MATCH (c:Chapter {name: $name}) RETURN c.id AS id", name=new_name).single()

        if existing:
            # 目标已存在 → 把旧 Chapter 下的 Topic 迁移过去，然后删除旧 Chapter
            target_id = existing["id"]
            print(f"\n  [{old_name}] → 合并到已有的 [{new_name}]")

            # 迁移关系
            result = s.run("""
                MATCH (old:Chapter {name: $old_name})
                MATCH (new:Chapter {name: $new_name})
                MATCH (t:Topic)-[r:BELONGS_TO_CHAPTER]->(old)
                DELETE r
                MERGE (t)-[:BELONGS_TO_CHAPTER]->(new)
                RETURN count(t) AS cnt
            """, old_name=old_name, new_name=new_name)
            cnt = result.single()["cnt"]
            print(f"    迁移 {cnt} 个 Topic")

            # 删除孤立的旧 Chapter
            s.run("MATCH (c:Chapter {name: $name}) DETACH DELETE c", name=old_name)
            print(f"    删除旧 Chapter [{old_name}]")
        else:
            # 目标不存在 → 直接改名
            print(f"\n  [{old_name}] → 重命名为 [{new_name}]")
            s.run("""
                MATCH (c:Chapter {name: $old_name})
                SET c.name = $new_name, c.id = $new_id
            """, old_name=old_name, new_name=new_name,
                 new_id=f"chapter_{new_name.replace(' ', '_')}")

    print("\n=== 修复后 Chapter 列表 ===")
    for r in s.run("MATCH (c:Chapter) RETURN c.name AS name ORDER BY c.name"):
        print(f"  {r['name']}")

    # 验证各科统计
    print("\n=== 修复后各科数据量 ===")
    print(f"  {'科目':<20} {'主题':>6} {'知识点':>8} {'题目':>6}")
    print(f"  {'-'*20} {'-'*6} {'-'*8} {'-'*6}")
    for r in s.run("""
        MATCH (c:Chapter)<-[:BELONGS_TO_CHAPTER]-(t:Topic)
        OPTIONAL MATCH (t)<-[:BELONGS_TO_TOPIC]-(kp:KnowledgePoint)
        OPTIONAL MATCH (t)<-[:BELONGS_TO_TOPIC]-(q:Question)
        WITH c.name AS chapter, count(DISTINCT t) AS topics,
             count(DISTINCT kp) AS kps, count(DISTINCT q) AS qs
        RETURN chapter, topics, kps, qs ORDER BY chapter
    """):
        print(f"  {r['chapter']:<20} {r['topics']:>6} {r['kps']:>8} {r['qs']:>6}")

driver.close()

# 同步修复源 JSON 文件
print("\n=== 修复源 JSON 文件 ===")
FILE_CHAPTER_MAP = {
    "判断推理上册(1)": "判断推理",
    "判断推理下册(1)": "判断推理",
    "资料分析上册(1)": "资料分析",
}
for stem, correct in FILE_CHAPTER_MAP.items():
    for suffix in ["_perpage_raw.json", "_perpage.json"]:
        path = f"data/{stem}{suffix}"
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        changed = False
        if suffix == "_perpage_raw.json" and data.get("chapter") != correct:
            old = data["chapter"]
            data["chapter"] = correct
            changed = True
        elif suffix == "_perpage.json":
            for node in data.get("nodes", []):
                if node.get("label") == "Chapter" and node["properties"].get("name") != correct:
                    old = node["properties"]["name"]
                    node["properties"]["name"] = correct
                    node["id"] = f"chapter_{correct.replace(' ', '_')}"
                    changed = True

        if changed:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  ✓ {os.path.basename(path)}: [{old}] → [{correct}]")

print("\n全部修复完成!")
