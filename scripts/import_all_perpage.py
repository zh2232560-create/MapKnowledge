#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""将所有 perpage 提取结果批量导入 Neo4j（先清空旧数据）"""

import sys
import os
import json
import glob

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from import_data import KnowledgeGraphImporter

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "5211314zhg")


def main():
    # 1. 检查连接 & 当前数据
    print("=" * 70)
    print("Neo4j 批量导入（perpage 提取数据）")
    print("=" * 70)

    importer = KnowledgeGraphImporter(URI, USER, PASSWORD)

    with importer.driver.session() as s:
        node_cnt = s.run("MATCH (n) RETURN count(n) as c").single()["c"]
        rel_cnt = s.run("MATCH ()-[r]->() RETURN count(r) as c").single()["c"]
        print(f"\n当前数据库: {node_cnt} 节点, {rel_cnt} 关系")

    # 2. 清空旧数据
    print("\n清空旧数据...", flush=True)
    with importer.driver.session() as s:
        s.run("MATCH (n) DETACH DELETE n")
    print("  已清空\n")

    # 3. 导入所有 perpage.json
    files = sorted(glob.glob("data/*_perpage.json"))
    print(f"待导入: {len(files)} 个文件\n")

    total_nodes = 0
    total_rels = 0

    for i, fpath in enumerate(files, 1):
        fname = os.path.basename(fpath)
        print(f"[{i}/{len(files)}] {fname}")

        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        n_nodes = len(data.get("nodes", []))
        n_rels = len(data.get("relationships", []))
        total_nodes += n_nodes
        total_rels += n_rels

        importer.import_from_json(fpath)

    # 4. 验证
    print(f"\n{'=' * 70}")
    print("导入完成，验证数据...")
    print("=" * 70)

    with importer.driver.session() as s:
        node_cnt = s.run("MATCH (n) RETURN count(n) as c").single()["c"]
        rel_cnt = s.run("MATCH ()-[r]->() RETURN count(r) as c").single()["c"]

        print(f"\n  数据库节点: {node_cnt}")
        print(f"  数据库关系: {rel_cnt}")

        # 按标签统计
        labels = s.run("""
            MATCH (n)
            WITH labels(n) AS lbls
            UNWIND lbls AS lbl
            RETURN lbl, count(*) AS cnt
            ORDER BY cnt DESC
        """)
        print("\n  节点分布:")
        for r in labels:
            print(f"    {r['lbl']:<25} {r['cnt']:>5}")

        # 按关系类型统计
        rel_types = s.run("""
            MATCH ()-[r]->()
            RETURN type(r) AS t, count(*) AS cnt
            ORDER BY cnt DESC
        """)
        print("\n  关系分布:")
        for r in rel_types:
            print(f"    {r['t']:<35} {r['cnt']:>5}")

    importer.close()
    print(f"\n{'=' * 70}")
    print("全部导入完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
