"""
PDF 实体抽取脚本
从 PDF 文件中提取知识点并导入知识图谱

使用方法:
1. 安装依赖: pip install pdfplumber openai
2. 设置 API Key: set OPENAI_API_KEY=your_key 或 set DASHSCOPE_API_KEY=your_key 或 set DASHSCOPE_CLAUDE_API_KEY=your_key
3. 运行: python scripts/extract_entities.py data/常识上册.pdf

支持的 LLM:
- OpenAI GPT (需要 OPENAI_API_KEY)
- 阿里通义千问 (需要 DASHSCOPE_API_KEY)
- 阿里百炼大模型 (需要 DASHSCOPE_CLAUDE_API_KEY)
- 本地 Ollama (需要运行 ollama serve)
"""
import os
import sys
import json
import re
from typing import List, Dict, Optional
from pathlib import Path

# PDF 解析
try:
    import pdfplumber
except ImportError:
    print("请安装 pdfplumber: pip install pdfplumber")
    sys.exit(1)


class PDFExtractor:
    """PDF 文本提取器"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.text_content = ""
        self.pages = []
    
    def extract_text(self) -> str:
        """提取 PDF 全文"""
        print(f"正在读取 PDF: {self.pdf_path}")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"共 {total_pages} 页")
            
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                self.pages.append(text)
                self.text_content += text + "\n\n"
                
                if (i + 1) % 10 == 0:
                    print(f"  已处理 {i + 1}/{total_pages} 页...")
        
        print(f"提取完成，共 {len(self.text_content)} 字符")
        return self.text_content
    
    def extract_by_pages(self, start: int = 0, end: int = None) -> str:
        """提取指定页范围的文本"""
        if not self.pages:
            self.extract_text()
        
        end = end or len(self.pages)
        return "\n\n".join(self.pages[start:end])
    
    def get_structure(self) -> List[str]:
        """尝试提取目录结构"""
        if not self.text_content:
            self.extract_text()
        
        # 匹配常见的章节标题模式
        patterns = [
            r'^第[一二三四五六七八九十]+[章节篇].*$',
            r'^[一二三四五六七八九十]+、.*$',
            r'^[（\(][一二三四五六七八九十]+[）\)].*$',
            r'^\d+[\.、].*$',
            r'^[A-Z]\.[^\n]+$',
        ]
        
        titles = []
        for line in self.text_content.split('\n'):
            line = line.strip()
            for pattern in patterns:
                if re.match(pattern, line):
                    titles.append(line)
                    break
        
        return titles


class EntityExtractor:
    """实体抽取器 - 使用 LLM 进行实体抽取"""
    
    def __init__(self, llm_type: str = "auto"):
        """
        初始化实体抽取器
        
        Args:
            llm_type: "openai", "dashscope", "dashscope_claude", "doubao", "ollama" 或 "auto"
        """
        self.llm_type = self._detect_llm(llm_type)
        self.client = None
        self._init_client()
    
    def _detect_llm(self, llm_type: str) -> str:
        """自动检测可用的 LLM"""
        if llm_type != "auto":
            return llm_type
        
        if os.getenv("DASHSCOPE_CLAUDE_API_KEY"):
            return "dashscope_claude"
        elif os.getenv("ARK_API_KEY"):
            return "doubao"
        elif os.getenv("OPENAI_API_KEY"):
            return "openai"
        elif os.getenv("DASHSCOPE_API_KEY"):
            return "dashscope"
        else:
            return "ollama"
    
    def _init_client(self):
        """初始化 LLM 客户端"""
        if self.llm_type == "dashscope_claude":
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                    api_key=os.getenv("DASHSCOPE_CLAUDE_API_KEY")
                )
                print("使用阿里百炼大模型平台")
            except ImportError:
                print("请安装 openai: pip install openai")
                sys.exit(1)
        
        elif self.llm_type == "doubao":
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    base_url="https://ark.cn-beijing.volces.com/api/v3",
                    api_key=os.getenv("ARK_API_KEY")
                )
                print("使用字节豆包 (Doubao)")
            except ImportError:
                print("请安装 openai: pip install openai")
                sys.exit(1)
        
        elif self.llm_type == "openai":
            try:
                from openai import OpenAI
                self.client = OpenAI()
                print("使用 OpenAI GPT")
            except ImportError:
                print("请安装 openai: pip install openai")
                sys.exit(1)
        
        elif self.llm_type == "dashscope":
            try:
                import dashscope
                dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
                self.client = dashscope
                print("使用阿里通义千问")
            except ImportError:
                print("请安装 dashscope: pip install dashscope")
                sys.exit(1)
        
        elif self.llm_type == "ollama":
            try:
                import requests
                # 测试 Ollama 是否运行
                resp = requests.get("http://localhost:11434/api/tags", timeout=5)
                if resp.status_code == 200:
                    print("使用本地 Ollama")
                else:
                    print("Ollama 服务未响应")
                    sys.exit(1)
            except Exception as e:
                print(f"无法连接 Ollama: {e}")
                print("请确保 Ollama 正在运行: ollama serve")
                sys.exit(1)
    
    def _call_llm(self, prompt: str, system_prompt: str = "") -> str:
        """调用 LLM"""
        if self.llm_type == "dashscope_claude":
            response = self.client.chat.completions.create(
                model="claude-3-5-sonnet",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        
        elif self.llm_type == "doubao":
            response = self.client.chat.completions.create(
                model="doubao-seed-1-6-flash-250828",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        
        elif self.llm_type == "openai":
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        
        elif self.llm_type == "dashscope":
            from dashscope import Generation
            response = Generation.call(
                model="qwen-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.output.text
        
        elif self.llm_type == "ollama":
            import requests
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:7b",  # 或 llama3, mistral 等
                    "prompt": f"{system_prompt}\n\n{prompt}",
                    "stream": False
                }
            )
            return response.json().get("response", "")
    
    def extract_knowledge_points(self, text: str, category: str = "常识判断") -> Dict:
        """
        从文本中抽取知识点和题目
        
        Args:
            text: 待抽取的文本
            category: 所属分类
        
        Returns:
            抽取的实体和关系
        """
        system_prompt = """你是一个公务员考试知识图谱构建专家。
