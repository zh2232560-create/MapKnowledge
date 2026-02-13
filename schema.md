# 公考知识图谱 Schema 设计

## 设计理念

本知识图谱采用层次化结构设计，完整覆盖公务员考试的所有科目和知识点。通过"实体-关系-实体"三元组来表示知识的组织结构和内在联系。

## 知识图谱总体架构

```
考公知识图谱/
├── 公共科目
│   ├── 行政职业能力测验（行测）
│   └── 申论
├── 专业科目
│   ├── 公安基础知识
│   ├── 法律专业知识
│   ├── 财务管理
│   └── 计算机
└── 面试环节
    ├── 结构化面试
    └── 无领导小组讨论
```

## 实体类型 (Node Labels)

### 0. Category (类别)
表示考试的顶层分类

**属性:**
- `id`: 唯一标识符 (string, unique)
- `name`: 类别名称 (string, required) - 如"公共科目"、"专业科目"、"面试环节"
- `code`: 类别编码 (string, unique) - 如"GONGGONG", "ZHUANYE", "MIANSHI"
- `description`: 类别描述 (string)
- `order`: 排序序号 (integer)
- `created_at`: 创建时间 (datetime)

### 1. Subject (科目)
表示类别下的具体科目

**属性:**
- `id`: 唯一标识符 (string, unique)
- `name`: 科目名称 (string, required) - 如"行测"、"申论"、"公安基础知识"
- `code`: 科目编码 (string, unique) - 如"XINGCE", "SHENLUN"
- `description`: 科目描述 (string)
- `exam_type`: 考试类型 (string) - "国考"、"省考"、"事业单位"
- `order`: 排序序号 (integer)
- `created_at`: 创建时间 (datetime)

### 2. Module (模块)
表示科目下的二级模块分类

**属性:**
- `id`: 唯一标识符 (string, unique)
- `name`: 模块名称 (string, required) - 如"言语理解与表达"、"数量关系"
- `code`: 模块编码 (string)
- `description`: 模块描述 (string)
- `order`: 排序序号 (integer)
- `created_at`: 创建时间 (datetime)

### 3. Chapter (章节)
表示模块下的三级章节分类

**属性:**
- `id`: 唯一标识符 (string, unique)
- `name`: 章节名称 (string, required) - 如"逻辑填空"、"片段阅读"
- `code`: 章节编码 (string)
- `description`: 章节描述 (string)
- `order`: 排序序号 (integer)
- `created_at`: 创建时间 (datetime)

### 4. Topic (主题/题型)
表示具体的题型或主题分类

**属性:**
- `id`: 唯一标识符 (string, unique)
- `name`: 主题名称 (string, required) - 如"实词辨析"、"成语辨析"
- `code`: 主题编码 (string)
- `description`: 主题描述 (string)
- `difficulty`: 难度等级 1-5 (integer)
- `order`: 排序序号 (integer)
- `created_at`: 创建时间 (datetime)

### 5. KnowledgePoint (知识点)
表示最小粒度的知识单元

**属性:**
- `id`: 唯一标识符 (string, unique)
- `name`: 知识点名称 (string, required)
- `content`: 知识点内容 (text)
- `definition`: 定义说明 (text)
- `examples`: 示例说明 (text)
- `difficulty`: 难度等级 1-5 (integer)
- `importance`: 重要程度 1-5 (integer)
- `frequency`: 考试频率 (integer) - 近5年出现次数
- `keywords`: 关键词标签 (string) - 逗号分隔
- `created_at`: 创建时间 (datetime)
- `updated_at`: 更新时间 (datetime)

### 6. Skill (解题技巧)
表示解题方法和技巧

**属性:**
- `id`: 唯一标识符 (string, unique)
- `name`: 技巧名称 (string, required)
- `description`: 技巧描述 (text)
- `steps`: 应用步骤 (text)
- `examples`: 应用示例 (text)
- `applicable_types`: 适用题型 (string) - 逗号分隔
- `effectiveness`: 有效性评分 1-5 (integer)
- `created_at`: 创建时间 (datetime)

