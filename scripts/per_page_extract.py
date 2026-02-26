#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
每页提取 PDF 题目和知识点

核心思路：
1. 逐页提取 PDF 文本
2. 每页调用 LLM 提取题目和知识点
3. 智能合并 + 去重
4. 输出标准 JSON 格式
5. 自动导入 Neo4j

使用方法:
  python scripts/per_page_extract.py                          # 处理所有 PDF
  python scripts/per_page_extract.py --pdf "常识上册.pdf"      # 处理指定 PDF
  python scripts/per_page_extract.py --pdf "常识上册.pdf" --no-import  # 只提取不导入
"""

import os
import sys
import json
import re
import time
import pdfplumber
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from import_data import KnowledgeGraphImporter

# 配置
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "5211314zhg")

# ======================================================================
# 多模型配置 —— 按优先级排列，额度耗尽自动切换下一个
# ======================================================================
DASHSCOPE_MODELS = [
    {"name": "qwen-max",             "desc": "通义千问-Max（旗舰）"},
    {"name": "qwen-plus",            "desc": "通义千问-Plus（高性价比）"},
    {"name": "qwen-turbo",           "desc": "通义千问-Turbo（高速）"},
    {"name": "qwen-max-latest",      "desc": "通义千问-Max-最新版"},
    {"name": "qwen-plus-latest",     "desc": "通义千问-Plus-最新版"},
    {"name": "qwen-turbo-latest",    "desc": "通义千问-Turbo-最新版"},
    {"name": "qwen2.5-72b-instruct", "desc": "Qwen2.5-72B"},
    {"name": "qwen2.5-32b-instruct", "desc": "Qwen2.5-32B"},
    {"name": "qwen-long",            "desc": "通义千问-Long（长文本）"},
]


class PerPageExtractor:
    """每页提取器（支持多模型自动切换）"""

    def __init__(self):
        from openai import OpenAI
        api_key = os.getenv("DASHSCOPE_CLAUDE_API_KEY", "sk-69b4138e853648a79659aa01cc859dd6")
        self.client = OpenAI(
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key=api_key,
            timeout=120.0,
        )
        self.models = list(DASHSCOPE_MODELS)          # 可用模型队列（会被裁剪）
        self.current_model_idx = 0                    # 当前使用的模型下标
        self.exhausted_models: set = set()            # 已耗尽额度的模型名
        self.stats = {"pages": 0, "questions": 0, "knowledge_points": 0, "skipped": 0}

        # 探测第一个可用模型
        self._probe_available_model()

    # 精简系统提示词（比 extract_knowledge_points 的短很多，加速 API 响应）
    SYSTEM_PROMPT = """你是公务员考试知识提取专家。从文本中提取知识点和题目，严格输出JSON格式：
{"chapter":"章节名","topics":[{"name":"主题名","knowledge_points":[{"name":"知识点","content":"内容","keywords":["词"],"difficulty":3,"importance":4}],"questions":[{"id":"q001","content":"题目","options":{"A":"","B":"","C":"","D":""},"answer":"A","analysis":"解析","difficulty":3,"related_knowledge_points":["知识点"]}]}]}

