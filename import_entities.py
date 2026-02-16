#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接导入实体到知识图谱
"""
import os
import sys

# 添加脚本目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from import_data import KnowledgeGraphImporter

# Neo4j 配置
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "5211314zhg")

def main():
    if len(sys.argv) < 2:
        print("使用方法: python import_entities.py <json_file> [<json_file2> ...]")
        print("\n示例:")
        print("  python import_entities.py data/常识上册_entities_extracted.json")
        print("  python import_entities.py data/*_entities_extracted.json")
        return
    
    try:
        importer = KnowledgeGraphImporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        
        for json_file in sys.argv[1:]:
            if os.path.exists(json_file):
                print(f"\n导入: {json_file}")
                importer.import_from_json(json_file)
            else:
                print(f"✗ 文件不存在: {json_file}")
        
        importer.close()
        
        print("\n" + "="*60)
        print("✓ 导入完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
