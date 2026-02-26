#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速对比三种提取方式 - 用小样本测试
1. 分块提取 (25K)
2. 每页提取 (5页样本)
3. 全量提取 (全文)
"""

import os
import sys
import json
import pdfplumber
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_entities import PDFExtractor, EntityExtractor


def test_method_1_chunked(pdf_path: str):
    """方法1：分块提取 (25K)"""
    print("\n" + "="*70)
    print("方法 1: 分块提取 (25000 字符/块)")
    print("="*70)
    
    try:
        extractor = PDFExtractor(pdf_path)
        text = extractor.extract_text()
        
        chunks = []
        current = ""
        for line in text.split('\n'):
            if len(current) + len(line) + 1 <= 25000:
                current += line + '\n'
            else:
                if current:
                    chunks.append(current)
                current = line + '\n'
        if current:
            chunks.append(current)
        
        print(f"分成 {len(chunks)} 块")
        
        entity_extractor = EntityExtractor("dashscope_claude")
        
        total_q = 0
        total_kp = 0
        
        for i, chunk in enumerate(chunks):
            print(f"  [块 {i+1}/{len(chunks)}]...")
            data = entity_extractor.extract_knowledge_points(chunk, category="常识")
            
            q = sum(len(t.get("questions", [])) for t in data.get("topics", []))
            kp = sum(len(t.get("knowledge_points", [])) for t in data.get("topics", []))
            
            total_q += q
            total_kp += kp
            print(f"    ✓ +{q} 题目, +{kp} 知识点 (累计: {total_q}/{total_kp})")
        
        print(f"\n总计: {total_kp} 知识点, {total_q} 题目")
        return {"method": "分块 (25K)", "questions": total_q, "knowledge_points": total_kp}
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return {"method": "分块 (25K)", "error": str(e), "questions": 0, "knowledge_points": 0}


def test_method_2_per_page(pdf_path: str, sample_size: int = 5):
    """方法2：每页提取（只测试前5页）"""
    print("\n" + "="*70)
    print(f"方法 2: 每页提取 (样本: 前 {sample_size} 页)")
    print("="*70)
    
    try:
        entity_extractor = EntityExtractor("dashscope_claude")
        
        total_q = 0
        total_kp = 0
        
        with pdfplumber.open(pdf_path) as pdf:
            pages_to_test = min(sample_size, len(pdf.pages))
            print(f"测试前 {pages_to_test} 页 (总共 {len(pdf.pages)} 页)")
            
            for page_idx in range(pages_to_test):
                print(f"\n  [第 {page_idx+1}/{pages_to_test} 页]...")
                
                text = pdf.pages[page_idx].extract_text()
                if not text or len(text) < 50:
                    print(f"    [跳过：内容太少]")
                    continue
                
                data = entity_extractor.extract_knowledge_points(text, category="常识")
                
                q = sum(len(t.get("questions", [])) for t in data.get("topics", []))
                kp = sum(len(t.get("knowledge_points", [])) for t in data.get("topics", []))
                
                total_q += q
                total_kp += kp
                print(f"    ✓ +{q} 题目, +{kp} 知识点 (累计: {total_q}/{total_kp})")
        
        # 估算全文
        pages_count = len(pdf.pages)
        estimated_q = int((total_q / pages_to_test) * pages_count) if pages_to_test > 0 else 0
        estimated_kp = int((total_kp / pages_to_test) * pages_count) if pages_to_test > 0 else 0
        
        print(f"\n样本统计 ({pages_to_test} 页): {total_kp} 知识点, {total_q} 题目")
        print(f"估算全文 ({pages_count} 页): {estimated_kp} 知识点, {estimated_q} 题目")
        
        return {"method": "每页", "questions": estimated_q, "knowledge_points": estimated_kp, 
                "sample_q": total_q, "sample_kp": total_kp}
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return {"method": "每页", "error": str(e), "questions": 0, "knowledge_points": 0}


def test_method_3_full(pdf_path: str):
    """方法3：全量提取（全文一次）"""
    print("\n" + "="*70)
    print("方法 3: 全量提取 (全文一次)")
    print("="*70)
    print("⚠️ 警告: 不考虑 token 消耗，尝试一次性提取全部\n")
    
    try:
        extractor = PDFExtractor(pdf_path)
        text = extractor.extract_text()
        
        print(f"文本长度: {len(text)} 字符")
        print("正在提取...（这可能需要 1-3 分钟）")
        
        entity_extractor = EntityExtractor("dashscope_claude")
        data = entity_extractor.extract_knowledge_points(text, category="常识")
        
        total_q = sum(len(t.get("questions", [])) for t in data.get("topics", []))
        total_kp = sum(len(t.get("knowledge_points", [])) for t in data.get("topics", []))
        
        print(f"\n总计: {total_kp} 知识点, {total_q} 题目")
        return {"method": "全量提取", "questions": total_q, "knowledge_points": total_kp}
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return {"method": "全量提取", "error": str(e), "questions": 0, "knowledge_points": 0}


def print_comparison(results):
    """打印对比"""
    print("\n\n" + "="*70)
    print("对比总结")
    print("="*70)
    
    print(f"\n{'方法':<20} {'知识点':<12} {'题目':<12}")
    print("-" * 70)
    
    for r in results:
        if "error" not in r:
            print(f"{r['method']:<20} {r['knowledge_points']:<12} {r['questions']:<12}")
        else:
            print(f"{r['method']:<20} ERROR: {r['error']}")
    
    # 分析
    valid = [r for r in results if "error" not in r]
    
    if valid:
        print("\n" + "="*70)
        print("分析:")
        print("="*70)
        
        best_q = max(valid, key=lambda x: x['questions'])
        
        print(f"\n✓ 题目提取最多: {best_q['method']}")
        print(f"  - {best_q['questions']} 道题目")
        print(f"  - {best_q['knowledge_points']} 个知识点")
        
        print(f"\n效率对比（vs 最优方案）:")
        for r in valid:
            ratio = (r['questions'] / best_q['questions'] * 100) if best_q['questions'] > 0 else 0
            print(f"  {r['method']:<20} : {ratio:.1f}%")


def main():
    """主函数"""
    pdf_path = "data/常识上册.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF 文件不存在: {pdf_path}")
        return
    
    print("\n" + "="*70)
    print("PDF 三种提取方式对比测试")
    print(f"测试文件: {pdf_path}")
    print("="*70)
    
    results = []
    
    # 方法1：分块提取
    r1 = test_method_1_chunked(pdf_path)
    results.append(r1)
    
    # 方法2：每页提取（样本）
    r2 = test_method_2_per_page(pdf_path, sample_size=5)
    results.append(r2)
    
    # 方法3：全量提取
    r3 = test_method_3_full(pdf_path)
    results.append(r3)
    
    # 打印对比
    print_comparison(results)


if __name__ == "__main__":
    main()
