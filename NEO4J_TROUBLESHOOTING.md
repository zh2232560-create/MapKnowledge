# 导入失败原因分析与解决方案

## 问题诊断

### 导入失败错误信息

```
[ERROR] 导入失败: Couldn't connect to localhost:7687
Failed to establish connection to ResolvedIPv6Address(('::1', 7687, 0, 0))
(reason [WinError 10061] 由于目标计算机积极拒绝，无法连接。)
Failed to establish connection to ResolvedIPv4Address(('127.0.0.1', 7687))
```

### 根本原因

❌ **Neo4j 数据库服务未启动**

诊断结果：
```
[1] Neo4j 进程状态：✗ 未运行
[2] 7687 端口状态：✗ 未开放
[3] 数据库连接：✗ 连接失败
```

## 解决方案

### 快速修复（推荐方式）

#### 步骤 1：启动 Neo4j

**方式 A：直接启动（推荐）**
```bash
# 直接运行启动脚本
start_neo4j.bat

# 或在命令行中运行
D:\vsprogram\mapKnowledge\neo4j-community-5.26.1\bin\neo4j.bat console
```

**方式 B：使用 bat 文件启动**
1. 打开文件管理器
2. 导航到 `D:\vsprogram\mapKnowledge`
3. 双击 `start_neo4j.bat`
4. 等待窗口显示 "Started"（约 10-15 秒）

#### 步骤 2：验证启动状态

```bash
python check_neo4j_status.py
```

预期输出：
```
✓ Neo4j 进程正在运行
✓ 7687 端口已开放
✓ 数据库连接成功！
✓ Neo4j 已就绪，可以导入数据
```

#### 步骤 3：导入数据

```bash
# 导入已提取的 JSON 文件
python import_entities.py data/*_entities_extracted.json

# 或导入单个文件
python import_entities.py data/常识上册_entities_extracted.json
```

### 详细启动指南

#### 方法 1：命令行启动（最简单）

```bash
# 进入项目目录
cd D:\vsprogram\mapKnowledge

# 启动 Neo4j
start_neo4j.bat

# 在另一个终端窗口运行导入
python import_entities.py data/*_entities_extracted.json
```

#### 方法 2：Neo4j Desktop 启动

1. **打开 Neo4j Desktop**
   - 搜索并启动 Neo4j Desktop 应用

2. **启动数据库**
   - 在 Desktop 中找到默认数据库
   - 点击"Start"按钮
   - 确保状态为 "Running"

3. **验证连接**
   ```bash
   python check_neo4j_status.py
   ```

4. **导入数据**
   ```bash
   python import_entities.py data/*_entities_extracted.json
   ```

#### 方法 3：Windows 服务启动

```bash
# 作为 Windows 服务安装
cd D:\vsprogram\mapKnowledge\neo4j-community-5.26.1\bin
neo4j.bat install-service

# 启动服务
net start Neo4j

# 或使用 services.msc 图形界面启动
```

### 配置检查

如果仍然无法连接，检查以下配置：

#### 检查 neo4j.conf

文件位置：`neo4j-community-5.26.1/conf/neo4j.conf`

必要配置（第 87-91 行）：

```properties
# Bolt connector
server.bolt.enabled=true
#server.bolt.tls_level=DISABLED
server.bolt.listen_address=:7687
server.bolt.advertised_address=localhost:7687
```

**如果这些行被注释（#），需要取消注释**

#### 检查端口占用

```bash
# Windows PowerShell 检查 7687 端口
netstat -ano | findstr :7687

# 如果显示 LISTENING，说明 Neo4j 正在运行
# 如果没有显示，需要启动 Neo4j
```

## 导入工作流程

### 完整流程（从 PDF 到图谱）

```
1. 处理 PDF ---------> 生成 JSON
   python scripts/batch_extract_and_import.py --pdf 常识上册
   
   结果：data/常识上册_entities_extracted.json (11.6 KB)

2. 验证 Neo4j 状态
   python check_neo4j_status.py
   
   结果：✓ 准备就绪

3. 导入到图谱
   python import_entities.py data/常识上册_entities_extracted.json
   
   结果：导入成功
```

### 快速命令集

