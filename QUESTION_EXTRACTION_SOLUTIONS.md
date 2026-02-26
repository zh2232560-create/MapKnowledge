# 题目提取方案分析与对比

## 📊 当前状态

### 题目提取统计
- **总题目数**：183 道
- **平均每个知识点**：0.50 道题目
- **预期目标**：每个知识点 1-2 道题目

### 问题分析

| 分类 | 知识点 | 题目 | 比例 | 状态 |
|------|--------|------|------|------|
| 常识判断 | 21 | 14 | 0.67 | ⚠️ 较少 |
| 判断推理 | 18 | 34 | 1.89 | ✓ 较好 |
| 数量关系 | 10 | 27 | 2.70 | ✓ 很好 |
| 言语理解 | 2 | 8 | 4.00 | ✓ 充足 |
| 资料分析 | 6 | 8 | 1.33 | ✓ 一般 |

**关键问题**：
- 常识判断题目最少（14 道）
- 常识下册只有 3 道题目
- 判断推理下册只有 8 道题目

## 🎯 解决方案对比

### 方案 1：分页提取（每 2 页提取一次）

**概念**：
```
PDF 总页数：100 页
分块方式：每 2 页提取一次
提取次数：50 次
预期题目数：183 × 3 = 549 道
```

**优点**：
- ✓ 题目覆盖更全面
- ✓ 减少 LLM 一次性处理大量内容的难度
- ✓ 可以捕捉更多的题目细节
- ✓ 提高题目提取的准确率

**缺点**：
- ✗ API 调用次数多（增加成本）
- ✗ 处理时间长（50 倍）
- ✗ 重复题目较多（需要去重）
- ✗ 知识点重复提取（需要合并）
- ✗ 题目碎片化风险（跨页题目可能被割断）

**成本估算**：
```
原始：10 个 PDF × 50 秒 = 500 秒 = 8 分钟
分页：100 次提取 × 50 秒 = 5000 秒 = 83 分钟
增加：约 10 倍时间和成本
```

**推荐度**：⚠️ 不太适合（成本太高）

---

### 方案 2：优化提示词 + 增加最小题目数

**概念**：
```
改进点1：提示词中强调"必须提取所有题目"
改进点2：设置最小题目数要求为 5-10 道
改进点3：扩展题目类型识别
改进点4：优化关键词识别
```

**优点**：
- ✓ 成本最低（无额外 API 调用）
- ✓ 效率高（只需重新运行一次）
- ✓ 题目质量好（完整性更高）
- ✓ 关联关系清晰

**缺点**：
- ✗ 改进空间有限（可能只增加 30-50%）
- ✗ 需要反复测试参数
- ✗ 对某些 PDF 可能效果不明显

**成本估算**：
```
原始：8 分钟
改进：8 分钟
增加：0 分钟额外时间
```

**预期效果**：
```
当前：183 道题目
改进后：220-270 道题目（+30-50%）
效果评分：★★★☆☆
```

**推荐度**：✓ 推荐（快速见效）

---

### 方案 3：按页面分块 + 智能去重

**概念**：
```
分块方式：每 5 页提取一次（而非 2 页）
去重策略：题目内容相似度 > 80% 则合并
知识点合并：自动检测重复知识点
```

**优点**：
- ✓ 题目提取更完整
- ✓ 成本相对较低（5 倍而非 50 倍）
- ✓ 自动去重避免重复
- ✓ 平衡覆盖率和成本

**缺点**：
- ✗ 实现复杂（需要开发去重算法）
- ✗ 仍需多次 API 调用
- ✗ 去重可能误删题目
- ✗ 处理时间仍较长

**成本估算**：
```
原始：8 分钟
分块：20 次提取 × 50 秒 = 1000 秒 = 16 分钟
增加：约 2 倍时间和成本
```

**预期效果**：
```
当前：183 道题目
改进后：350-400 道题目（+90-120%）
效果评分：★★★★☆
```

**推荐度**：✓✓ 较推荐（性价比好）

---

### 方案 4：多模型融合提取

