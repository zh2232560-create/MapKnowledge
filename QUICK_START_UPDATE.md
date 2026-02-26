# 快速更新指南

## ✨ 改进摘要

已修改提示词和导入逻辑，现在系统能够：
- ✓ 识别每个知识点相关的题目
- ✓ 标注每道题目的相关知识点
- ✓ 在知识图谱中建立双向关联

## 🚀 立即开始

### 步骤 1：重新提取所有 PDF（应用新提示词）

```powershell
cd D:\vsprogram\mapKnowledge
python scripts/batch_extract_and_import.py
```

**预期输出**：
```
[1] 正在处理: 常识上册.pdf
  分类: 常识判断
[2] 正在提取实体（使用 Qwen-Max 模型）...
  [OK] 成功提取实体
  [OK] 已保存到: data/常识上册_entities_extracted.json
```

**完成时间**：约 8-17 分钟（处理 10 个 PDF）

### 步骤 2：验证 JSON 中的关联字段

```bash
# 查看一个 JSON 文件，确认新增字段
python -c "
import json
with open('data/常识上册_entities_extracted.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    for topic in data['topics'][:1]:
        for kp in topic['knowledge_points'][:1]:
            print('知识点:', kp['name'])
            print('关联题目:', kp.get('related_questions', []))
        for q in topic['questions'][:1]:
            print('题目:', q.get('content', '')[:30] + '...')
            print('关联知识点:', q.get('related_knowledge_points', []))
"
```

**预期输出**：
```
知识点: 三角形内角和
关联题目: ['question_001', 'question_002']
题目: 下列哪个选项是三角形...
关联知识点: ['三角形内角和', '基本几何']
```

### 步骤 3：导入到 Neo4j（可选）

如果需要更新知识图谱，清空后重新导入：

```powershell
# 方法 1：使用自动导入脚本
python scripts/batch_extract_and_import.py

# 方法 2：手动导入（不清空现有数据，只添加新数据）
python import_entities.py data/*_entities_extracted.json
```

## 📊 效果对比

### 改进前（原始提示词）

```
常识上册 PDF：
  知识点: 14 个
  题目: 3 个
  比例: 0.21
  
  问题：知识点多但题目少，且没有关联
```

### 改进后（新提示词）

```
常识上册 PDF（预期）：
  知识点: 14 个
  题目: 10-15 个 ↑
  比例: 0.7-1.1
  关联关系: 每个知识点有 1-2 个题目 ⭐
  
  改进：题目多且有明确的知识点关联
```

## 🔍 验证关联关系

### 方法 1：查看 JSON 文件

```bash
python -c "
import json

# 统计关联关系
topics_data = []
for file in ['data/常识上册_entities_extracted.json']:
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for topic in data['topics']:
            kp_count = len(topic.get('knowledge_points', []))
            q_count = len(topic.get('questions', []))
            
            # 统计有关联的知识点
            kps_with_relations = sum(1 for kp in topic.get('knowledge_points', [])
                                    if kp.get('related_questions', []))
            q_with_relations = sum(1 for q in topic.get('questions', [])
                                  if q.get('related_knowledge_points', []))
            
            print(f'{topic[\"name\"]}:')
            print(f'  知识点: {kp_count} (有关联: {kps_with_relations})')
            print(f'  题目: {q_count} (有关联: {q_with_relations})')
            print()
"
```

### 方法 2：Neo4j Cypher 查询

```cypher
# 查看知识点和相关题目
MATCH (kp:KnowledgePoint)<-[r:RELATED_TO_KNOWLEDGE_POINT]-(q:Question)
RETURN 
  kp.name as 知识点,
  COUNT(q) as 相关题目数,
  COLLECT(q.content)[0..2] as 题目示例
GROUP BY kp.name
ORDER BY COUNT(q) DESC
LIMIT 10
```

## ⚙️ 配置调整

如果提取效果不理想，可以调整以下参数：

### 1. 最小题目数要求

文件：`scripts/extract_entities.py` 第 270 行

```python
# 改之前
"至少提取 3-5 道题目"

# 改为要求更多
"至少提取 5-10 道题目"
```

### 2. 知识点-题目比例

文件：`scripts/extract_entities.py` 第 260 行

```python
# 改之前
"确保每个知识点都至少有 1-2 道相关题目"

# 改为要求更高
"确保每个知识点都至少有 2-3 道相关题目"
```

### 3. LLM 模型选择

文件：`scripts/batch_extract_and_import.py` 第 112 行