```bash
# 1. 检查 Neo4j 状态
python check_neo4j_status.py

# 2. 启动 Neo4j（如果未启动）
start_neo4j.bat

# 3. 处理 PDF（如果还未处理）
python scripts/batch_extract_and_import.py --pdf 常识上册

# 4. 导入数据
python import_entities.py data/*_entities_extracted.json

# 5. 验证导入
python check_neo4j_status.py  # 应该显示连接成功
```

## 常见问题

### Q1：启动后仍然无法连接

**原因可能：**
1. Neo4j 启动尚未完成（需要 15-30 秒）
2. 防火墙阻止了 7687 端口
3. 配置文件有误

**解决方案：**
```bash
# 等待更长时间
Start-Sleep -Seconds 30

# 再次检查
python check_neo4j_status.py

# 如果仍失败，检查防火墙
# Windows Defender 防火墙 -> 允许应用通过防火墙 -> 允许 Java
```

### Q2：显示"端口已被占用"

**原因：**
其他程序已占用 7687 端口

**解决方案：**
```bash
# 查看占用端口的进程
netstat -ano | findstr :7687

# 记下 PID，然后终止该进程
taskkill /PID <PID> /F

# 重启 Neo4j
start_neo4j.bat
```

### Q3：Neo4j 进程启动后立即退出

**原因：**
- Java 环境未配置
- 配置文件有语法错误
- 磁盘空间不足

**解决方案：**
```bash
# 检查 Java 安装
java -version

# 查看启动日志
type neo4j-community-5.26.1\logs\debug.log

# 检查配置文件语法
# 使用 neo4j.conf 验证工具
```

### Q4：连接超时

**原因：**
Neo4j 响应缓慢或被防火墙阻止

**解决方案：**
```bash
# 增加连接超时时间
# 在导入脚本中修改：
driver = GraphDatabase.driver(uri, auth=(user, password), max_connection_lifetime=30)

# 检查防火墙设置
# 允许 java.exe 通过防火墙
```

## 监控和验证

### 检查导入状态

```bash
# 运行诊断工具
python check_neo4j_status.py

# 预期输出示例
✓ Neo4j 进程正在运行
✓ 7687 端口已开放
✓ 数据库连接成功！
✓ Neo4j 已就绪，可以导入数据
```

### 查看导入日志

```bash
# 导入时会显示详细日志
python import_entities.py data/常识上册_entities_extracted.json

# 输出示例
从 data\常识上册_entities_extracted.json 导入数据...
✓ 导入 50 个 Chapter 节点
✓ 导入 50 个 KnowledgePoint 节点
✓ 导入 50 个 BELONGS_TO_CHAPTER 关系
```

### 验证数据入库

在 Neo4j Browser 中运行查询：

```cypher
# 查看所有节点数
MATCH (n) RETURN count(n) as node_count

# 查看节点类型分布
MATCH (n) RETURN labels(n) as type, count(n) as count

# 查看所有关系
MATCH ()-[r]->() RETURN type(r) as type, count(r) as count

# 查看具体知识点
MATCH (kp:KnowledgePoint) RETURN kp.name LIMIT 10
```

## 解决方案总结

| 步骤 | 命令 | 预期结果 |
|------|------|--------|
| 1. 检查状态 | `python check_neo4j_status.py` | ✓ 连接失败（正常，因为未启动） |
| 2. 启动数据库 | `start_neo4j.bat` | 窗口显示"Started" |
| 3. 等待启动 | `Start-Sleep -Seconds 15` | 等待就绪 |
| 4. 验证连接 | `python check_neo4j_status.py` | ✓ 连接成功 |
| 5. 导入数据 | `python import_entities.py data/*.json` | ✓ 导入完成 |

## 下一步

导入成功后：

1. **验证数据**
   ```bash
   # 在 Neo4j Browser 中检查数据
   # http://localhost:7474
   ```

2. **构建查询**
   ```bash
   # 创建知识图谱查询接口
   python scripts/query_examples.py
   ```

3. **可视化展示**
   ```bash
   # 使用 Neo4j 内置可视化工具
   # 或集成自定义 UI
   ```

---

**结论：** 导入失败是因为 Neo4j 未启动。按照上述步骤启动后，数据导入将成功。

**更新时间**：2026-02-16  
**状态**：问题原因已明确，解决方案已提供