请从给定的文本中抽取知识点和题目，并按照以下 JSON 格式输出：

{
  "chapter": "章节名称",
  "topics": [
    {
      "name": "主题名称",
      "knowledge_points": [
        {
          "name": "知识点名称",
          "content": "知识点详细内容",
          "keywords": ["关键词1", "关键词2"],
          "difficulty": 3,
          "importance": 4
        }
      ],
      "questions": [
        {
          "content": "完整的题目内容",
          "options": {"A": "选项A内容", "B": "选项B内容", "C": "选项C内容", "D": "选项D内容"},
          "answer": "正确答案字母",
          "analysis": "答案解析",
          "difficulty": 3
        }
      ]
    }
  ]
}

要求：
1. 知识点名称简洁准确（5-15字）
2. content 包含完整的知识点内容
3. 提取 2-5 个关键词
4. difficulty 和 importance 为 1-5 的整数
5. 题目要完整提取，包括题干、选项、答案和解析
6. 只输出一个完整的 JSON 对象，不要输出多个 JSON"""

        prompt = f"""请从以下公务员考试"{category}"相关文本中抽取知识点和题目：

---
{text[:4000]}
---

请严格按照 JSON 格式输出，确保只输出一个完整的 JSON 对象。"""

        try:
            response = self._call_llm(prompt, system_prompt)
            
            # 尝试多种方式提取 JSON
            result = self._parse_json_response(response)
            if result:
                return result
            else:
                print(f"无法解析响应: {response[:200]}")
                return {}
        except Exception as e:
            print(f"LLM 调用失败: {e}")
            return {}
    
    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """尝试多种方式解析 JSON 响应"""
        # 方法1: 直接解析
        try:
            return json.loads(response)
        except:
            pass
        
        # 方法2: 提取第一个完整的 JSON 对象
        try:
            # 找到第一个 { 和匹配的 }
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
            
            json_str = response[start:end]
            return json.loads(json_str)
        except:
            pass
        
        # 方法3: 使用正则提取并清理
        try:
            json_match = re.search(r'\{[\s\S]*?\}(?=\s*$|\s*\{)', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # 方法4: 尝试修复常见问题
        try:
            # 移除 markdown 代码块标记
            cleaned = re.sub(r'```json?\s*', '', response)
            cleaned = re.sub(r'```\s*$', '', cleaned)
            
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            if start != -1 and end > start:
                json_str = cleaned[start:end]
                return json.loads(json_str)
        except:
            pass
        
        return None
    
    def extract_structure(self, text: str) -> List[Dict]:
        """从文本中抽取知识结构"""
        system_prompt = """你是公务员考试知识结构分析专家。
