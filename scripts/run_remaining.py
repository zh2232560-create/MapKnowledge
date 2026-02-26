#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""批量每页提取剩余 PDF（跳过已完成的）"""

import sys
import os
import json
import glob
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from per_page_extract import PerPageExtractor, get_category

def main():
    # 找出待处理的 PDF
    done = set(
        os.path.splitext(os.path.basename(f))[0].replace('_perpage_raw', '')
        for f in glob.glob('data/*_perpage_raw.json')
    )
    pdfs = sorted([
        f for f in glob.glob('data/*.pdf')
        if os.path.splitext(os.path.basename(f))[0] not in done
    ])

    print(f'待处理: {len(pdfs)} 个 PDF', flush=True)
    for p in pdfs:
        print(f'  · {os.path.basename(p)}', flush=True)

    if not pdfs:
        print('所有 PDF 已处理完毕！')
        return

    extractor = PerPageExtractor()

    for i, pdf_path in enumerate(pdfs, 1):
        stem = Path(pdf_path).stem
        category = get_category(os.path.basename(pdf_path))
        print(f'\n{"="*70}', flush=True)
        print(f'[{i}/{len(pdfs)}] {os.path.basename(pdf_path)}  (分类: {category})', flush=True)
        print('=' * 70, flush=True)

        try:
            entities = extractor.extract_pdf(pdf_path, category)

            # 保存原始合并数据
            raw_path = f'data/{stem}_perpage_raw.json'
            with open(raw_path, 'w', encoding='utf-8') as f:
                json.dump(entities, f, ensure_ascii=False, indent=2)

            # 保存 KG 格式
            kg_data = extractor.convert_to_kg_format(entities)
            kg_path = f'data/{stem}_perpage.json'
            with open(kg_path, 'w', encoding='utf-8') as f:
                json.dump(kg_data, f, ensure_ascii=False, indent=2)

            total_q = sum(len(t.get('questions', [])) for t in entities.get('topics', []))
            total_kp = sum(len(t.get('knowledge_points', [])) for t in entities.get('topics', []))
            print(f'\n✓ 完成: {total_kp} 知识点, {total_q} 题目', flush=True)
            print(f'  保存: {kg_path}', flush=True)

        except KeyboardInterrupt:
            print('\n\n用户中断', flush=True)
            break
        except RuntimeError as e:
            if "所有模型额度均已耗尽" in str(e):
                print(f'\n✗ 所有模型额度均已耗尽，停止处理', flush=True)
                break
            print(f'\n✗ 错误: {e}', flush=True)
            import traceback
            traceback.print_exc()
        except Exception as e:
            print(f'\n✗ 错误: {e}', flush=True)
            import traceback
            traceback.print_exc()

    # 最终总结
    print(f'\n{"="*70}', flush=True)
    print('总结', flush=True)
    print('=' * 70, flush=True)

    all_raw = sorted(glob.glob('data/*_perpage_raw.json'))
    total_q_all = 0
    total_kp_all = 0
    for f in all_raw:
        d = json.load(open(f, encoding='utf-8'))
        q = sum(len(t.get('questions', [])) for t in d.get('topics', []))
        kp = sum(len(t.get('knowledge_points', [])) for t in d.get('topics', []))
        total_q_all += q
        total_kp_all += kp
        print(f'  {os.path.basename(f):<45} 知识点:{kp:3}  题目:{q:3}', flush=True)

    print(f'\n  总计: {total_kp_all} 知识点, {total_q_all} 题目', flush=True)
    print('=' * 70, flush=True)


if __name__ == '__main__':
    main()