**概念**：
```
使用多个 LLM 模型分别提取：
- 模型1（qwen-max）：提取知识点和题目
- 模型2（claude 等）：验证并补充题目
- 合并：去重后合并结果
```

**优点**：
- ✓ 充分利用多个模型的优势
- ✓ 互补性强（某个模型遗漏的能被另一个捕获）
- ✓ 提取质量最高
- ✓ 关联关系准确率高

**缺点**：
- ✗ 成本最高（2-3 倍）
- ✗ 需要支持多个 API 密钥
- ✗ 需要实现复杂的合并逻辑
- ✗ 处理时间最长

**成本估算**：
```
单模型：8 分钟
双模型：16 分钟
增加：约 2 倍时间和成本
```

**预期效果**：
```
当前：183 道题目
改进后：300-350 道题目（+60-90%）
效果评分：★★★★★
```

**推荐度**：⚠️ 可选（成本较高）

---

## 📋 方案选择建议

### 第 1 优先级：方案 2（优化提示词）

**立即执行**（推荐）

```python
# 修改 extract_entities.py 中的提示词
# 第 270-280 行

system_prompt = """
...
⭐ 关键要求（最高优先级）：
1. 必须提取文本中的所有题目，包括：
   - 所有选择题（单选、多选）
   - 所有判断题
   - 所有简答题和论述题
   - 所有案例分析题
   - 所有示例和习题
2. 最小题目数保证：至少 5-10 道题目（如果有的话）
3. 完整性检查：每道题目都必须有题干和答案

⭐ 质量要求：
1. 题干内容完整（不截断）
2. 选项完整（A、B、C、D 都要）
3. 答案明确标注
4. 解析详细说明
"""
```

**执行步骤**：
```bash
# 1. 修改提示词
# 编辑 scripts/extract_entities.py 第 270-280 行

# 2. 重新处理特定 PDF（最需要改进的）
python scripts/batch_extract_and_import.py --pdf "常识下册"
python scripts/batch_extract_and_import.py --pdf "判断推理下册"
python scripts/batch_extract_and_import.py --pdf "言语"
python scripts/batch_extract_and_import.py --pdf "资料分析"

# 3. 重新导入数据
python import_entities.py data/*_entities_extracted.json

# 4. 验证效果
python check_extraction_quality.py
```

**预期时间**：~15 分钟  
**预期效果**：题目数量 +30-50%

---

### 第 2 优先级：方案 3（分块提取）

**如果方案 2 效果不理想则执行**

需要创建新脚本：

```python
# scripts/batch_extract_pagewise.py

def extract_pagewise(pdf_path, pages_per_chunk=5):
    """
    按页面分块提取
    
    Args:
        pdf_path: PDF 文件路径
        pages_per_chunk: 每次提取的页面数
    """
    pdf = PDFExtractor(pdf_path)
    total_pages = pdf.get_total_pages()
    
    all_questions = []
    all_knowledge_points = []
    
    # 分块提取
    for start_page in range(0, total_pages, pages_per_chunk):
        end_page = min(start_page + pages_per_chunk, total_pages)
        
        print(f"提取第 {start_page}-{end_page} 页...")
        
        chunk_text = pdf.extract_text(start_page, end_page)
        entities = entity_extractor.extract_knowledge_points(chunk_text)
        
        all_questions.extend(entities.get("questions", []))
        all_knowledge_points.extend(entities.get("knowledge_points", []))
    
    # 去重和合并
    merged = merge_and_deduplicate(all_questions, all_knowledge_points)
    
    return merged
```

**执行步骤**：
```bash
# 1. 创建分块提取脚本
# 2. 使用分块模式重新处理所有 PDF
python scripts/batch_extract_pagewise.py

# 3. 去重和合并
python scripts/deduplicate_questions.py

# 4. 重新导入数据
```

**预期时间**：~30-40 分钟  
**预期效果**：题目数量 +90-120%

---

### 第 3 优先级：方案 4（多模型融合）

**仅在方案 2 和 3 都不理想时执行**