规则：1.提取所有题目（选择题/判断题/例题/习题）2.提取所有知识点 3.题目必须关联知识点 4.只输出JSON"""

    # ------------------------------------------------------------------
    # 多模型管理
    # ------------------------------------------------------------------
    @property
    def current_model(self) -> str:
        return self.models[self.current_model_idx]["name"]

    @property
    def current_model_desc(self) -> str:
        return self.models[self.current_model_idx]["desc"]

    def _is_quota_error(self, exc: Exception) -> bool:
        """判断是否为额度耗尽错误（403 AllocationQuota）"""
        msg = str(exc)
        return "AllocationQuota" in msg or ("403" in msg and "free tier" in msg.lower())

    def _switch_to_next_model(self) -> bool:
        """切换到下一个可用模型，返回是否成功"""
        old = self.current_model
        self.exhausted_models.add(old)
        print(f"\n  ⚠ 模型 [{old}] 额度耗尽，尝试切换...", flush=True)

        # 在剩余模型中找下一个未耗尽的
        for i, m in enumerate(self.models):
            if m["name"] not in self.exhausted_models:
                self.current_model_idx = i
                print(f"  → 切换到模型: [{self.current_model}] ({self.current_model_desc})", flush=True)
                return True

        print("  ✗ 所有模型额度均已耗尽，无法继续！", flush=True)
        return False

    def _probe_available_model(self):
        """启动时快速探测第一个有额度的模型"""
        print("探测可用模型...", flush=True)
        for i, m in enumerate(self.models):
            model_name = m["name"]
            try:
                resp = self.client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": "hi"}],
                    max_tokens=5,
                    temperature=0,
                )
                self.current_model_idx = i
                print(f"  ✓ 使用模型: [{model_name}] ({m['desc']})\n", flush=True)
                return
            except Exception as e:
                if self._is_quota_error(e):
                    print(f"  ✗ [{model_name}] 额度耗尽", flush=True)
                    self.exhausted_models.add(model_name)
                else:
                    # 其他错误（网络等），也可以用这个模型
                    self.current_model_idx = i
                    print(f"  ? [{model_name}] 探测异常({e})，仍尝试使用\n", flush=True)
                    return
        print("  ✗ 所有模型额度均已耗尽！", flush=True)
        sys.exit(1)

    def _call_llm(self, prompt: str, system_prompt: str = "") -> str:
        """调用 LLM（带额度耗尽自动切换）"""
        while True:
            try:
                response = self.client.chat.completions.create(
                    model=self.current_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                )
                return response.choices[0].message.content
            except Exception as e:
                if self._is_quota_error(e):
                    if not self._switch_to_next_model():
                        raise RuntimeError("所有模型额度均已耗尽") from e
                    # 切换成功，立即用新模型重试
                    continue
                else:
                    raise

    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """尝试多种方式解析 JSON 响应"""
        # 直接解析
        try:
            return json.loads(response)
        except Exception:
            pass
        # 提取 { ... }
        try:
            start = response.find('{')
            if start == -1:
                return None
            depth = 0
            end = start
            for i, char in enumerate(response[start:], start):
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            return json.loads(response[start:end])
        except Exception:
            pass
        # 去掉 ```json 标记
        try:
            cleaned = re.sub(r'```json?\s*', '', response)
            cleaned = re.sub(r'```\s*$', '', cleaned)
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(cleaned[start:end])
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------
    # 核心：按页提取
    # ------------------------------------------------------------------
    def extract_pdf(self, pdf_path: str, category: str = "常识判断") -> Dict:
        """
        逐页提取一个 PDF 的题目和知识点，最后智能合并。
        """
        print(f"\n正在处理: {pdf_path}")
        pages_data: List[Dict] = []

        with pdfplumber.open(pdf_path) as pdf:
            total = len(pdf.pages)
            print(f"共 {total} 页\n")

            for idx, page in enumerate(pdf.pages):
                page_no = idx + 1
                text = (page.extract_text() or "").strip()

                # 跳过内容太少的页（目录页、空白页等）
                if len(text) < 80:
                    self.stats["skipped"] += 1
                    continue

                print(f"  [{page_no:>3}/{total}]", end=" ", flush=True)

                page_result = self._extract_single_page(text, category, page_no)
                if page_result:
                    pages_data.append(page_result)
                    q = sum(len(t.get("questions", [])) for t in page_result.get("topics", []))
                    kp = sum(len(t.get("knowledge_points", [])) for t in page_result.get("topics", []))
                    print(f"✓ 知识点 {kp}  题目 {q}", flush=True)
                else:
                    print("- (无结构化内容)", flush=True)

                self.stats["pages"] += 1

        # 合并所有页的结果
        merged = self._merge_pages(pages_data, category)
        return merged

    def _extract_single_page(self, text: str, category: str, page_no: int) -> Optional[Dict]:
        """调用 LLM 提取单页内容（带超时、重试和模型自动切换）"""
        prompt = f"从以下「{category}」教材第{page_no}页提取知识点和题目，题目ID用q_p{page_no}_序号格式，只返回JSON：\n\n{text}"

        max_retries = 2
        for attempt in range(max_retries):
            try:
                time.sleep(1)

                response = self._call_llm(prompt, self.SYSTEM_PROMPT)
                data = self._parse_json_response(response)

                if data and data.get("topics"):
                    # 给题目 ID 加页码前缀，避免跨页重复
                    for topic in data.get("topics", []):
                        for i, q in enumerate(topic.get("questions", [])):
                            if not q.get("id") or not q["id"].startswith(f"q_p{page_no}"):
                                q["id"] = f"q_p{page_no}_{i+1:03d}"
                    return data
                return None
            except KeyboardInterrupt:
                raise
            except RuntimeError as e:
                # 所有模型耗尽，直接向上抛出
                if "所有模型额度均已耗尽" in str(e):
                    raise
                if attempt < max_retries - 1:
                    print(f"[RETRY p{page_no}] {e}", flush=True)
                    time.sleep(3)
                else:
                    print(f"[ERR p{page_no}] {e}", flush=True)
                    return None
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"[RETRY p{page_no}] {e}", flush=True)
                    time.sleep(3)
                else:
                    print(f"[ERR p{page_no}] {e}", flush=True)
                    return None

    # ------------------------------------------------------------------
    # 智能合并 + 去重
    # ------------------------------------------------------------------
    def _merge_pages(self, pages_data: List[Dict], category: str) -> Dict:
        """合并所有页的提取结果"""
        print(f"\n合并 {len(pages_data)} 页的提取结果...")

        chapter_name = category
        for p in pages_data:
            if p.get("chapter"):
                chapter_name = p["chapter"]
                break

        # 按主题名合并
        topic_map: Dict[str, Dict] = {}

        for page in pages_data:
            for topic in page.get("topics", []):
                topic_name = self._normalize_topic_name(topic.get("name", ""))
                if not topic_name:
                    topic_name = "通用"

                if topic_name not in topic_map:
                    topic_map[topic_name] = {
                        "name": topic.get("name", topic_name),
                        "knowledge_points": [],
                        "questions": []
                    }

                # 合并知识点（去重）
                for kp in topic.get("knowledge_points", []):
                    if not self._is_duplicate_kp(kp, topic_map[topic_name]["knowledge_points"]):
                        topic_map[topic_name]["knowledge_points"].append(kp)

                # 合并题目（去重）
                for q in topic.get("questions", []):
                    if not self._is_duplicate_question(q, topic_map[topic_name]["questions"]):
                        topic_map[topic_name]["questions"].append(q)

        # 建立题目-知识点关联
        for topic in topic_map.values():
            kp_names = [kp["name"] for kp in topic["knowledge_points"]]
            for q in topic["questions"]:
                if not q.get("related_knowledge_points"):
                    # 自动关联：用关键词匹配最相关的知识点
                    q["related_knowledge_points"] = self._auto_link_kps(q, kp_names)

        merged = {
            "chapter": chapter_name,
            "topics": list(topic_map.values())
        }

        # 统计
        total_kp = sum(len(t["knowledge_points"]) for t in merged["topics"])
        total_q = sum(len(t["questions"]) for t in merged["topics"])
        self.stats["questions"] = total_q
        self.stats["knowledge_points"] = total_kp

        print(f"合并完成: {len(merged['topics'])} 个主题, {total_kp} 个知识点, {total_q} 道题目")
        return merged

    def _normalize_topic_name(self, name: str) -> str:
        """标准化主题名（去空白、统一格式）"""
        name = name.strip()
        # 去除常见前缀
        name = re.sub(r'^(第[一二三四五六七八九十\d]+[章节篇]\s*)', '', name)
        return name

    def _is_duplicate_kp(self, new_kp: Dict, existing: List[Dict]) -> bool:
        """检查知识点是否重复"""
        new_name = new_kp.get("name", "")
        for kp in existing:
            if kp.get("name") == new_name:
                return True
            # 相似度 > 0.85 也认为重复
            if SequenceMatcher(None, new_name, kp.get("name", "")).ratio() > 0.85:
                return True
        return False

    def _is_duplicate_question(self, new_q: Dict, existing: List[Dict]) -> bool:
        """检查题目是否重复"""
        new_content = new_q.get("content", "")
        if not new_content:
            return True
        for q in existing:
            old_content = q.get("content", "")
            # 完全相同或相似度 > 0.8
            if new_content == old_content:
                return True
            if len(new_content) > 20 and len(old_content) > 20:
                if SequenceMatcher(None, new_content, old_content).ratio() > 0.8:
                    return True
        return False

    def _auto_link_kps(self, question: Dict, kp_names: List[str]) -> List[str]:
        """自动关联题目到知识点"""
        q_text = question.get("content", "") + question.get("analysis", "")
        linked = []
        for kp_name in kp_names:
            # 简单关键词匹配
            if kp_name in q_text or any(kw in q_text for kw in kp_name.split("、")):
                linked.append(kp_name)
        # 至少关联一个（如果有知识点的话）
        if not linked and kp_names:
            linked.append(kp_names[0])
        return linked[:3]  # 最多关联3个

    # ------------------------------------------------------------------
    # 转换为 Neo4j 导入格式
    # ------------------------------------------------------------------
    def convert_to_kg_format(self, entities: Dict) -> Dict:
        """转换为 nodes + relationships 格式"""
        nodes = []
        relationships = []
        node_ids = set()

        chapter = entities.get("chapter", "Unknown")
        chapter_id = f"chapter_{chapter.replace(' ', '_')}"

        if chapter_id not in node_ids:
            nodes.append({
                "id": chapter_id,
                "label": "Chapter",
                "properties": {"name": chapter, "created_at": datetime.now().isoformat()}
            })
            node_ids.add(chapter_id)

        for topic in entities.get("topics", []):
            topic_name = topic.get("name", "Unknown")
            topic_id = f"topic_{topic_name.replace(' ', '_')}"

            if topic_id not in node_ids:
                nodes.append({
                    "id": topic_id,
                    "label": "Topic",
                    "properties": {"name": topic_name, "created_at": datetime.now().isoformat()}
                })
                node_ids.add(topic_id)
                relationships.append({
                    "type": "BELONGS_TO_CHAPTER",
                    "start_node": {"value": topic_id},
                    "end_node": {"value": chapter_id},
                    "properties": {}
                })

            for kp in topic.get("knowledge_points", []):
                kp_name = kp.get("name", "Unknown")
                kp_id = f"kp_{kp_name.replace(' ', '_')}"

                if kp_id not in node_ids:
                    nodes.append({
                        "id": kp_id,
                        "label": "KnowledgePoint",
                        "properties": {
                            "name": kp_name,
                            "content": kp.get("content", ""),
                            "keywords": json.dumps(kp.get("keywords", []), ensure_ascii=False),
                            "difficulty": kp.get("difficulty", 3),
                            "importance": kp.get("importance", 3),
                            "created_at": datetime.now().isoformat()
                        }
                    })
                    node_ids.add(kp_id)
                    relationships.append({
                        "type": "BELONGS_TO_TOPIC",
                        "start_node": {"value": kp_id},
                        "end_node": {"value": topic_id},
                        "properties": {}
                    })

            for q in topic.get("questions", []):
                q_id = q.get("id", f"q_{hash(q.get('content',''))}")
                if q_id not in node_ids:
                    nodes.append({
                        "id": q_id,
                        "label": "Question",
                        "properties": {
                            "content": q.get("content", ""),
                            "options": json.dumps(q.get("options", {}), ensure_ascii=False),
                            "answer": q.get("answer", ""),
                            "analysis": q.get("analysis", ""),
                            "difficulty": q.get("difficulty", 3),
                            "created_at": datetime.now().isoformat()
                        }
                    })
                    node_ids.add(q_id)
                    relationships.append({
                        "type": "BELONGS_TO_TOPIC",
                        "start_node": {"value": q_id},
                        "end_node": {"value": topic_id},
                        "properties": {}
                    })

                for kp_name in q.get("related_knowledge_points", []):
                    kp_id = f"kp_{kp_name.replace(' ', '_')}"
                    relationships.append({
                        "type": "RELATED_TO_KNOWLEDGE_POINT",
                        "start_node": {"value": q_id},
                        "end_node": {"value": kp_id},
                        "properties": {}
                    })

        return {"nodes": nodes, "relationships": relationships}


# ======================================================================
# 批量处理入口
# ======================================================================

def find_pdfs(data_dir: str, pattern: Optional[str] = None) -> List[str]:
    """查找 PDF 文件"""
    import glob
    if pattern:
        files = glob.glob(os.path.join(data_dir, f"*{pattern}*"))
    else:
        files = glob.glob(os.path.join(data_dir, "*.pdf"))
    return sorted([f for f in files if f.endswith(".pdf")])


def get_category(filename: str) -> str:
    """从文件名推断分类"""
    mapping = {
        "常识": "常识判断", "判断推理": "判断推理",
        "数量": "数量关系", "言语": "言语理解", "资料分析": "资料分析"
    }
    for key, val in mapping.items():
        if key in filename:
            return val
    return "通用知识"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="每页提取 PDF 题目和知识点")
    parser.add_argument("--pdf", type=str, help="指定 PDF 文件名（模糊匹配）")
    parser.add_argument("--data-dir", default="data", help="PDF 所在目录")
    parser.add_argument("--no-import", action="store_true", help="只提取不导入")
    parser.add_argument("--clear", action="store_true", help="清空数据库后导入")
    args = parser.parse_args()

    pdfs = find_pdfs(args.data_dir, args.pdf)
    if not pdfs:
        print("[ERROR] 未找到 PDF 文件")
        return

    print("="*70)
    print("每页提取模式")
    print("="*70)
    print(f"找到 {len(pdfs)} 个 PDF:\n")
    for p in pdfs:
        print(f"  · {os.path.basename(p)}")

    extractor = PerPageExtractor()
    json_files = []

    for i, pdf_path in enumerate(pdfs, 1):
        print(f"\n{'='*70}")
        print(f"[{i}/{len(pdfs)}] {os.path.basename(pdf_path)}")
        print("="*70)

        category = get_category(os.path.basename(pdf_path))

        # 每页提取
        entities = extractor.extract_pdf(pdf_path, category)

        # 转换格式
        kg_data = extractor.convert_to_kg_format(entities)

        # 保存 JSON
        stem = Path(pdf_path).stem
        out_path = os.path.join(args.data_dir, f"{stem}_perpage.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(kg_data, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 已保存: {out_path}")

        # 同时保存原始合并数据（方便调试）
        raw_path = os.path.join(args.data_dir, f"{stem}_perpage_raw.json")
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(entities, f, ensure_ascii=False, indent=2)

        json_files.append(out_path)

        # 打印统计
        n_nodes = len(kg_data.get("nodes", []))
        n_rels = len(kg_data.get("relationships", []))
        print(f"  节点: {n_nodes}, 关系: {n_rels}")

    # 导入 Neo4j
    if not args.no_import and json_files:
        print(f"\n{'='*70}")
        print("导入到 Neo4j...")
        print("="*70)

        try:
            importer = KnowledgeGraphImporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

            if args.clear:
                importer.clear_database()

            for jf in json_files:
                print(f"\n导入: {os.path.basename(jf)}")
                importer.import_from_json(jf)

            importer.close()
            print("\n✓ 全部导入完成")
        except Exception as e:
            print(f"\n[ERROR] 导入失败: {e}")

    # 总结
    print(f"\n{'='*70}")
    print("总结")
    print("="*70)
    print(f"  处理页数  : {extractor.stats['pages']}")
    print(f"  跳过页数  : {extractor.stats['skipped']}")
    print(f"  知识点数  : {extractor.stats['knowledge_points']}")
    print(f"  题目数    : {extractor.stats['questions']}")
    print("="*70)


if __name__ == "__main__":
    main()
