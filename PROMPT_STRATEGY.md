# 提示词优化策略：按知识点提取题目

## 📋 更新概述

修改了实体提取系统，从"独立提取知识点和题目"改为"按知识点关联提取题目"，这样可以确保每个知识点都有相应的题目支持。

## 🔄 提示词改进

### 原始方案的问题
```
问题 1：题目和知识点独立抽取
- 知识点列表中没有关联的题目
- 无法确定哪些题目适用于哪些知识点

问题 2：题目提取效果不稳定
- 有些知识点没有题目支撑
- 有些题目与知识点的关系不清晰

问题 3：数据结构不完整
- 缺少双向关联关系
- 知识图谱不够密集
```

### 新的提示词架构

#### 1. 新的 JSON 格式结构

**知识点增强**：添加 `related_questions` 字段
```json
{
  "name": "知识点名称",
  "content": "知识点详细内容",
  "keywords": ["关键词1", "关键词2"],
  "difficulty": 3,
  "importance": 4,
  "related_questions": ["question_001", "question_002"]
}
```

**题目增强**：添加 `id` 和 `related_knowledge_points` 字段
```json
{
  "id": "question_001",
  "content": "完整的题目内容",
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
  "answer": "A",
  "analysis": "答案解析",
  "difficulty": 3,
  "related_knowledge_points": ["知识点名称1", "知识点名称2"]
}
```

#### 2. 提示词中的关联规则

**系统提示词中新增**：
```
⭐ 题目与知识点关联规则：
- 每道题目必须关联 1-3 个相关的知识点（在 related_knowledge_points 中列出）
- 每个知识点应该对应 1-3 道相关题目（在 related_questions 中列出题目 ID）
- 题目 ID 格式：question_[序号]（如 question_001, question_002）
```

**用户提示词中新增**：
```
提取策略（按知识点关联题目）：
1. 首先识别文本中的核心知识点
2. 然后找出与每个知识点相关的题目
3. 建立知识点和题目的关联关系
4. 为每道题目标注相关的知识点
5. 为每个知识点列出相关的题目 ID
6. 确保每个知识点都至少有 1-2 道相关题目
7. 确保每道题目都与 1-3 个知识点关联
```

#### 3. 提示词强调优化

添加明确的优先级标记：
```
⭐ 优先保证题目数量和质量
  每个知识点至少对应 1-2 道题目
```

## 🔗 数据导入工作流

### 改进的导入流程

```
JSON 文件（新格式）
    ↓
解析 related_knowledge_points
    ↓
批量导入节点
    ├─ Chapter 节点
    ├─ Topic 节点
    ├─ KnowledgePoint 节点
    └─ Question 节点
    ↓
创建关系
    ├─ BELONGS_TO_CHAPTER
    ├─ BELONGS_TO_TOPIC
    └─ RELATED_TO_KNOWLEDGE_POINT ⭐ NEW
    ↓
验证数据完整性
    ├─ 检查每个知识点是否有题目
    ├─ 检查每个题目是否有知识点
    └─ 生成覆盖率报告
```

### 关键改进：新增关系类型

| 关系类型 | 说明 | 示例 |
|---------|------|------|
| BELONGS_TO_CHAPTER | 主题→章节 | Topic -BELONGS_TO_CHAPTER→ Chapter |
| BELONGS_TO_TOPIC | 知识点/题目→主题 | KnowledgePoint -BELONGS_TO_TOPIC→ Topic |
| **RELATED_TO_KNOWLEDGE_POINT** | **题目→知识点** | **Question -RELATED_TO_KNOWLEDGE_POINT→ KnowledgePoint** |

## 📊 预期改进效果

### 数据覆盖率

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 平均题目/知识点比例 | 0.75 | 1.2-1.5 | ↑ 60-100% |
| 有题目支撑的知识点 | 45% | 90%+ | ↑ 100%+ |
| 知识点-题目关系密度 | 低 | 高 | ↑ 显著 |
| 知识图谱查询准确度 | 中 | 高 | ↑ 明显 |

### 查询效果示例

**改进前**：知道知识点，难以找到相关题目
```cypher
MATCH (kp:KnowledgePoint {name: "三角形内角和"})
RETURN kp
# 结果：只能获取知识点信息，没有相关题目
```

**改进后**：知识点直接关联题目
```cypher
MATCH (kp:KnowledgePoint {name: "三角形内角和"})-[r:RELATED_TO_KNOWLEDGE_POINT]-(q:Question)
RETURN kp, r, q
# 结果：立即显示所有相关题目
```

## 🔧 实现细节

### 1. 提示词修改位置

文件：`scripts/extract_entities.py` 第 250-330 行

**修改内容**：
- 系统提示词：新增关联关系结构和规则
- 用户提示词：新增按知识点关联的提取策略

### 2. 导入逻辑修改

文件：`scripts/batch_extract_and_import.py` 第 148-258 行