```python
# 当前使用 qwen-max（更快、更便宜）
entity_extractor = EntityExtractor(llm_type="dashscope_claude")

# 可选的其他模型:
# "dashscope_qwen"    - 更快的处理
# "doubao"            - 字节跳动模型
# "ollama"            - 本地模型（需要本地部署）
```

## 📈 性能监控

### 关键指标

| 指标 | 目标值 | 检查命令 |
|------|--------|---------|
| 平均题目/知识点比例 | > 0.8 | `python check_extraction_quality.py` |
| 知识点覆盖率 | > 80% | `MATCH (kp:KnowledgePoint) WHERE NOT (kp)<-[:RELATED_TO_KNOWLEDGE_POINT]-() RETURN COUNT(kp)` |
| 题目关联覆盖率 | > 80% | `MATCH (q:Question) WHERE NOT (q)-[:RELATED_TO_KNOWLEDGE_POINT]->() RETURN COUNT(q)` |
| 平均关联数 | > 1.5 | Neo4j 查询统计 |

### 生成质量检查报告

```bash
python -c "
import json
import os

total_kps = 0
total_questions = 0
covered_kps = 0
related_questions = 0

for file in os.listdir('data'):
    if file.endswith('_entities_extracted.json'):
        with open(f'data/{file}', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for topic in data['topics']:
                for kp in topic.get('knowledge_points', []):
                    total_kps += 1
                    if kp.get('related_questions', []):
                        covered_kps += 1
                
                for q in topic.get('questions', []):
                    total_questions += 1
                    if q.get('related_knowledge_points', []):
                        related_questions += 1

print(f'总知识点数: {total_kps}')
print(f'有题目支撑的知识点: {covered_kps} ({100*covered_kps/max(total_kps,1):.1f}%)')
print(f'总题目数: {total_questions}')
print(f'有知识点关联的题目: {related_questions} ({100*related_questions/max(total_questions,1):.1f}%)')
print(f'知识点-题目比例: {total_questions/max(total_kps,1):.2f}')
"
```

## 🐛 故障排除

### 问题 1：提取的题目仍然较少

**原因**：LLM 可能仍然优先提取知识点

**解决方案**：
1. 增加提示词中的优先级标记数量
2. 调整最小题目数要求
3. 尝试不同的 LLM 模型

### 问题 2：关联关系不准确

**原因**：LLM 可能错误地关联知识点和题目

**解决方案**：
1. 手动检查 JSON 文件中的关联
2. 删除错误的关联并重新导入
3. 添加更具体的提示词示例

### 问题 3：导入失败

**原因**：可能是 Neo4j 未启动或知识点 ID 不一致

**解决方案**：
```bash
# 检查 Neo4j 状态
python check_neo4j_status.py

# 检查 JSON 中是否有重复的知识点名称
python -c "
import json
names = {}
with open('data/常识上册_entities_extracted.json') as f:
    data = json.load(f)
    for topic in data['topics']:
        for kp in topic['knowledge_points']:
            name = kp['name']
            names[name] = names.get(name, 0) + 1
for name, count in names.items():
    if count > 1:
        print(f'重复知识点: {name} (出现 {count} 次)')
"
```

## 📝 后续优化

### 第一阶段（本周）
- [ ] 执行 `batch_extract_and_import.py`
- [ ] 验证 JSON 中的关联字段
- [ ] 检查提取质量指标
- [ ] 根据效果调整参数

### 第二阶段（下周）
- [ ] 手动验证关联关系的准确性
- [ ] 修正明显的错误
- [ ] 优化提示词措辞
- [ ] 增加题目数量

### 第三阶段（本月）
- [ ] 构建题目查询接口
- [ ] 开发题目推荐算法
- [ ] 创建知识点复习模式
- [ ] 添加难度自适应

## 💡 最佳实践

### 提示词优化技巧

1. **使用具体的标记符号**
   - ✓ 使用 `⭐` 标记关键要求
   - ✓ 使用 `[IMPORTANT]` 强调优先级
   - ✗ 避免过于复杂的描述

2. **提供具体示例**
   - 在提示词中展示期望的输出格式
   - 给出样例知识点-题目关联

3. **分层级说明**
   - 第一层：最重要的要求
   - 第二层：次要要求
   - 第三层：可选要求

### 数据质量检查清单

- [ ] 所有知识点都有 name 和 content
- [ ] 所有题目都有 content 和 answer
- [ ] 题目 ID 格式正确（`question_XXX`）
- [ ] 知识点名称在 JSON 中保持一致
- [ ] 关联关系不为空

---

**文档创建时间**：2026-02-18 15:30  
**版本**：1.0  
**下一步**：执行 `python scripts/batch_extract_and_import.py`