请分析文本的知识结构，识别章节、主题层次。

输出 JSON 格式：
{
  "chapters": [
    {
      "name": "章节名",
      "topics": ["主题1", "主题2"]
    }
  ]
}"""
        
        prompt = f"""请分析以下文本的知识结构：

{text[:6000]}

只输出 JSON。"""
        
        try:
            response = self._call_llm(prompt, system_prompt)
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception as e:
            print(f"结构分析失败: {e}")
            return {}


class KnowledgeGraphBuilder:
    """知识图谱构建器"""
    
    def __init__(self):
        self.nodes = {
            "Chapter": [],
            "Topic": [],
            "KnowledgePoint": [],
            "Question": []
        }
        self.relationships = {
            "HAS_CHAPTER": [],
            "HAS_TOPIC": [],
            "HAS_KNOWLEDGE": [],
            "BELONGS_TO_TOPIC": [],
            "TESTS": []
        }
        self.id_counter = 0
    
    def _generate_id(self, prefix: str) -> str:
        """生成唯一 ID"""
        self.id_counter += 1
        return f"{prefix}_{self.id_counter}"
    
    def add_from_extraction(self, data: Dict, parent_module_id: str = None) -> None:
        """从抽取结果添加节点和关系"""
        if not data:
            return
        
        chapter_name = data.get("chapter", "未知章节")
        chapter_id = self._generate_id("ch_pdf")
        
        self.nodes["Chapter"].append({
            "id": chapter_id,
            "name": chapter_name,
            "code": f"PDF_{self.id_counter}",
            "description": f"从 PDF 抽取的章节: {chapter_name}",
            "order": len(self.nodes["Chapter"]) + 1
        })
        
        if parent_module_id:
            self.relationships["HAS_CHAPTER"].append({
                "from_id": parent_module_id,
                "to_id": chapter_id,
                "properties": {}
            })
        
        for topic_data in data.get("topics", []):
            topic_id = self._generate_id("tp_pdf")
            topic_name = topic_data.get("name", "未知主题")
            
            self.nodes["Topic"].append({
                "id": topic_id,
                "name": topic_name,
                "code": f"PDF_{self.id_counter}",
                "description": f"从 PDF 抽取的主题: {topic_name}",
                "difficulty": 3,
                "order": len(self.nodes["Topic"]) + 1
            })
            
            self.relationships["HAS_TOPIC"].append({
                "from_id": chapter_id,
                "to_id": topic_id,
                "properties": {}
            })
            
            # 处理知识点
            for kp_data in topic_data.get("knowledge_points", []):
                kp_id = self._generate_id("kp_pdf")
                
                self.nodes["KnowledgePoint"].append({
                    "id": kp_id,
                    "name": kp_data.get("name", "未知知识点"),
                    "content": kp_data.get("content", ""),
                    "keywords": ",".join(kp_data.get("keywords", [])),
                    "difficulty": kp_data.get("difficulty", 3),
                    "importance": kp_data.get("importance", 3)
                })
                
                self.relationships["HAS_KNOWLEDGE"].append({
                    "from_id": topic_id,
                    "to_id": kp_id,
                    "properties": {}
                })
            
            # 处理题目
            for q_data in topic_data.get("questions", []):
                q_id = self._generate_id("q_pdf")
                
                # 处理选项
                options = q_data.get("options", {})
                if isinstance(options, dict):
                    options_str = json.dumps(options, ensure_ascii=False)
                else:
                    options_str = str(options)
                
                self.nodes["Question"].append({
                    "id": q_id,
                    "content": q_data.get("content", ""),
                    "options": options_str,
                    "answer": q_data.get("answer", ""),
                    "analysis": q_data.get("analysis", ""),
                    "difficulty": q_data.get("difficulty", 3),
                    "year": 2026,
                    "exam_type": "练习题"
                })
                
                # 题目属于主题
                self.relationships["BELONGS_TO_TOPIC"].append({
                    "from_id": q_id,
                    "to_id": topic_id,
                    "properties": {}
                })
    
    def to_json(self) -> Dict:
        """导出为 JSON 格式"""
        return {
            "nodes": self.nodes,
            "relationships": self.relationships
        }
    
    def save(self, output_path: str) -> None:
        """保存到文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_json(), f, ensure_ascii=False, indent=2)
        print(f"已保存到: {output_path}")
    
    def stats(self) -> Dict:
        """统计信息"""
        return {
            "章节数": len(self.nodes["Chapter"]),
            "主题数": len(self.nodes["Topic"]),
            "知识点数": len(self.nodes["KnowledgePoint"]),
            "题目数": len(self.nodes["Question"])
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="从 PDF 提取知识点")
    parser.add_argument("pdf_path", help="PDF 文件路径")
    parser.add_argument("--output", "-o", default=None, help="输出 JSON 文件路径")
    parser.add_argument("--llm", choices=["openai", "dashscope", "dashscope_claude", "doubao", "ollama", "auto"], 
                        default="auto", help="选择 LLM")
    parser.add_argument("--pages", type=str, default=None, 
                        help="指定页码范围，如 1-10")
    parser.add_argument("--preview", action="store_true", 
                        help="仅预览 PDF 结构，不进行实体抽取")
    parser.add_argument("--module-id", default=None,
                        help="关联到的模块 ID（用于导入时建立关系）")
    
    args = parser.parse_args()
    
    # 检查文件
    if not os.path.exists(args.pdf_path):
        print(f"文件不存在: {args.pdf_path}")
        sys.exit(1)
    
    # 提取 PDF 文本
    pdf_extractor = PDFExtractor(args.pdf_path)
    
    if args.pages:
        start, end = map(int, args.pages.split('-'))
        text = pdf_extractor.extract_by_pages(start - 1, end)
    else:
        text = pdf_extractor.extract_text()
    
    # 预览模式
    if args.preview:
        print("\n" + "="*60)
        print("PDF 结构预览")
        print("="*60)
        
        structure = pdf_extractor.get_structure()
        for title in structure[:30]:
            print(f"  {title}")
        
        if len(structure) > 30:
            print(f"  ... 共 {len(structure)} 个标题")
        
        print("\n前 2000 字内容预览:")
        print("-"*60)
        print(text[:2000])
        print("-"*60)
        return
    
    # 实体抽取
    print("\n" + "="*60)
    print("开始实体抽取")
    print("="*60)
    
    entity_extractor = EntityExtractor(args.llm)
    kg_builder = KnowledgeGraphBuilder()
    
    # 分段处理（每段约 3000 字）
    segments = []
    segment_size = 3000
    for i in range(0, len(text), segment_size):
        segment = text[i:i + segment_size]
        if len(segment.strip()) > 100:  # 忽略太短的段落
            segments.append(segment)
    
    print(f"共 {len(segments)} 个文本段落需要处理")
    
    for i, segment in enumerate(segments):
        print(f"\n处理段落 {i + 1}/{len(segments)}...")
        result = entity_extractor.extract_knowledge_points(segment, "常识判断")
        if result:
            kg_builder.add_from_extraction(result, args.module_id)
            print(f"  ✓ 抽取成功")
        else:
            print(f"  ✗ 抽取失败")
    
    # 统计和保存
    stats = kg_builder.stats()
    print("\n" + "="*60)
    print("抽取结果统计")
    print("="*60)
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    # 保存结果
    output_path = args.output or args.pdf_path.replace('.pdf', '_entities.json')
    kg_builder.save(output_path)
    
    print("\n" + "="*60)
    print("后续步骤")
    print("="*60)
    print(f"1. 查看抽取结果: {output_path}")
    print(f"2. 导入知识图谱: python scripts/import_data.py {output_path}")


if __name__ == "__main__":
    main()