### 7. Question (真题)
表示历年真题

**属性:**
- `id`: 唯一标识符 (string, unique)
- `year`: 考试年份 (integer)
- `exam_type`: 考试类型 (string) - "国考"、"省考"等
- `province`: 省份 (string) - 仅省考适用
- `question_number`: 题号 (integer)
- `content`: 题目内容 (text)
- `options`: 选项内容 (text) - JSON格式
- `answer`: 正确答案 (string)
- `analysis`: 答案解析 (text)
- `difficulty`: 难度等级 1-5 (integer)
- `created_at`: 创建时间 (datetime)

### 8. Resource (学习资源)
表示学习材料和资源

**属性:**
- `id`: 唯一标识符 (string, unique)
- `title`: 资源标题 (string, required)
- `type`: 资源类型 (string) - "视频"、"文档"、"课件"、"习题集"
- `url`: 资源链接 (string)
- `author`: 作者/讲师 (string)
- `duration`: 时长(分钟) (integer) - 仅视频适用
- `quality`: 质量评分 1-5 (integer)
- `view_count`: 浏览次数 (integer)
- `created_at`: 创建时间 (datetime)

### 9. Concept (概念)
表示重要概念和术语

**属性:**
- `id`: 唯一标识符 (string, unique)
- `name`: 概念名称 (string, required)
- `definition`: 概念定义 (text)
- `explanation`: 详细解释 (text)
- `examples`: 示例 (text)
- `related_terms`: 相关术语 (string) - 逗号分隔
- `created_at`: 创建时间 (datetime)

### 10. TestPoint (考点)
表示高频考点和重点

**属性:**
- `id`: 唯一标识符 (string, unique)
- `name`: 考点名称 (string, required)
- `description`: 考点描述 (text)
- `frequency`: 出现频率 (integer)
- `importance`: 重要程度 1-5 (integer)
- `trend`: 趋势分析 (string) - "上升"、"稳定"、"下降"
- `created_at`: 创建时间 (datetime)

## 关系类型 (Relationship Types)

### 0. HAS_SUBJECT
**说明:** 类别包含科目
**起点:** Category
**终点:** Subject
**属性:** 无

### 1. HAS_MODULE
**说明:** 科目包含模块
**起点:** Subject
**终点:** Module
**属性:** 无

### 2. HAS_CHAPTER
**说明:** 模块包含章节
**起点:** Module
**终点:** Chapter
**属性:** 无

### 3. HAS_TOPIC
**说明:** 章节包含主题/题型
**起点:** Chapter
**终点:** Topic
**属性:** 无

### 4. HAS_KNOWLEDGE
**说明:** 主题包含知识点
**起点:** Topic
**终点:** KnowledgePoint
**属性:** 无

### 5. PREREQUISITE
**说明:** 前置依赖关系(知识点A是知识点B的前置知识)
**起点:** KnowledgePoint
**终点:** KnowledgePoint
**属性:**
- `strength`: 依赖强度 1-5 (integer)

### 6. RELATED_TO
**说明:** 知识点关联关系
**起点:** KnowledgePoint
**终点:** KnowledgePoint
**属性:**
- `relation_type`: 关系类型 (string) - "相似"、"对比"、"补充"

### 7. CONFUSABLE_WITH
**说明:** 易混淆关系
**起点:** KnowledgePoint/Concept
**终点:** KnowledgePoint/Concept
**属性:**
- `confusion_reason`: 混淆原因 (string)
- `distinction`: 区分要点 (string)

### 8. APPLIES_TO
**说明:** 技巧应用于知识点/题型
**起点:** Skill
**终点:** KnowledgePoint/Topic
**属性:**
- `effectiveness`: 有效性 1-5 (integer)

### 9. TESTS
**说明:** 真题考察知识点
**起点:** Question
**终点:** KnowledgePoint
**属性:**
- `weight`: 考察权重 (float) - 0-1之间

