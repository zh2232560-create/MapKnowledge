#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
处理长文本 PDF 的分块提取脚本

当文本超过 LLM 限制时，将其分成多个块分别处理，然后合并结果
"""

import os
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extract_entities import PDFExtractor, EntityExtractor


class LongTextProcessor:
    """处理超长文本的提取处理器"""
    
    def __init__(self, max_text_length: int = 25000):
        """
        初始化处理器
        
        Args:
            max_text_length: 单次处理的最大文本长度（字符）
        """
        self.max_text_length = max_text_length
        self.entity_extractor = EntityExtractor(llm_type="dashscope_claude")
    
    def split_text_by_length(self, text: str, max_length: int) -> List[str]:
        """按长度分割文本"""
        chunks = []
        current_chunk = ""
        
        # 按段落分割
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_length:
                current_chunk += para + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + '\n\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def extract_from_chunks(self, text: str, category: str) -> Dict:
        """
        从长文本中分块提取实体
        
        Args:
            text: 长文本
            category: 分类
        
        Returns:
            合并后的实体
        """
        # 分割文本
        if len(text) <= self.max_text_length:
            print(f"  文本长度 {len(text)} 字符，直接处理")
            try:
                return self.entity_extractor.extract_knowledge_points(text, category)
            except Exception as e:
                print(f"  直接处理失败: {e}")
                # 继续分块处理
        
        print(f"  文本长度 {len(text)} 字符，需要分块处理")
        chunks = self.split_text_by_length(text, self.max_text_length)
        print(f"  分成 {len(chunks)} 个块")
        
        all_questions = []
        all_knowledge_points = []
        
        # 分块处理
        for idx, chunk in enumerate(chunks, 1):
            print(f"  处理第 {idx}/{len(chunks)} 块...")
            
            try:
                entities = self.entity_extractor.extract_knowledge_points(chunk, category)
                
                if entities:
                    # 收集题目
                    for topic in entities.get("topics", []):
                        all_questions.extend(topic.get("questions", []))
                        all_knowledge_points.extend(topic.get("knowledge_points", []))
                    
                    print(f"    ✓ 提取了 {len(all_questions)} 道题目")
            except Exception as e:
                print(f"    ✗ 处理失败: {e}")
                continue
        
        # 去重知识点（按名称）
        kp_dict = {}
        for kp in all_knowledge_points:
            name = kp.get("name", "Unknown")
            if name not in kp_dict:
                kp_dict[name] = kp
        
        # 构建最终结果
        result = {
            "chapter": entities.get("chapter", "Unknown") if entities else "Unknown",
            "topics": [{
                "name": "合并主题",
                "knowledge_points": list(kp_dict.values()),
                "questions": all_questions
            }]
        }
        
        print(f"  ✓ 合并完成：{len(list(kp_dict.values()))} 个知识点，{len(all_questions)} 道题目")
        
        return result


def main():
    import glob
    
    if len(sys.argv) > 1:
        pattern = sys.argv[1]
        print(f"\n处理 PDF: {pattern}")
    else:
        print("使用方法: python process_long_text.py <PDF名称模式>")
        print("示例: python process_long_text.py 常识下册")
        return
    
    # 查找 PDF
    pdf_files = glob.glob(f"data/*{pattern}*.pdf")
    
    if not pdf_files:
        print(f"✗ 未找到匹配的 PDF 文件")
        return
    
    processor = LongTextProcessor(max_text_length=25000)
    
    for pdf_path in pdf_files:
        print(f"\n处理: {os.path.basename(pdf_path)}")
        
        # 提取 PDF 文本
        pdf_extractor = PDFExtractor(pdf_path)
        text = pdf_extractor.extract_text()
        
        if not text:
            print("✗ 无法提取文本")
            continue
        
        print(f"✓ 提取文本：{len(text)} 字符")
        
        # 从文件名推断分类
        filename = os.path.basename(pdf_path)
        if "常识" in filename:
            category = "常识判断"
        elif "判断推理" in filename:
            category = "判断推理"
        elif "数量" in filename:
            category = "数量关系"
        elif "言语" in filename:
            category = "言语理解"
        elif "资料" in filename:
            category = "资料分析"
        else:
            category = "未知分类"
        
        print(f"分类: {category}")
        
        # 分块提取
        entities = processor.extract_from_chunks(text, category)
        
        if not entities:
            print("✗ 提取失败")
            continue
        
        # 保存结果
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_file = f"data/{base_name}_entities_extracted.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(entities, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 已保存到: {output_file}")
        
        # 统计信息
        total_kps = sum(len(t.get("knowledge_points", [])) for t in entities["topics"])
        total_qs = sum(len(t.get("questions", [])) for t in entities["topics"])
        print(f"✓ 提取结果：{total_kps} 个知识点，{total_qs} 道题目")


if __name__ == "__main__":
    main()
