#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
对比三种 PDF 提取方式的效果
"""

import os
import sys
import json
import pdfplumber
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_entities import PDFExtractor, EntityExtractor


class ComparisonTest:
    """对比测试"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.results = {}
    
    def method_1_chunked(self) -> Dict[str, Any]:
        """方法1：分块提取（当前方式 - 25000 字符/块）"""
        print("\n" + "="*70)
        print("方法 1: 分块提取（25000 字符/块）")
        print("="*70)
        
        try:
            extractor = PDFExtractor(self.pdf_path)
            text = extractor.extract_text()
            
            # 分块
            chunks = self._split_by_length(text, 25000)
            print(f"分成 {len(chunks)} 块")
            
            # 逐块提取
            entity_extractor = EntityExtractor("dashscope_claude")
            
            all_topics = {}
            for i, chunk in enumerate(chunks):
                print(f"\n  [块 {i+1}/{len(chunks)}]")
                data = entity_extractor.extract_knowledge_points(chunk, category="常识")
                
                # 合并数据
                for topic in data.get("topics", []):
                    topic_name = topic["name"]
                    if topic_name not in all_topics:
                        all_topics[topic_name] = topic
                    else:
                        # 合并题目和知识点
                        all_topics[topic_name]["questions"].extend(topic.get("questions", []))
                        all_topics[topic_name]["knowledge_points"].extend(topic.get("knowledge_points", []))
                
                q_count = sum(len(t.get("questions", [])) for t in data.get("topics", []))
                kp_count = sum(len(t.get("knowledge_points", [])) for t in data.get("topics", []))
                print(f"    ✓ 题目: {q_count}, 知识点: {kp_count}")
            
            total_q = sum(len(t.get("questions", [])) for t in all_topics.values())
            total_kp = sum(len(t.get("knowledge_points", [])) for t in all_topics.values())
            
            result = {
                "method": "分块提取 (25K)",
                "chunks": len(chunks),
                "questions": total_q,
                "knowledge_points": total_kp,
                "data": all_topics
            }
            
            print(f"\n总计: {total_kp} 知识点, {total_q} 题目")
            return result
            
        except Exception as e:
            print(f"✗ 错误: {e}")
            return {"method": "分块提取 (25K)", "error": str(e), "questions": 0, "knowledge_points": 0}
    
    def method_2_per_page(self) -> Dict[str, Any]:
        """方法2：每页提取"""
        print("\n" + "="*70)
        print("方法 2: 每页提取")
        print("="*70)
        
        try:
            entity_extractor = EntityExtractor("dashscope_claude")
            
            all_topics = {}
            
            with pdfplumber.open(self.pdf_path) as pdf:
                print(f"总页数: {len(pdf.pages)}")
                
                for page_idx, page in enumerate(pdf.pages):
                    if (page_idx + 1) % 5 == 0 or (page_idx + 1) == len(pdf.pages):
                        print(f"\n  [第 {page_idx + 1}/{len(pdf.pages)} 页]")
                    
                    text = page.extract_text()
                    if not text or len(text) < 100:
                        continue
                    
                    data = entity_extractor.extract_knowledge_points(text, category="常识")
                    
                    for topic in data.get("topics", []):
                        topic_name = topic["name"]
                        if topic_name not in all_topics:
                            all_topics[topic_name] = topic
                        else:
                            all_topics[topic_name]["questions"].extend(topic.get("questions", []))
                            all_topics[topic_name]["knowledge_points"].extend(topic.get("knowledge_points", []))
                    
                    if (page_idx + 1) % 5 == 0 or (page_idx + 1) == len(pdf.pages):
                        q_count = sum(len(t.get("questions", [])) for t in all_topics.values())
                        kp_count = sum(len(t.get("knowledge_points", [])) for t in all_topics.values())
                        print(f"    累计: 题目 {q_count}, 知识点 {kp_count}")
            
            total_q = sum(len(t.get("questions", [])) for t in all_topics.values())
            total_kp = sum(len(t.get("knowledge_points", [])) for t in all_topics.values())
            
            result = {
                "method": "每页提取",
                "pages": len(pdf.pages),
                "questions": total_q,
                "knowledge_points": total_kp,
                "data": all_topics
            }
            
            print(f"\n总计: {total_kp} 知识点, {total_q} 题目")
            return result
            
        except Exception as e:
            print(f"✗ 错误: {e}")
            return {"method": "每页提取", "error": str(e), "questions": 0, "knowledge_points": 0}
    
    def method_3_full_text(self) -> Dict[str, Any]:
        """方法3：全量提取（不考虑 token 消耗）"""
        print("\n" + "="*70)
        print("方法 3: 全量提取（不考虑 token 消耗）")
        print("="*70)
        print("⚠️ 警告: 可能超过 token 限制，但尝试一次性提取全部")
        
        try:
            extractor = PDFExtractor(self.pdf_path)
            text = extractor.extract_text()
            
            print(f"\n文本长度: {len(text)} 字符")
            print("正在提取...（可能需要较长时间）")
            
            entity_extractor = EntityExtractor("dashscope_claude")
            data = entity_extractor.extract_knowledge_points(text, category="常识")
            
            total_q = sum(len(t.get("questions", [])) for t in data.get("topics", []))
            total_kp = sum(len(t.get("knowledge_points", [])) for t in data.get("topics", []))
            
            result = {
                "method": "全量提取",
                "text_length": len(text),
                "questions": total_q,
                "knowledge_points": total_kp,
                "data": data
            }
            
            print(f"\n总计: {total_kp} 知识点, {total_q} 题目")
            return result
            
        except Exception as e:
            print(f"✗ 错误: {e}")
            return {"method": "全量提取", "error": str(e), "questions": 0, "knowledge_points": 0}
    
    def _split_by_length(self, text: str, chunk_size: int) -> list:
        """按字符长度分块"""
        chunks = []
        current_chunk = ""
        
        for line in text.split('\n'):
            if len(current_chunk) + len(line) + 1 <= chunk_size:
                current_chunk += line + '\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = line + '\n'
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def run(self):
        """运行对比"""
        print("\n" + "="*70)
        print("PDF 提取方式对比测试")
        print(f"文件: {self.pdf_path}")
        print("="*70)
        
        # 运行三种方法
        r1 = self.method_1_chunked()
        self.results["method_1"] = r1
        
        r2 = self.method_2_per_page()
        self.results["method_2"] = r2
        
        r3 = self.method_3_full_text()
        self.results["method_3"] = r3
        
        # 打印对比
        self.print_summary()
    
    def print_summary(self):
        """打印总结"""
        print("\n\n" + "="*70)
        print("对比总结")
        print("="*70)
        
        print(f"\n{'方法':<20} {'知识点数':<12} {'题目数':<12} {'备注'}")
        print("-" * 70)
        
        for key, result in self.results.items():
            if "error" in result:
                print(f"{result['method']:<20} {'ERROR':<12} {result.get('error', '')}")
            else:
                method = result['method']
                kp = result.get('knowledge_points', 0)
                q = result.get('questions', 0)
                
                note = ""
                if 'chunks' in result:
                    note = f"({result['chunks']} 块)"
                elif 'pages' in result:
                    note = f"({result['pages']} 页)"
                elif 'text_length' in result:
                    note = f"({result['text_length']} 字符)"
                
                print(f"{method:<20} {kp:<12} {q:<12} {note}")
        
        # 对比分析
        print("\n" + "="*70)
        print("分析:")
        print("="*70)
        
        valid = {k: v for k, v in self.results.items() if "error" not in v}
        
        if valid:
            best = max(valid.items(), key=lambda x: x[1].get('questions', 0))
            print(f"\n✓ 最优方案: {best[1]['method']}")
            print(f"  - 题目数: {best[1].get('questions', 0)}")
            print(f"  - 知识点数: {best[1].get('knowledge_points', 0)}")
            
            # 计算效率对比
            print(f"\n效率对比:")
            for key, result in valid.items():
                if result.get('questions', 0) > 0:
                    method = result['method']
                    q = result['questions']
                    ratio = q / best[1].get('questions', 1)
                    print(f"  {method:<20} : {q:3} 题目 ({ratio*100:.1f}% vs 最优)")


def main():
    """主函数"""
    # 找题目数为 0 的 PDF
    test_pdfs = [
        "data/常识上册.pdf",
        "data/数量上册(1).pdf",
        "data/资料分析上册(1).pdf"
    ]
    
    pdf_path = None
    for pdf in test_pdfs:
        if os.path.exists(pdf):
            pdf_path = pdf
            break
    
    if not pdf_path:
        print("未找到测试 PDF")
        return
    
    test = ComparisonTest(pdf_path)
    test.run()


if __name__ == "__main__":
    main()