---

## 🚀 立即实施：方案 2

### 步骤 1：查看当前提示词

```bash
cd D:\vsprogram\mapKnowledge
python -c "
from scripts.extract_entities import EntityExtractor
import inspect

extractor = EntityExtractor()
source = inspect.getsource(extractor.extract_knowledge_points)
print(source[500:1000])  # 打印提示词部分
"
```

### 步骤 2：增强提示词中的题目要求

需要修改 `scripts/extract_entities.py` 中的提示词，特别是这些关键点：

**原始**：
```
8. ⭐ 优先保证题目数量和质量，每个知识点至少对应 1-2 道题目
```

**改进后**：
```
8. ⭐ CRITICAL：必须提取所有题目！
   - 最小数量：至少 5-10 道题目（如果文本中有的话）
   - 题目类型：选择题、判断题、简答题、论述题、案例题等
   - 完整性：每道题都要有题干、选项、答案和解析
   - 不要遗漏：任何出现的题目都要提取，即使不完整也要尽力
```

### 步骤 3：运行改进后的提取

```bash
# 只重新处理题目较少的 PDF
python scripts/batch_extract_and_import.py --pdf "常识下册"
python scripts/batch_extract_and_import.py --pdf "判断推理下册"
python scripts/batch_extract_and_import.py --pdf "言语"
python scripts/batch_extract_and_import.py --pdf "资料分析"
```

### 步骤 4：验证改进效果

```bash
python -c "
import json

# 对比改进前后
old_data = {'常识下册': 3}
new_data = {}

for file in [
    'data/常识下册_entities_extracted.json',
    'data/判断推理下册(1)_entities_extracted.json',
    'data/言语上册(1)_entities_extracted.json',
    'data/资料分析上册(1)_entities_extracted.json'
]:
    with open(file, encoding='utf-8') as f:
        data = json.load(f)
        name = file.split('/')[-1].replace('_entities_extracted.json', '')
        questions = sum(len(t.get('questions', [])) for t in data['topics'])
        new_data[name] = questions
        print(f'{name}: {questions} 道题目')
"
```

## 📈 效果预测

### 最保守估计（仅改进提示词）

```
当前：183 道题目
改进：+30% = 238 道题目
时间：+0 分钟
```

### 乐观估计（改进提示词 + 手动补充）

```
当前：183 道题目
改进：+50% = 275 道题目
时间：+5 分钟（手动检查）
```

### 激进方案（分块提取）

```
当前：183 道题目
改进：+100% = 365 道题目
时间：+25 分钟
```

## 💡 建议行动计划

### 今天（2026-02-18）

1. **立即执行**：方案 2（优化提示词）
   ```bash
   # 修改提示词后重新处理 4 个 PDF
   # 预计 10 分钟完成
   ```

2. **验证效果**
   ```bash
   # 检查新提取的题目数量
   # 对比改进前后的数据
   ```

### 明天（如果需要）

3. **备选方案**：方案 3（分块提取）
   - 如果方案 2 效果不理想再执行
   - 预计 30 分钟完成

### 本周末

4. **数据质量审查**
   - 手动检查提取的题目质量
   - 修正明显的错误
   - 补充遗漏的题目

## 📊 成本-收益分析

| 方案 | 时间 | 成本 | 效果 | 难度 | 推荐 |
|------|------|------|------|------|------|
| 方案 1 | +0 分钟 | 无 | +30-50% | 低 | ⭐⭐⭐⭐⭐ |
| 方案 2 | +5 分钟 | 无 | +50-70% | 低 | ⭐⭐⭐⭐ |
| 方案 3 | +25 分钟 | 中 | +90-120% | 中 | ⭐⭐⭐ |
| 方案 4 | +25 分钟 | 高 | +60-90% | 高 | ⭐⭐ |

**结论**：🎯 **强烈推荐方案 2**（方案 1 的增强版）

---

**文档创建**：2026-02-18  
**优先级**：高  
**下一步**：执行方案 2（修改提示词并重新提取）
