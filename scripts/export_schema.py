#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""导出知识图谱结构到 schema.md（适配 Category 多级分类体系）"""

import sys, os
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', '5211314zhg'))
out = []

def w(line=""):
    out.append(line)

with driver.session() as s:
    # ── 总览 ──
    node_cnt = s.run("MATCH (n) RETURN count(n) AS c").single()["c"]
    rel_cnt = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]

    w("# 公务员考试知识图谱 · 结构文档")
    w()
    w(f"> 自动生成于 Neo4j 数据库 | 节点 **{node_cnt}** | 关系 **{rel_cnt}**")
    w()

    # ── 节点标签 ──
    w("## 一、节点类型")
    w()
    w("| 标签 | 数量 | 说明 |")
    w("|------|------|------|")
    label_desc = {
        "Category": "分类（多级分类体系，从根到叶最多 5 层）",
        "Topic": "主题（知识专题，归入分类体系）",
        "KnowledgePoint": "知识点（最小知识单元）",
        "Question": "题目（选择题 / 判断题）",
    }
    for r in s.run("MATCH (n) WITH labels(n) AS l UNWIND l AS lbl RETURN lbl, count(*) AS c ORDER BY c DESC"):
        desc = label_desc.get(r["lbl"], "")
        w(f"| **{r['lbl']}** | {r['c']} | {desc} |")
    w()

    # ── 节点属性 ──
    w("## 二、节点属性")
    w()
    prop_desc = {
        "Category": {
            "id": "唯一标识，如 `cat_行政职业能力测验_言语理解与表达`",
            "name": "分类名称",
            "level": "层级（0=根, 1=模块, 2+=子分类）",
            "is_leaf": "是否叶节点",
            "path": "完整路径，如 `行政职业能力测验/言语理解与表达/逻辑填空`",
        },
        "Topic": {
            "id": "唯一标识，如 `topic_地理与环境`",
            "name": "主题名称",
            "created_at": "创建时间",
        },
        "KnowledgePoint": {
            "id": "唯一标识，如 `kp_中国自然地理`",
            "name": "知识点名称（5-15 字）",
            "content": "知识点详细内容",
            "keywords": "关键词列表（JSON 数组字符串）",
            "difficulty": "难度 1-5",
            "importance": "重要性 1-5",
            "created_at": "创建时间",
        },
        "Question": {
            "id": "唯一标识，如 `q_p3_001`",
            "content": "完整题目内容",
            "options": "选项（JSON 对象字符串，如 {A:…, B:…}）",
            "answer": "正确答案字母",
            "analysis": "答案解析",
            "difficulty": "难度 1-5",
            "created_at": "创建时间",
        },
    }
    for label in ["Category", "Topic", "KnowledgePoint", "Question"]:
        w(f"### {label}")
        w()
        w("| 属性 | 类型 | 说明 |")
        w("|------|------|------|")
        r = s.run(f"MATCH (n:{label}) RETURN n LIMIT 1").single()
        if r:
            node = dict(r["n"])
            for k in sorted(node.keys()):
                val = node[k]
                typ = type(val).__name__
                if typ == "str":
                    typ = "String"
                elif typ == "int":
                    typ = "Integer"
                elif typ == "float":
                    typ = "Float"
                elif typ == "bool":
                    typ = "Boolean"
                desc = prop_desc.get(label, {}).get(k, "")
                w(f"| `{k}` | {typ} | {desc} |")
        w()

    # ── 关系类型 ──
    w("## 三、关系类型")
    w()
    w("| 关系 | 起点 | 终点 | 数量 | 说明 |")
    w("|------|------|------|------|------|")
    rel_desc = {
        "HAS_CHILD": "父分类包含子分类",
        "BELONGS_TO_CATEGORY": "主题归属于分类",
        "BELONGS_TO_TOPIC": "知识点/题目隶属于主题",
        "RELATED_TO_KNOWLEDGE_POINT": "题目关联到知识点",
    }
    for r in s.run("""
        MATCH (a)-[r]->(b)
        WITH labels(a)[0] AS fl, type(r) AS t, labels(b)[0] AS tl, count(*) AS c
        RETURN fl, t, tl, c ORDER BY c DESC
    """):
        desc = rel_desc.get(r["t"], "")
        w(f"| **{r['t']}** | {r['fl']} | {r['tl']} | {r['c']} | {desc} |")
    w()

    # ── 图谱层次结构 ──
    w("## 四、层次结构")
    w()
    w("```")
    w("Category (根: 行政职业能力测验)")
    w("  └── Category (模块: 言语理解与表达/数量关系/...)   [HAS_CHILD]")
    w("        └── Category (子分类: 逻辑填空/片段阅读/...)  [HAS_CHILD]")
    w("              └── Category (细分: 实词辨析/...)        [HAS_CHILD]")
    w("                    └── Topic (主题)                   [BELONGS_TO_CATEGORY]")
    w("                          ├── KnowledgePoint           [BELONGS_TO_TOPIC]")
    w("                          └── Question                 [BELONGS_TO_TOPIC]")
    w("                                └──→ KnowledgePoint    [RELATED_TO_KNOWLEDGE_POINT]")
    w("```")
    w()

    # ── 分类体系树 ──
    w("## 五、标准分类体系树")
    w()
    w("以下为完整分类层级及各分类下的 Topic 数量：")
    w()

    def count_topics_under(cid):
        """递归统计某分类及其所有子孙下的 Topic 总数"""
        direct = s.run("""
            MATCH (c:Category {id: $cid})<-[:BELONGS_TO_CATEGORY]-(t:Topic)
            RETURN count(t) AS cnt
        """, cid=cid).single()["cnt"]

        children = list(s.run("""
            MATCH (c:Category {id: $cid})-[:HAS_CHILD]->(child:Category)
            RETURN child.id AS child_id
        """, cid=cid))

        total = direct
        for ch in children:
            total += count_topics_under(ch["child_id"])
        return total

    def print_category_tree(parent_id, depth=0):
        children = list(s.run("""
            MATCH (p:Category {id: $pid})-[:HAS_CHILD]->(c:Category)
            RETURN c.id AS cid, c.name AS name
            ORDER BY c.name
        """, pid=parent_id))

        for child in children:
            total = count_topics_under(child["cid"])
            prefix = "  " * depth + "- "
            topic_str = f" `{total}`" if total > 0 else ""
            w(f"{prefix}**{child['name']}**{topic_str}")
            print_category_tree(child["cid"], depth + 1)

    root = s.run("MATCH (c:Category {level: 0}) RETURN c.id AS cid").single()
    if root:
        print_category_tree(root["cid"], 0)
    w()

    # ── 各模块数据分布 ──
    w("## 六、各模块数据分布")
    w()
    w("| 模块 | 主题 | 知识点 | 题目 |")
    w("|------|------|--------|------|")
    total_t = total_kp = total_q = 0
    for r in s.run("""
        MATCH (t:Topic)-[:BELONGS_TO_CATEGORY]->(c:Category)
        WITH CASE WHEN c.level = 1 THEN c.name
                  ELSE split(c.path, '/')[1] END AS modname, t
        OPTIONAL MATCH (t)<-[:BELONGS_TO_TOPIC]-(kp:KnowledgePoint)
        OPTIONAL MATCH (t)<-[:BELONGS_TO_TOPIC]-(q:Question)
        WITH modname,
             count(DISTINCT t) AS topics,
             count(DISTINCT kp) AS kps,
             count(DISTINCT q) AS qs
        RETURN modname, topics, kps, qs
        ORDER BY modname
    """):
        w(f"| {r['modname']} | {r['topics']} | {r['kps']} | {r['qs']} |")
        total_t += r['topics']; total_kp += r['kps']; total_q += r['qs']
    w(f"| **合计** | **{total_t}** | **{total_kp}** | **{total_q}** |")
    w()

    # ── 关联统计 ──
    w("## 七、关联统计")
    w()
    r1 = s.run("MATCH (q:Question)-[r:RELATED_TO_KNOWLEDGE_POINT]->(kp) RETURN count(r) AS c").single()
    r2 = s.run("MATCH (q:Question) RETURN count(q) AS c").single()
    r3 = s.run("MATCH (q:Question) WHERE (q)-[:RELATED_TO_KNOWLEDGE_POINT]->() RETURN count(q) AS c").single()
    r4 = s.run("MATCH (q:Question) WHERE NOT (q)-[:RELATED_TO_KNOWLEDGE_POINT]->() RETURN count(q) AS c").single()
    w(f"- 题目→知识点 总关联数：**{r1['c']}**")
    w(f"- 总题目数：**{r2['c']}**")
    if r2['c'] > 0:
        w(f"- 已关联题目：**{r3['c']}**（{r3['c']*100//r2['c']}%）")
    w(f"- 未关联题目：**{r4['c']}**")
    w()

    # ── 各分类 Topic 列表 ──
    w("## 八、各分类下的主题一览")
    w()

    modules = list(s.run("""
        MATCH (mod:Category {level: 1})
        RETURN mod.id AS mid, mod.name AS name ORDER BY name
    """))

    for mod in modules:
        w(f"### {mod['name']}")
        w()

        topics_by_cat = list(s.run("""
            MATCH (t:Topic)-[:BELONGS_TO_CATEGORY]->(c:Category)
            WHERE c.path STARTS WITH $prefix
            OPTIONAL MATCH (t)<-[:BELONGS_TO_TOPIC]-(kp:KnowledgePoint)
            OPTIONAL MATCH (t)<-[:BELONGS_TO_TOPIC]-(q:Question)
            WITH c.path AS cat_path, c.name AS cat_name,
                 t.name AS topic_name,
                 count(DISTINCT kp) AS kps, count(DISTINCT q) AS qs
            RETURN cat_path, cat_name, topic_name, kps, qs
            ORDER BY cat_path, topic_name
        """, prefix=f"行政职业能力测验/{mod['name']}"))

        if not topics_by_cat:
            w("*暂无数据*")
            w()
            continue

        cur_cat = ""
        for t in topics_by_cat:
            cat_display = t["cat_path"].replace("行政职业能力测验/", "")
            if cat_display != cur_cat:
                cur_cat = cat_display
                w(f"**{cur_cat}**")
                w()
                w("| 主题 | 知识点 | 题目 |")
                w("|------|--------|------|")
            w(f"| {t['topic_name']} | {t['kps']} | {t['qs']} |")

        w()

    # ── Cypher 查询示例 ──
    w("## 九、常用 Cypher 查询")
    w()
    w("```cypher")
    w("-- 查看分类体系树")
    w("MATCH path = (root:Category {level: 0})-[:HAS_CHILD*]->(leaf:Category)")
    w("WHERE NOT (leaf)-[:HAS_CHILD]->()")
    w("RETURN [n IN nodes(path) | n.name] AS 分类路径")
    w()
    w("-- 查看某模块的所有主题")
    w("MATCH (t:Topic)-[:BELONGS_TO_CATEGORY]->(c:Category)")
    w("WHERE c.path STARTS WITH '行政职业能力测验/常识判断'")
    w("RETURN c.name AS 分类, t.name AS 主题 ORDER BY c.path, t.name")
    w()
    w("-- 查看某主题下的知识点和题目")
    w("MATCH (t:Topic {name: '地理与环境'})<-[:BELONGS_TO_TOPIC]-(n)")
    w("RETURN labels(n)[0] AS type, n.name AS name, n.content AS content")
    w()
    w("-- 查看某题目关联的知识点")
    w("MATCH (q:Question)-[:RELATED_TO_KNOWLEDGE_POINT]->(kp:KnowledgePoint)")
    w("WHERE q.content CONTAINS '地理'")
    w("RETURN q.content, kp.name")
    w()
    w("-- 按难度查找题目（沿分类链路）")
    w("MATCH (q:Question)-[:BELONGS_TO_TOPIC]->(t:Topic)-[:BELONGS_TO_CATEGORY]->(c:Category)")
    w("WHERE q.difficulty >= 4")
    w("RETURN c.name AS 分类, t.name AS 主题, q.content AS 题目, q.difficulty AS 难度")
    w("ORDER BY q.difficulty DESC LIMIT 10")
    w()
    w("-- 统计各模块题目难度分布")
    w("MATCH (q:Question)-[:BELONGS_TO_TOPIC]->(t:Topic)-[:BELONGS_TO_CATEGORY]->(c:Category)")
    w("RETURN split(c.path, '/')[1] AS 模块, q.difficulty AS 难度, count(q) AS 数量")
    w("ORDER BY 模块, 难度")
    w()
    w("-- 查看分类的 Topic 数量分布")
    w("MATCH (c:Category)<-[:BELONGS_TO_CATEGORY]-(t:Topic)")
    w("RETURN c.path AS 分类路径, count(t) AS 主题数")
    w("ORDER BY 主题数 DESC")
    w("```")

driver.close()

# 写文件
schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema.md')
with open(schema_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out) + '\n')

print(f"已导出到 schema.md ({len(out)} 行)")