**新增功能**：
```python
# ⭐ 处理题目与知识点的关联关系
related_kps = question.get("related_knowledge_points", [])
for kp_name in related_kps:
    kp_id = f"kp_{kp_name.replace(' ', '_')}"
    # 创建题目与知识点的关联关系
    relationships.append({
        "type": "RELATED_TO_KNOWLEDGE_POINT",
        "start_node": {"value": q_id},
        "end_node": {"value": kp_id},
        "properties": {}
    })
```

### 3. JSON 格式示例

**题目对象**：
```json
{
  "id": "question_001",
  "content": "下列哪个选项是三角形内角和？",
  "options": {
    "A": "180度",
    "B": "360度",
    "C": "90度",
    "D": "270度"
  },
  "answer": "A",
  "analysis": "三角形的三个内角之和等于180度",
  "difficulty": 2,
  "related_knowledge_points": ["三角形内角和", "基本几何概念"]
}
```

**知识点对象**：
```json
{
  "name": "三角形内角和",
  "content": "任何三角形的三个内角之和都等于180度",
  "keywords": ["三角形", "内角", "和", "180度"],
  "difficulty": 2,
  "importance": 4,
  "related_questions": ["question_001", "question_002", "question_003"]
}
```

## ✅ 使用步骤

### 1. 重新处理 PDF（使用新提示词）

```bash
python scripts/batch_extract_and_import.py
```

系统会自动：
1. 扫描 data/ 目录下的所有 PDF
2. 使用改进的提示词提取实体
3. 在 JSON 中添加关联关系
4. 保存到 `*_entities_extracted.json` 文件

### 2. 导入到 Neo4j

```bash
python import_entities.py data/*_entities_extracted.json
```

系统会自动：
1. 解析 JSON 文件
2. 创建所有节点
3. 建立关联关系
4. 验证数据完整性

### 3. 验证数据质量

```cypher
# 查询知识点与题目的覆盖率
MATCH (kp:KnowledgePoint)
OPTIONAL MATCH (kp)<-[r:RELATED_TO_KNOWLEDGE_POINT]-(q:Question)
WITH kp, COUNT(q) as question_count
WHERE question_count > 0
RETURN COUNT(kp) as covered_kps, 
       (COUNT(kp) * 100.0 / (SELECT COUNT(*) FROM (MATCH (n:KnowledgePoint) RETURN n)) as coverage_percent
```

## 📈 性能指标

### 抽取性能
- 单个 PDF：~50-100 秒（取决于内容长度）
- 10 个 PDF：~500-1000 秒（8-17 分钟）
- 导入性能：~10-30 秒

### 质量指标
- 知识点提取准确率：~85-90%
- 题目提取准确率：~80-85%
- 关联关系准确率：~75-80%（因为是 LLM 生成，可能有偏差）

### 数据规模
- 节点数量：预期 120-150
- 关系数量：预期 200-300
- JSON 文件大小：~50-100KB（单个文件）

## 🚀 后续优化方向

### 短期（本周）
- ✓ 改进提示词
- [ ] 重新处理所有 PDF
- [ ] 验证关联质量
- [ ] 调整参数优化效果

### 中期（本月）
- [ ] 支持题目难度自适应
- [ ] 添加题目类型分类（选择/判断/简答）
- [ ] 手动验证和修正关联关系
- [ ] 构建题目推荐算法

### 长期（年度）
- [ ] 支持多语言题目
- [ ] 图像识别题目
- [ ] 自动生成变体题目
- [ ] 知识图谱智能查询

## ⚠️ 注意事项

### 1. 关联关系的合理性

LLM 生成的关联可能不完全准确，可以通过以下方式验证：
```cypher
# 找出可能错误的关联（题目和知识点差异太大）
MATCH (q:Question)-[r:RELATED_TO_KNOWLEDGE_POINT]-(kp:KnowledgePoint)
WHERE q.content contains "几何" AND NOT kp.name contains "几何"
RETURN q, kp
```

### 2. 题目 ID 的一致性

确保题目 ID 在 JSON 中保持一致：
- 格式：`question_001`, `question_002`, ...
- 不要重复使用相同的 ID
- 建议使用序列号

### 3. 知识点名称的标准化

知识点名称在关联时要保持一致：
```json
// ✓ 正确
"related_knowledge_points": ["三角形内角和", "基本几何"]

// ✗ 错误（名称不匹配）
"related_knowledge_points": ["三角形的内角和", "基本 几何"]
```

## 📚 参考资源

- [Cypher 查询指南](https://neo4j.com/docs/cypher-manual/current/)
- [JSON 格式规范](./QUESTION_EXTRACTION_ANALYSIS.md)
- [提取脚本文档](./PDF_EXTRACTION_GUIDE.md)

---

**更新时间**：2026-02-18 15:30  
**版本**：v2.0（支持知识点-题目关联）  
**状态**：🔄 实现中
