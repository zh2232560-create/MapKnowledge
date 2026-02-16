# PDF 实体抽取快速参考

## 一句话说明

将 PDF 文本通过 AI 模型自动提取知识点，存储到 Neo4j 知识图谱中。

## 基本命令

### 处理单个 PDF
```bash
python scripts/batch_extract_and_import.py --pdf 常识上册
```

### 处理所有 PDF
```bash
python scripts/batch_extract_and_import.py
```

### 只导入已有的 JSON
```bash
python import_entities.py data/常识上册_entities_extracted.json
```

## 工作原理

```
常识上册.pdf
    ↓ 提取文本 (pdfplumber)
文本内容 (25,406 字符)
    ↓ AI 实体抽取 (qwen-max 模型)
JSON 结构化数据
├── 知识点 (文化常识、文学常识等)
├── 题目 (包含选项和解析)
└── 分类关系
    ↓ 转换为图谱格式
Neo4j 知识图谱
├── Chapter (常识判断)
├── Topic (人文常识)
├── KnowledgePoint (文化常识、历史常识等)
└── Question (具体题目)
```

## 已支持的 PDF

| 分类 | 文件 | 状态 |
|------|------|------|
| 常识判断 | 常识上册.pdf | ✓ 已处理 |
| 常识判断 | 常识下册.pdf | 待处理 |
| 判断推理 | 判断推理上册(1).pdf | 待处理 |
| 判断推理 | 判断推理下册(1).pdf | 待处理 |
| 数量关系 | 数量上册(1).pdf | 待处理 |
| 数量关系 | 数量下册(1).pdf | 待处理 |
| 言语理解 | 言语上册(1).pdf | 待处理 |
| 言语理解 | 言语下册(1).pdf | 待处理 |
| 资料分析 | 资料分析上册(1).pdf | 待处理 |
| 资料分析 | 资料分析下册(1).pdf | 待处理 |

## 常用场景

### 场景 1：处理单个 PDF
```bash
python scripts/batch_extract_and_import.py --pdf 判断推理
```
会找到并处理所有包含 "判断推理" 的 PDF 文件。

### 场景 2：启动 Neo4j 后导入
```bash
# 启动数据库
start_neo4j.bat

# 导入数据
python import_entities.py data/*_entities_extracted.json
```

### 场景 3：清空数据库后重新导入
```bash
python scripts/batch_extract_and_import.py --clear
```
会询问是否确认清空，然后重新处理所有 PDF。

## 输出文件

处理完的 PDF 会生成对应的 JSON 文件：
- `常识上册_entities_extracted.json`：包含提取的知识点和题目

JSON 文件格式：
```json
{
  "nodes": [
    {
      "id": "chapter_常识判断",
      "label": "Chapter",
      "properties": {"name": "常识判断", ...}
    },
    {
      "id": "kp_文化常识",
      "label": "KnowledgePoint",
      "properties": {"name": "文化常识", "content": "...", ...}
    }
  ],
  "relationships": [
    {
      "type": "BELONGS_TO_CHAPTER",
      "start_node": {"value": "topic_人文常识"},
      "end_node": {"value": "chapter_常识判断"}
    }
  ]
}
```

## 性能参数

- **PDF 提取**：约 5-10 秒/100 页
- **实体抽取**：约 30-60 秒/PDF（取决于内容和网络）
- **数据导入**：约 2-5 秒/PDF

## 问题排查

| 问题 | 原因 | 解决方案 |
|------|------|--------|
| "pdfplumber not found" | 未安装依赖 | `pip install pdfplumber` |
| "qwen-max model not found" | API 配置错误 | 检查 API Key |
| "Neo4j connection failed" | 数据库未启动 | 运行 `start_neo4j.bat` |
| Unicode 编码错误 | PowerShell 编码问题 | 使用 Python 脚本而非 cmd |

## 关键文件说明

| 文件 | 用途 |
|------|------|
| `scripts/batch_extract_and_import.py` | 核心脚本，处理 PDF 和导入 |
| `import_entities.py` | 单独导入 JSON 文件 |
| `scripts/extract_entities.py` | 实体抽取核心库 |
| `scripts/import_data.py` | Neo4j 导入库 |
| `PDF_EXTRACTION_GUIDE.md` | 详细文档 |

## API 配置

**LLM:** 阿里百炼 DashScope
- Model: `qwen-max`
- API Key: `sk-69b4138e853648a79659aa01cc859dd6`
- Endpoint: `https://dashscope.aliyuncs.com/compatible-mode/v1`

**Neo4j:** 本地部署
- URI: `bolt://localhost:7687`
- User: `neo4j`
- Password: `5211314zhg`

## 后续计划

- [ ] 处理其他 9 个 PDF 文件
- [ ] 支持增量更新
- [ ] OCR 识别扫描版 PDF
- [ ] Web UI 可视化界面
- [ ] 知识图谱查询接口

---

**更新时间：** 2026-02-16  
**状态：** 核心功能完成，常识上册 PDF 处理示例成功
