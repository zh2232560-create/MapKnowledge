# PDF 实体抽取与知识图谱导入指南

## 概述

本项目支持从 PDF 文件中自动提取实体和知识点，然后导入到 Neo4j 知识图谱中。目前包含 10 个公务员考试相关的 PDF 文档。

## 已支持的 PDF 文件

data 目录下包含以下 PDF 文件：

### 常识判断
- `常识上册.pdf` ✓
- `常识下册.pdf` (待处理)

### 判断推理
- `判断推理上册(1).pdf`
- `判断推理下册(1).pdf`

### 数量关系
- `数量上册(1).pdf`
- `数量下册(1).pdf`

### 言语理解
- `言语上册(1).pdf`
- `言语下册(1).pdf`

### 资料分析
- `资料分析上册(1).pdf`
- `资料分析下册(1).pdf`

## 快速开始

### 1. 处理单个 PDF 文件

```bash
# 处理常识上册
python scripts/batch_extract_and_import.py --pdf 常识上册

# 处理任何包含 "常识" 的 PDF
python scripts/batch_extract_and_import.py --pdf 常识
```

### 2. 批量处理所有 PDF

```bash
python scripts/batch_extract_and_import.py
```

### 3. 清空数据库后导入

```bash
python scripts/batch_extract_and_import.py --clear
```

### 4. 单独导入已有的 JSON 文件

如果 PDF 已经提取为 JSON，可直接导入到知识图谱：

```bash
python import_entities.py data/常识上册_entities_extracted.json

# 批量导入所有提取的 JSON
python import_entities.py data/*_entities_extracted.json
```

## 处理流程

### 第一步：PDF 文本提取
- 使用 `pdfplumber` 库从 PDF 中提取文本
- 保留原始结构和格式
- 支持中文 OCR 识别

### 第二步：实体抽取
- 使用 LLM（阿里百炼 qwen-max 模型）进行智能实体抽取
- 抽取以下内容：
  - **知识点**：名称、内容、关键词、难度、重要性
  - **题目**：题干、选项、答案、解析、难度
  - **分类**：自动根据文件名推断（常识、判断推理、数量关系等）

### 第三步：知识图谱转换
- 将抽取的实体转换为知识图谱格式
- 生成包含以下节点的图：
  - `Chapter`（章节）
  - `Topic`（主题）
  - `KnowledgePoint`（知识点）
  - `Question`（题目）

### 第四步：Neo4j 导入
- 自动创建节点和关系
- 建立以下关系：
  - `BELONGS_TO_CHAPTER`：主题属于章节
  - `BELONGS_TO_TOPIC`：知识点属于主题

## 配置

### LLM 配置

默认使用阿里百炼 DashScope 的 qwen-max 模型，API 密钥已内置：

```
API Key: sk-69b4138e853648a79659aa01cc859dd6
Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
Model: qwen-max
```

### Neo4j 配置

默认连接配置：

```
URI: bolt://localhost:7687
User: neo4j
Password: 5211314zhg
```

可通过环境变量覆盖：
```bash
set NEO4J_URI=bolt://your-server:7687
set NEO4J_USER=your_user
set NEO4J_PASSWORD=your_password
```

## 必要依赖

```bash
# 核心依赖
pip install pdfplumber        # PDF 文本提取
pip install openai            # LLM API 调用
pip install neo4j             # Neo4j 数据库驱动

# 可选依赖（支持其他 LLM）
pip install dashscope         # 阿里通义千问
pip install requests          # HTTP 请求
```

安装所有依赖：
```bash
pip install pdfplumber openai neo4j dashscope requests
```

## 输出文件

### JSON 格式

提取的实体保存为 JSON 文件，格式示例：

```json
{
  "nodes": [
    {
      "id": "chapter_常识判断",
      "label": "Chapter",
      "properties": {
        "name": "常识判断",
        "created_at": "2026-02-16T18:39:55.891217"
      }
    },
    {
      "id": "kp_文化常识",
      "label": "KnowledgePoint",
      "properties": {
        "name": "文化常识",
        "content": "包括夯实基础和高难进阶两部分...",
        "keywords": "[\"文化\", \"基础知识\", \"高难进阶\"]",
        "difficulty": 3,
        "importance": 4,
        "created_at": "2026-02-16T18:39:55.891217"
      }
    }
  ],
  "relationships": [
    {
      "type": "BELONGS_TO_CHAPTER",
      "start_node": {"value": "topic_人文常识"},
      "end_node": {"value": "chapter_常识判断"},
      "properties": {}
    }
  ]
}
```

