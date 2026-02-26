# 快速导入指南 - 完成数据导入

## 🎯 当前状态

✓ 已完成：
- 提示词优化
- 长文本分块处理
- JSON 文件生成（153 道题目）

⏳ 待完成：
- 解决编码问题
- 完成数据导入到 Neo4j

## 🚀 立即执行

### 方案 1：清空后重新导入（推荐）

```powershell
# 在 PowerShell 中执行

# 1. 连接 Neo4j 并清空所有数据
python -c "
import sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', '5211314zhg'))
with driver.session() as session:
    session.run('MATCH (n) DETACH DELETE n')
    print('✓ 数据库已清空')
driver.close()
"

# 2. 导入新数据
python -c "
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import os
from scripts.import_data import KnowledgeGraphImporter

importer = KnowledgeGraphImporter('bolt://localhost:7687', 'neo4j', '5211314zhg')

for file in sorted(os.listdir('data')):
    if file.endswith('_entities_extracted.json'):
        filepath = os.path.join('data', file)
        print(f'导入: {file}')
        try:
            importer.import_from_json(filepath)
        except Exception as e:
            print(f'  错误: {str(e)[:100]}')

importer.close()
print('✓ 导入完成')
"
```

### 方案 2：如果编码仍有问题

```powershell
# 修改 import_data.py，移除 Unicode 符号

# 或使用批处理 Python 脚本
python -c "
import sys
import os
import json

# 设置 UTF-8 输出
sys.stdout.reconfigure(encoding='utf-8')

from scripts.import_data import KnowledgeGraphImporter

importer = KnowledgeGraphImporter('bolt://localhost:7687', 'neo4j', '5211314zhg')

files_to_import = [
    'data/常识上册_entities_extracted.json',
    'data/常识下册_entities_extracted.json',
    'data/判断推理上册(1)_entities_extracted.json',
    'data/判断推理下册(1)_entities_extracted.json',
    'data/数量上册(1)_entities_extracted.json',
    'data/数量下册(1)_entities_extracted.json',
    'data/言语上册(1)_entities_extracted.json',
    'data/言语下册(1)_entities_extracted.json',
    'data/资料分析上册(1)_entities_extracted.json',
    'data/资料分析下册(1)_entities_extracted.json'
]

for filepath in files_to_import:
    if os.path.exists(filepath):
        print(f'导入: {os.path.basename(filepath)}')
        try:
            importer.import_from_json(filepath)
            print(f'  OK')
        except Exception as e:
            print(f'  ERROR: {str(e)[:100]}')
    else:
        print(f'找不到: {filepath}')

importer.close()
"
```

## ✅ 验证导入结果

```bash
# 检查导入是否成功
python -c "
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', '5211314zhg'))

with driver.session() as session:
    q_count = session.run('MATCH (n:Question) RETURN COUNT(n) as c').single()['c']
    kp_count = session.run('MATCH (n:KnowledgePoint) RETURN COUNT(n) as c').single()['c']
    rel_count = session.run('MATCH ()-[r:RELATED_TO_KNOWLEDGE_POINT]->() RETURN COUNT(r) as c').single()['c']
    
    print(f'题目: {q_count}')
    print(f'知识点: {kp_count}')
    print(f'关联: {rel_count}')
    
    if q_count > 150:
        print('SUCCESS: 数据导入成功！')
    else:
        print('WARNING: 题目数量较少，可能导入不完整')

driver.close()
"
```

## 📊 预期结果

如果导入成功，应该看到：

```
题目: 150-160 个（vs 原来的 91 个）
知识点: 90-100 个（vs 原来的 57 个）
关联: 80-100 条（vs 原来的 58 条）

提升比例：
- 题目数：+68-76%
- 知识点：+58-75%
- 覆盖率：显著提升
```

## 🔍 快速验证查询

```cypher
# 1. 查看知识点与题目的关联情况
MATCH (kp:KnowledgePoint)
OPTIONAL MATCH (kp)<-[r:RELATED_TO_KNOWLEDGE_POINT]-(q:Question)
WITH kp, COUNT(q) as q_count
RETURN 
  COUNT(kp) as total_kps,
  SUM(CASE WHEN q_count > 0 THEN 1 ELSE 0 END) as covered_kps,
  AVG(q_count) as avg_questions_per_kp

# 2. 找出题目最多的知识点
MATCH (kp:KnowledgePoint)<-[r:RELATED_TO_KNOWLEDGE_POINT]-(q:Question)
RETURN kp.name, COUNT(q) as question_count
ORDER BY question_count DESC
LIMIT 10

# 3. 找出仍然没有题目的知识点
MATCH (kp:KnowledgePoint)
WHERE NOT (kp)<-[:RELATED_TO_KNOWLEDGE_POINT]-()
RETURN COUNT(kp) as uncovered_count
```

## ❌ 故障排除

### 问题 1：导入时出现 Unicode 错误

**原因**：PowerShell 默认编码是 GBK

**解决**：
```powershell
# 在脚本开头添加
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

### 问题 2：数据导入后题目仍然只有 90 个

**原因**：可能导入了旧的 JSON 文件

**解决**：
```bash
# 1. 清空数据库
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', '5211314zhg'))
with driver.session() as session:
    session.run('MATCH (n) DETACH DELETE n')
driver.close()
"

# 2. 检查 JSON 文件中的题目数量
python -c "
import json
for file in ['data/常识下册_entities_extracted.json', 'data/判断推理下册(1)_entities_extracted.json']:
    with open(file, encoding='utf-8') as f:
        data = json.load(f)
        q = sum(len(t.get('questions', [])) for t in data.get('topics', []))
        print(f'{file}: {q} 道题目')
"

# 3. 重新导入
python import_entities.py data/*_entities_extracted.json
```

### 问题 3：关联关系仍然较少

**原因**：某些 PDF 的题目仍没有关联知识点

**解决**：
```bash
# 检查哪些题目没有关联
python -c "
import json
for file in sorted([f for f in os.listdir('data') if f.endswith('_entities_extracted.json')]):
    with open(f'data/{file}', encoding='utf-8') as f:
        data = json.load(f)
        for topic in data.get('topics', []):
            for q in topic.get('questions', []):
                if not q.get('related_knowledge_points'):
                    print(f'{file}: 题目 \"{q.get(\"content\", \"\"[:20])}\" 无关联知识点')
"
```

## 📝 完整工作流

```
1. 修改提示词 ✓
   ↓
2. 分块处理长 PDF ✓
   ↓
3. 生成改进的 JSON ✓
   ↓
4. 清空旧数据 ← 现在执行
   ↓
5. 导入新数据 ← 现在执行
   ↓
6. 验证导入结果
   ↓
7. 优化和调整（如需要）
```

## 🎯 建议行动

### 立即执行（5 分钟）
```bash
# 复制下面的命令直接在 PowerShell 运行
python -c "
import sys; sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', '5211314zhg'))
with driver.session() as session:
    session.run('MATCH (n) DETACH DELETE n')
    print('[OK] 数据库已清空')
driver.close()
"
```

### 然后执行导入
```bash
python import_entities.py data/*_entities_extracted.json
```

### 最后验证
```bash
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', '5211314zhg'))
with driver.session() as session:
    q = session.run('MATCH (n:Question) RETURN COUNT(n) as c').single()['c']
    print(f'[RESULT] 数据库中有 {q} 道题目')
driver.close()
"
```

---

**关键目标**：将题目数从 91 增加到 150+  
**预期时间**：5 分钟  
**下一步**：执行上面的三个命令块