### 10. BELONGS_TO_TOPIC
**说明:** 真题属于某个主题/题型
**起点:** Question
**终点:** Topic
**属性:** 无

### 11. HAS_RESOURCE
**说明:** 知识点/主题关联学习资源
**起点:** KnowledgePoint/Topic
**终点:** Resource
**属性:**
- `recommended`: 是否推荐 (boolean)

### 12. DEFINES
**说明:** 概念定义关系
**起点:** Concept
**终点:** KnowledgePoint
**属性:** 无

### 13. IS_TEST_POINT
**说明:** 知识点是考点
**起点:** KnowledgePoint
**终点:** TestPoint
**属性:** 无

### 14. USES_SKILL
**说明:** 解答真题使用的技巧
**起点:** Question
**终点:** Skill
**属性:** 无

## 索引设计

### 唯一性约束 (Unique Constraints)
```cypher
CREATE CONSTRAINT category_id IF NOT EXISTS FOR (c:Category) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT subject_id IF NOT EXISTS FOR (s:Subject) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT module_id IF NOT EXISTS FOR (m:Module) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT chapter_id IF NOT EXISTS FOR (c:Chapter) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT topic_id IF NOT EXISTS FOR (t:Topic) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT knowledge_id IF NOT EXISTS FOR (k:KnowledgePoint) REQUIRE k.id IS UNIQUE;
CREATE CONSTRAINT skill_id IF NOT EXISTS FOR (s:Skill) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT question_id IF NOT EXISTS FOR (q:Question) REQUIRE q.id IS UNIQUE;
CREATE CONSTRAINT resource_id IF NOT EXISTS FOR (r:Resource) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT testpoint_id IF NOT EXISTS FOR (t:TestPoint) REQUIRE t.id IS UNIQUE;
```

### 属性索引 (Property Indexes)
```cypher
CREATE INDEX category_code IF NOT EXISTS FOR (c:Category) ON (c.code);
CREATE INDEX category_name IF NOT EXISTS FOR (c:Category) ON (c.name);
CREATE INDEX subject_code IF NOT EXISTS FOR (s:Subject) ON (s.code);
CREATE INDEX subject_name IF NOT EXISTS FOR (s:Subject) ON (s.name);
CREATE INDEX module_name IF NOT EXISTS FOR (m:Module) ON (m.name);
CREATE INDEX chapter_name IF NOT EXISTS FOR (c:Chapter) ON (c.name);
CREATE INDEX topic_name IF NOT EXISTS FOR (t:Topic) ON (t.name);
CREATE INDEX knowledge_name IF NOT EXISTS FOR (k:KnowledgePoint) ON (k.name);
CREATE INDEX knowledge_difficulty IF NOT EXISTS FOR (k:KnowledgePoint) ON (k.difficulty);
CREATE INDEX knowledge_importance IF NOT EXISTS FOR (k:KnowledgePoint) ON (k.importance);
CREATE INDEX skill_name IF NOT EXISTS FOR (s:Skill) ON (s.name);
CREATE INDEX question_year IF NOT EXISTS FOR (q:Question) ON (q.year);
CREATE INDEX question_exam_type IF NOT EXISTS FOR (q:Question) ON (q.exam_type);
CREATE INDEX resource_type IF NOT EXISTS FOR (r:Resource) ON (r.type);
CREATE INDEX concept_name IF NOT EXISTS FOR (c:Concept) ON (c.name);
```

### 全文索引 (Fulltext Indexes)
```cypher
CREATE FULLTEXT INDEX knowledge_content IF NOT EXISTS
FOR (k:KnowledgePoint) ON EACH [k.name, k.content, k.definition];

CREATE FULLTEXT INDEX question_content IF NOT EXISTS
FOR (q:Question) ON EACH [q.content, q.analysis];

CREATE FULLTEXT INDEX resource_content IF NOT EXISTS
FOR (r:Resource) ON EACH [r.title];

CREATE FULLTEXT INDEX concept_content IF NOT EXISTS
FOR (c:Concept) ON EACH [c.name, c.definition, c.explanation];
```