## 常见问题

### Q: API 请求失败，提示 "The model does not exist"

A: 确保使用的是正确的模型名称。当前使用 `qwen-max` 模型，如需使用 Claude，需要有相应的权限。

### Q: Neo4j 连接失败

A: 
1. 确保 Neo4j 服务已启动：`start_neo4j.bat`
2. 检查连接配置（URI、用户名、密码）
3. 确保防火墙未阻止 7687 端口

### Q: PDF 提取内容为空或很少

A: 可能是 PDF 是扫描版本（图片形式），需要 OCR 支持。当前版本不支持 OCR，建议使用文本版 PDF。

### Q: 实体提取结果不理想

A: 这取决于 PDF 内容的清晰度和结构。可以：
1. 尝试手动调整提取提示语
2. 增加 LLM 的 context 长度
3. 使用更高级的模型（如需权限）

## 脚本说明

### batch_extract_and_import.py

批量处理 PDF 文件的主脚本。

**用途：**
- 扫描目录中的 PDF 文件
- 逐个提取实体
- 保存为 JSON 格式
- 自动导入到知识图谱

**参数：**
- `--pdf <pattern>`：指定要处理的 PDF 文件名模式
- `--clear`：清空数据库（谨慎使用）
- `--data-dir`：PDF 所在目录（默认：data）
- `--output-dir`：输出 JSON 目录（默认：data）

### import_entities.py

单独导入 JSON 文件到知识图谱。

**用途：**
- 导入已生成的 JSON 文件
- 支持批量导入多个文件

**用法：**
```bash
python import_entities.py <json_file> [<json_file2> ...]
```

### extract_entities.py（核心库）

实体抽取的核心模块，包含：

- `PDFExtractor`：PDF 文本提取
- `EntityExtractor`：LLM 实体抽取
- 支持多种 LLM 后端

## 工作流示例

```
PDF 文件
   ↓
PDFExtractor (文本提取)
   ↓
EntityExtractor (LLM 抽取)
   ↓
JSON 文件
   ↓
KnowledgeGraphImporter (导入)
   ↓
Neo4j 知识图谱
```

## 性能估计

- **PDF 文本提取**：平均 5-10 秒/100 页
- **LLM 实体抽取**：平均 30-60 秒/PDF（取决于内容长度和 LLM 响应时间）
- **数据导入**：平均 2-5 秒/PDF

**建议：**
- 大规模导入时，可使用 `--pdf` 参数分批处理
- 监控 Neo4j 服务器内存使用情况

## 扩展开发

### 添加新的 PDF 分类

在 `batch_extract_and_import.py` 的 `_get_category_from_filename()` 方法中添加映射：

```python
mapping = {
    "新分类名": "新分类显示名",
    ...
}
```

### 自定义实体抽取逻辑

编辑 `extract_entities.py` 中的 `extract_knowledge_points()` 方法的 `system_prompt`。

### 支持新的 LLM 后端

在 `EntityExtractor` 类中添加新的 `elif self.llm_type == "..."` 分支。

## 许可证

本项目遵循原项目许可证。

## 更新日志

### 2026-02-16
- ✓ 创建 batch_extract_and_import.py 批量处理脚本
- ✓ 支持 PDF 自动分类
- ✓ 实现知识图谱格式转换
- ✓ 集成自动导入功能
- ✓ 完成常识上册 PDF 处理示例
- ✓ 创建 import_entities.py 单独导入工具

## 后续改进

- [ ] 支持 OCR 识别扫描版 PDF
- [ ] 增加进度条显示
- [ ] 支持增量更新
- [ ] 数据验证和冲突处理
- [ ] Web UI 可视化导入进度
- [ ] 支持其他文档格式（Word、PPT 等）
- [ ] 性能优化（并行处理）

---

**问题反馈：** 如遇到问题，请检查日志输出或参考常见问题部分。
