#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量从 PDF 中提取实体并导入知识图谱

使用方法:
1. python scripts/batch_extract_and_import.py          # 处理所有 PDF
2. python scripts/batch_extract_and_import.py --clear  # 清空图数据库后再导入
3. python scripts/batch_extract_and_import.py --pdf 常识上册.pdf  # 处理指定 PDF

流程:
1. 扫描 data/ 目录下的所有 PDF 文件
2. 对每个 PDF 调用 extract_entities.py 进行实体抽取
3. 自动生成 JSON 文件
4. 使用 import_data.py 导入到 Neo4j 知识图谱
"""

import os
import sys
import json
import glob
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extract_entities import PDFExtractor, EntityExtractor
from import_data import KnowledgeGraphImporter

# Neo4j 配置
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "5211314zhg")


class BatchProcessor:
    """批量处理 PDF 和知识图谱导入"""
    
    def __init__(self, data_dir: str = "data", output_dir: str = "data"):
        """
        初始化处理器
        
        Args:
            data_dir: PDF 文件所在目录
            output_dir: 输出 JSON 文件的目录
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.pdf_files = []
        self.results = []
        self.importer = KnowledgeGraphImporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        
        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def find_pdf_files(self, pattern: Optional[str] = None) -> List[str]:
        """查找 PDF 文件"""
        if pattern:
            # 处理指定的 PDF
            search_pattern = os.path.join(self.data_dir, f"*{pattern}*.pdf")
            self.pdf_files = glob.glob(search_pattern, recursive=False)
            if not self.pdf_files:
                # 如果没有找到，尝试直接查找
                direct_path = os.path.join(self.data_dir, pattern if pattern.endswith('.pdf') else f"{pattern}.pdf")
                if os.path.exists(direct_path):
                    self.pdf_files = [direct_path]
        else:
            # 找到所有 PDF
            self.pdf_files = glob.glob(os.path.join(self.data_dir, "*.pdf"), recursive=False)
        
        self.pdf_files.sort()
        return self.pdf_files
    
    def extract_from_pdf(self, pdf_path: str) -> Optional[Dict]:
        """
        从单个 PDF 提取实体
        
        Args:
            pdf_path: PDF 文件路径
        
        Returns:
            抽取的实体和关系字典，失败时返回 None
        """
        try:
            print(f"\n[1] 正在处理: {os.path.basename(pdf_path)}")
            
            # 提取 PDF 文本
            pdf_extractor = PDFExtractor(pdf_path)
            text = pdf_extractor.extract_text()
            
            if not text or len(text) < 100:
                print(f"  ⚠️  PDF 内容过少，跳过")
                return None
            
            # 获取分类标签
            filename = os.path.basename(pdf_path)
            category = self._get_category_from_filename(filename)
            
            print(f"  分类: {category}")
            
            # 设置 API 密钥（如果未设置）
            if not os.getenv("DASHSCOPE_CLAUDE_API_KEY"):
                os.environ["DASHSCOPE_CLAUDE_API_KEY"] = "sk-69b4138e853648a79659aa01cc859dd6"
            
            # 提取实体
            print(f"\n[2] 正在提取实体（使用 Qwen-Max 模型）...")
            entity_extractor = EntityExtractor(llm_type="dashscope_claude")
            entities = entity_extractor.extract_knowledge_points(text, category)
            
            if not entities:
                print(f"  [WARNING] 未能提取实体")
                return None
            
            print(f"  [OK] 成功提取实体")
            return entities
            
        except Exception as e:
            print(f"  [ERROR] 处理失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_entities_to_json(self, entities: Dict, pdf_filename: str) -> str:
        """
        保存提取的实体到 JSON 文件
        
        Args:
            entities: 实体字典
            pdf_filename: 原始 PDF 文件名
        
        Returns:
            输出文件路径
        """
        # 生成输出文件名
        base_name = os.path.splitext(pdf_filename)[0]
        output_filename = f"{base_name}_entities_extracted.json"
        output_path = os.path.join(self.output_dir, output_filename)
        
        # 转换为知识图谱格式
        kg_data = self._convert_to_kg_format(entities)
        
        # 保存
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, ensure_ascii=False, indent=2)
        
        print(f"  [OK] 已保存到: {output_path}")
        return output_path
    
    def _convert_to_kg_format(self, entities: Dict) -> Dict:
        """
        将提取的实体转换为知识图谱格式
        
        转换为包含 nodes 和 relationships 的格式
        """
        nodes = []
        relationships = []
        node_ids = set()
        
        if not entities or "topics" not in entities:
            return {"nodes": [], "relationships": []}
        
        chapter = entities.get("chapter", "Unknown")
        
        # 添加章节节点
        chapter_id = f"chapter_{chapter.replace(' ', '_')}"
        if chapter_id not in node_ids:
            nodes.append({
                "id": chapter_id,
                "label": "Chapter",
                "properties": {
                    "name": chapter,
                    "created_at": datetime.now().isoformat()
                }
            })
            node_ids.add(chapter_id)
        
        # 处理主题和知识点
        for topic in entities.get("topics", []):
            topic_name = topic.get("name", "Unknown Topic")
            topic_id = f"topic_{topic_name.replace(' ', '_')}"
            
            # 添加主题节点
            if topic_id not in node_ids:
                nodes.append({
                    "id": topic_id,
                    "label": "Topic",
                    "properties": {
                        "name": topic_name,
                        "created_at": datetime.now().isoformat()
                    }
                })
                node_ids.add(topic_id)
                
                # 主题与章节的关系
                relationships.append({
                    "type": "BELONGS_TO_CHAPTER",
                    "start_node": {"value": topic_id},
                    "end_node": {"value": chapter_id},
                    "properties": {}
                })
            
            # 处理知识点
            for kp in topic.get("knowledge_points", []):
                kp_name = kp.get("name", "Unknown")
                kp_id = f"kp_{kp_name.replace(' ', '_')}"
                
                # 添加知识点节点
                if kp_id not in node_ids:
                    nodes.append({
                        "id": kp_id,
                        "label": "KnowledgePoint",
                        "properties": {
                            "name": kp_name,
                            "content": kp.get("content", ""),
                            "keywords": json.dumps(kp.get("keywords", [])),
                            "difficulty": kp.get("difficulty", 3),
                            "importance": kp.get("importance", 3),
                            "created_at": datetime.now().isoformat()
                        }
                    })
                    node_ids.add(kp_id)
                    
                    # 知识点与主题的关系
                    relationships.append({
                        "type": "BELONGS_TO_TOPIC",
                        "start_node": {"value": kp_id},
                        "end_node": {"value": topic_id},
                        "properties": {}
                    })
            
            # 处理题目
            for question in topic.get("questions", []):
                q_content = question.get("content", "Unknown")[:50]  # 用前50字作为ID
                q_id = f"question_{q_content.replace(' ', '_')}"
                
                # 添加题目节点
                if q_id not in node_ids:
                    nodes.append({
                        "id": q_id,
                        "label": "Question",
                        "properties": {
                            "content": question.get("content", ""),
                            "answer": question.get("answer", ""),
                            "analysis": question.get("analysis", ""),
                            "difficulty": question.get("difficulty", 3),
                            "created_at": datetime.now().isoformat()
                        }
                    })
                    node_ids.add(q_id)
                    
                    # 题目与主题的关系
                    relationships.append({
                        "type": "BELONGS_TO_TOPIC",
                        "start_node": {"value": q_id},
                        "end_node": {"value": topic_id},
                        "properties": {}
                    })
        
        return {
            "nodes": nodes,
            "relationships": relationships
        }
    
    def _get_category_from_filename(self, filename: str) -> str:
        """从文件名推断分类"""
        mapping = {
            "常识": "常识判断",
            "判断推理": "判断推理",
            "数量": "数量关系",
            "言语": "言语理解",
            "资料分析": "资料分析"
        }
        
        for key, value in mapping.items():
            if key in filename:
                return value
        
        return "通用知识"
    
    def process_all(self, clear_db: bool = False, pdf_pattern: Optional[str] = None):
        """
        处理所有 PDF 文件
        
        Args:
            clear_db: 是否清空数据库
            pdf_pattern: PDF 文件模式过滤
        """
        print("\n" + "=" * 70)
        print("批量提取 PDF 实体并导入知识图谱")
        print("=" * 70)
        
        # 查找 PDF 文件
        pdfs = self.find_pdf_files(pdf_pattern)
        if not pdfs:
            print("[ERROR] 未找到 PDF 文件！")
            return
        
        print(f"\n找到 {len(pdfs)} 个 PDF 文件:")
        for pdf in pdfs:
            print(f"  - {os.path.basename(pdf)}")
        
        # 清空数据库（可选）
        if clear_db:
            confirm = input("\n是否清空 Neo4j 数据库? (yes/no): ").lower()
            if confirm == "yes":
                self.importer.clear_database()
        
        # 处理每个 PDF
        extracted_files = []
        for i, pdf_path in enumerate(pdfs, 1):
            print(f"\n{'='*70}")
            print(f"处理进度: {i}/{len(pdfs)}")
            print(f"{'='*70}")
            
            # 提取实体
            entities = self.extract_from_pdf(pdf_path)
            if not entities:
                continue
            
            # 保存为 JSON
            json_path = self.save_entities_to_json(entities, os.path.basename(pdf_path))
            extracted_files.append(json_path)
            
            self.results.append({
                "pdf": os.path.basename(pdf_path),
                "status": "success",
                "json_file": json_path
            })
        
        # 导入到知识图谱
        if extracted_files:
            print(f"\n{'='*70}")
            print("开始导入到知识图谱...")
            print(f"{'='*70}")
            
            for json_file in extracted_files:
                print(f"\n导入: {os.path.basename(json_file)}")
                try:
                    self.importer.import_from_json(json_file)
                except Exception as e:
                    print(f"  [ERROR] 导入失败: {e}")
        
        # 汇总统计
        self._print_summary()
        
        self.importer.close()
    
    def _print_summary(self):
        """打印处理总结"""
        print(f"\n{'='*70}")
        print("处理完成")
        print(f"{'='*70}")
        
        success = sum(1 for r in self.results if r.get("status") == "success")
        print(f"\n总计: {len(self.results)} 个 PDF")
        print(f"成功: {success} 个")
        print(f"失败: {len(self.results) - success} 个")
        
        if self.results:
            print("\n详情:")
            for result in self.results:
                status_icon = "[OK]" if result.get("status") == "success" else "[ERROR]"
                print(f"  {status_icon} {result['pdf']}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="批量提取 PDF 实体并导入知识图谱")
    parser.add_argument("--clear", action="store_true", help="清空 Neo4j 数据库")
    parser.add_argument("--pdf", type=str, help="指定要处理的 PDF 文件名模式")
    parser.add_argument("--data-dir", type=str, default="data", help="PDF 所在目录")
    parser.add_argument("--output-dir", type=str, default="data", help="输出 JSON 目录")
    
    args = parser.parse_args()
    
    try:
        processor = BatchProcessor(
            data_dir=args.data_dir,
            output_dir=args.output_dir
        )
        processor.process_all(
            clear_db=args.clear,
            pdf_pattern=args.pdf
        )
    except KeyboardInterrupt:
        print("\n\n[INFO] 用户中断")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