## 数据示例

### 层次结构示例：行测 > 言语理解 > 逻辑填空 > 实词辨析

```cypher
// 创建科目
CREATE (s:Subject {
  id: 'SUB001',
  name: '行测',
  code: 'XINGCE',
  description: '行政职业能力测验',
  exam_type: '国考',
  created_at: datetime()
})

// 创建模块
CREATE (m:Module {
  id: 'MOD001',
  name: '言语理解与表达',
  code: 'YUYAN',
  description: '考查语言文字理解和表达能力',
  order: 1,
  created_at: datetime()
})

// 创建章节
CREATE (c:Chapter {
  id: 'CHP001',
  name: '逻辑填空',
  code: 'LUOJI_TIANKONG',
  description: '根据语境填入恰当的词语',
  order: 1,
  created_at: datetime()
})

// 创建主题
CREATE (t:Topic {
  id: 'TOP001',
  name: '实词辨析',
  code: 'SHICI_BIANXI',
  description: '辨析实词的细微差别',
  difficulty: 3,
  order: 1,
  created_at: datetime()
})

// 创建知识点
CREATE (k:KnowledgePoint {
  id: 'KP001',
  name: '词义侧重分析',
  content: '通过分析词语侧重点的不同来选择合适的词语',
  definition: '同义词虽然意思相近，但往往在词义侧重上有所不同',
  difficulty: 3,
  importance: 4,
  frequency: 15,
  keywords: '词义,侧重,辨析',
  created_at: datetime(),
  updated_at: datetime()
})

// 建立关系
CREATE (s)-[:HAS_MODULE]->(m)
CREATE (m)-[:HAS_CHAPTER]->(c)
CREATE (c)-[:HAS_TOPIC]->(t)
CREATE (t)-[:HAS_KNOWLEDGE]->(k)
```

## 常用查询模式

### 1. 查询某个科目的完整知识树
```cypher
MATCH path = (s:Subject {name: '行测'})-[:HAS_MODULE*1..5]->(n)
RETURN path
```

### 2. 查询某个知识点的所有前置知识
```cypher
MATCH (k:KnowledgePoint {name: '词义侧重分析'})<-[:PREREQUISITE*]-(prereq)
RETURN prereq.name, prereq.difficulty
ORDER BY prereq.difficulty
```

### 3. 查询某个主题的所有真题
```cypher
MATCH (t:Topic {name: '实词辨析'})<-[:BELONGS_TO_TOPIC]-(q:Question)
RETURN q.year, q.content, q.difficulty
ORDER BY q.year DESC
```

### 4. 查询高频考点
```cypher
MATCH (k:KnowledgePoint)-[:IS_TEST_POINT]->(tp:TestPoint)
WHERE tp.frequency > 10
RETURN k.name, tp.frequency, tp.trend
ORDER BY tp.frequency DESC
```

### 5. 查询某个知识点的易混淆概念
```cypher
MATCH (k:KnowledgePoint {name: '词义侧重分析'})-[r:CONFUSABLE_WITH]-(confused)
RETURN confused.name, r.confusion_reason, r.distinction
```

### 6. 推荐学习路径
```cypher
MATCH path = (start:KnowledgePoint)-[:PREREQUISITE*]->(end:KnowledgePoint {name: '目标知识点'})
RETURN path
ORDER BY length(path)
LIMIT 1
```

### 7. 查询适用某个技巧的所有题型
```cypher
MATCH (s:Skill {name: '排除法'})-[:APPLIES_TO]->(target)
RETURN labels(target)[0] as type, target.name
```

### 8. 查询某年某类考试的所有真题及知识点分布
```cypher
MATCH (q:Question {year: 2023, exam_type: '国考'})-[:TESTS]->(k:KnowledgePoint)
RETURN k.name, count(q) as question_count
ORDER BY question_count DESC
```
