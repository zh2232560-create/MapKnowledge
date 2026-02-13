# 知识图谱快速使用指南

## 📁 项目结构

```
mapKnowledge/
├── data/                    # 数据文件
│   └── sample_data.json    # 示例数据
├── scripts/                 # 脚本工具
│   ├── init_schema.py      # Schema 初始化
│   ├── import_data.py      # 数据导入工具
│   └── query_examples.py   # 查询示例
├── neo4j_examples/          # Neo4j 连接示例
│   ├── neo4j_test.py       # 连接测试
│   └── change_password.py  # 密码修改
├── mapknowledge/            # Python 虚拟环境
├── schema.md                # Schema 设计文档
├── start_neo4j.bat         # Neo4j 启动脚本
└── README_Neo4j_Setup.md   # Neo4j 安装指南
```

## 🚀 快速开始

### 1. 启动 Neo4j 数据库

**方式一：使用启动脚本（推荐）**
```powershell
# 双击运行或命令行执行
D:\vsprogram\mapKnowledge\start_neo4j.bat
```

**方式二：手动启动**
```powershell
Set-Location "D:\vsprogram\mapKnowledge\neo4j-community-5.26.1\bin"
$env:JAVA_HOME = "C:\Program Files\Microsoft\jdk-21.0.9.10-hotspot"
.\neo4j.bat console
```

### 2. 激活 Python 虚拟环境

```powershell
Set-Location "D:\vsprogram\mapKnowledge"
. .\mapknowledge\Scripts\Activate.ps1
```

### 3. 初始化知识图谱 Schema

```powershell
python .\scripts\init_schema.py
```

这会创建：
- ✓ 6 个节点类型的唯一约束（Person, Concept, Organization, Location, Event, Document）
- ✓ 6 个属性索引（name, title, date 等）
- ✓ 3 个全文搜索索引

### 4. 导入示例数据

```powershell
# 导入默认示例数据
python .\scripts\import_data.py .\data\sample_data.json

# 或导入自定义 JSON 文件
python .\scripts\import_data.py <你的JSON文件路径>
```

示例数据包含：
- 3 个人物（张三、李四、王五）
- 4 个概念（知识图谱、Neo4j、Python、机器学习）
- 2 个组织（TechCorp、数据科学研究院）
- 2 个地点（北京、上海）
- 1 个事件（技术峰会）
- 2 个文档

### 5. 运行查询示例

```powershell
python .\scripts\query_examples.py
```

## 📊 数据格式说明

### JSON 数据格式

```json
{
  "nodes": {
    "Person": [
      {
        "id": "p001",
        "name": "张三",
        "age": 28,
        "occupation": "软件工程师"
      }
    ],
    "Concept": [...]
  },
  "relationships": {
    "KNOWS": [
      {
        "from_id": "p001",
        "from_label": "Person",
        "to_id": "p002",
        "to_label": "Person",
        "properties": {"since": "2020"}
      }
    ]
  }
}
```

## 🔍 常用查询示例

### 在 Neo4j Browser 中（http://localhost:7474）

```cypher
// 1. 查看所有节点类型和数量
MATCH (n)
RETURN labels(n)[0] as label, count(*) as count
ORDER BY count DESC

// 2. 查找某人的社交网络
MATCH path = (p:Person {name: '张三'})-[:KNOWS*1..3]-(friend)
RETURN path

// 3. 查找两人之间的最短路径
MATCH path = shortestPath(
  (p1:Person {name: '张三'})-[*]-(p2:Person {name: '王五'})
)
RETURN path

// 4. 查找相关概念
MATCH (c:Concept {name: '知识图谱'})-[:RELATED_TO]-(related)
RETURN c, related

// 5. 查找某公司的所有员工
MATCH (p:Person)-[r:WORKS_FOR]->(o:Organization {name: 'TechCorp'})
RETURN p.name, r.position, r.start_date
ORDER BY r.start_date
```

### 在 Python 中

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "5211314zhg")
)

with driver.session() as session:
    result = session.run("""
        MATCH (p:Person)-[:WORKS_FOR]->(o:Organization)
        RETURN p.name as person, o.name as company
    """)
    
    for record in result:
        print(f"{record['person']} 工作于 {record['company']}")

driver.close()
```

## 🛠️ 常用操作

### 清空数据库（保留 Schema）

```cypher
MATCH (n) DETACH DELETE n
```

### 删除所有约束和索引

```cypher
// 查看所有约束
SHOW CONSTRAINTS

// 删除特定约束
DROP CONSTRAINT constraint_name

// 查看所有索引
SHOW INDEXES

// 删除特定索引
DROP INDEX index_name
```

### 添加自定义数据

创建一个 JSON 文件（如 `my_data.json`），按照示例格式填充数据，然后：

```powershell
python .\scripts\import_data.py .\data\my_data.json
```

## 📝 自定义 Schema

编辑 `scripts/init_schema.py` 添加新的节点类型或关系：

```python
# 添加新的约束
"CREATE CONSTRAINT project_id IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE",

# 添加新的索引
"CREATE INDEX project_name IF NOT EXISTS FOR (p:Project) ON (p.name)",
```

## 🎯 进阶应用

### 1. 批量导入大数据集

使用 `LOAD CSV` 或 Neo4j 的 `neo4j-admin import` 工具。

### 2. 图算法应用

安装 Neo4j Graph Data Science 库进行：
- 社区检测
- 路径查找
- 中心性分析
- 相似度计算

### 3. 可视化

- Neo4j Browser（内置）
- Neo4j Bloom（企业版）
- Gephi、Cytoscape 等第三方工具

## 🔧 故障排查

### Neo4j 连接失败

```powershell
# 检查端口是否开启
Test-NetConnection -ComputerName localhost -Port 7687

# 如果返回 False，重启 Neo4j
.\start_neo4j.bat
```

### 密码错误

```powershell
python .\neo4j_examples\change_password.py
```

### 虚拟环境问题

```powershell
# 重新激活
. .\mapknowledge\Scripts\Activate.ps1

# 检查 Python 版本
python --version

# 检查已安装的包
pip list
```

## 📚 参考资源

- [Neo4j 官方文档](https://neo4j.com/docs/)
- [Cypher 查询语言](https://neo4j.com/docs/cypher-manual/current/)
- [Neo4j Python 驱动](https://neo4j.com/docs/python-manual/current/)
- [知识图谱最佳实践](https://neo4j.com/developer/knowledge-graph/)

## ⚡ 快捷命令

```powershell
# 完整流程（首次使用）
.\start_neo4j.bat
. .\mapknowledge\Scripts\Activate.ps1
python .\scripts\init_schema.py
python .\scripts\import_data.py .\data\sample_data.json
python .\scripts\query_examples.py

# 日常使用
.\start_neo4j.bat
. .\mapknowledge\Scripts\Activate.ps1
# 开始你的工作...
```

---

**提示**：每次重启电脑后需要重新运行 `start_neo4j.bat` 启动数据库。
