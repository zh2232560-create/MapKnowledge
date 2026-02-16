# 🚀 快速开始 - 阿里百炼集成

## 📋 概览

本项目已成功集成**阿里百炼平台**的大模型服务，替换原本的豆包模型。

### 核心信息
- **API Key**: `sk-69b4138e853648a79659aa01cc859dd6`
- **Base URL**: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- **Model**: `claude-3-5-sonnet`
- **Region**: 华北2（北京）

---

## ⚡ 30秒快速启动

### Windows 用户

```batch
REM 1. 双击运行配置脚本
setup_aliyun.bat

REM 2. 测试（可选）
python scripts/aliyun_dashscope_example.py

REM 3. 使用
python scripts/extract_entities.py data/常识上册.pdf
```

### Linux/Mac 用户

```bash
# 1. 运行配置脚本
chmod +x setup_aliyun.sh
./setup_aliyun.sh

# 2. 测试（可选）
python3 scripts/aliyun_dashscope_example.py

# 3. 使用
python3 scripts/extract_entities.py data/常识上册.pdf
```

---

## 📖 详细步骤

### 步骤 1: 环境配置

#### 方法 A：自动配置（推荐）✅

**Windows:**
```
双击 setup_aliyun.bat
```
脚本会自动：
- ✅ 设置环境变量
- ✅ 安装依赖
- ✅ 验证 API 连接

**Linux/Mac:**
```bash
chmod +x setup_aliyun.sh && ./setup_aliyun.sh
```

#### 方法 B：手动配置

**Windows (Command Prompt):**
```batch
set DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6
setx DASHSCOPE_CLAUDE_API_KEY sk-69b4138e853648a79659aa01cc859dd6
```

**Windows (PowerShell):**
```powershell
$env:DASHSCOPE_CLAUDE_API_KEY = "sk-69b4138e853648a79659aa01cc859dd6"
```

**Linux/Mac:**
```bash
export DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6
echo 'export DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6' >> ~/.bashrc
source ~/.bashrc
```

### 步骤 2: 安装依赖

```bash
pip install openai pdfplumber
```

### 步骤 3: 验证配置

```bash
# 测试 API 连接
python scripts/aliyun_dashscope_example.py
```

预期输出：
```
[✓] API 连接成功！
    响应内容: Hi
```

### 步骤 4: 使用项目

```bash
# 提取 PDF 中的知识点
python scripts/extract_entities.py data/常识上册.pdf

# 指定输出文件
python scripts/extract_entities.py data/常识上册.pdf -o output.json

# 显式指定 LLM 类型
python scripts/extract_entities.py data/常识上册.pdf --llm dashscope_claude
```

---

## 💻 常见命令

### 提取实体

```bash
# 基础用法
python scripts/extract_entities.py <pdf_path>

# 自定义参数
python scripts/extract_entities.py <pdf_path> \
    --llm dashscope_claude \
    --output result.json \
    --pages 1-50

# 参数说明
# --llm          : LLM 类型 (dashscope_claude|openai|doubao|ollama|dashscope|auto)
# --output, -o   : 输出文件路径
# --pages        : 页码范围 (例: 1-10)
# --preview      : 仅预览文档结构
```

### 运行示例

```bash
# 运行所有示例
python scripts/aliyun_dashscope_example.py

# 示例包括:
# 1. 实体抽取
# 2. 文档分类
# 3. 文本摘要
# 4. 知识问答
# 5. 批量处理
```

---

## 🔄 LLM 类型选择

### 优先级（自动检测）

使用 `--llm auto`（默认）时，按以下优先级自动选择：

1. **DASHSCOPE_CLAUDE_API_KEY** → `dashscope_claude` ⭐ **推荐**
2. ARK_API_KEY → `doubao`
3. OPENAI_API_KEY → `openai`
4. DASHSCOPE_API_KEY → `dashscope`
5. 本地 Ollama → `ollama`

### 手动选择

```bash
# 使用阿里百炼
python scripts/extract_entities.py data.pdf --llm dashscope_claude

# 使用 OpenAI
python scripts/extract_entities.py data.pdf --llm openai

# 使用豆包
python scripts/extract_entities.py data.pdf --llm doubao

# 使用本地 Ollama
python scripts/extract_entities.py data.pdf --llm ollama
```

---

## 📚 文档导航

| 文档 | 用途 | 位置 |
|------|------|------|
| **QUICK_START_ALIYUN.md** | 快速参考 | 项目根目录 |
| **ALIYUN_DASHSCOPE_GUIDE.md** | 完整指南 | 项目根目录 |
| **INTEGRATION_SUMMARY.md** | 集成总结 | 项目根目录 |
| **CHANGELOG.md** | 更新日志 | 项目根目录 |

---

## 🎯 功能演示

### 功能 1: 知识点抽取

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-69b4138e853648a79659aa01cc859dd6"
)

response = client.chat.completions.create(
    model="claude-3-5-sonnet",
    messages=[
        {"role": "system", "content": "你是知识抽取专家"},
        {"role": "user", "content": "从这段文本中抽取主要概念..."}
    ]
)

print(response.choices[0].message.content)
```

### 功能 2: 文档分类

```bash
python -c "
from openai import OpenAI
import os

client = OpenAI(
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
    api_key=os.getenv('DASHSCOPE_CLAUDE_API_KEY')
)

response = client.chat.completions.create(
    model='claude-3-5-sonnet',
    messages=[
        {'role': 'system', 'content': '你是文档分类专家'},
        {'role': 'user', 'content': '将这段文本分类...'}
    ]
)

print(response.choices[0].message.content)
"
```

### 功能 3: 批量处理

见 `scripts/aliyun_dashscope_example.py` 中的 `batch_processing_example()` 函数

---

## 🔧 故障排除

### 问题 1: API Key 无效

**症状**: `API 连接失败` 错误

**解决**:
```bash
# 检查环境变量
echo %DASHSCOPE_CLAUDE_API_KEY%  # Windows
echo $DASHSCOPE_CLAUDE_API_KEY    # Linux/Mac

# 确保 API Key 正确
set DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6
```

### 问题 2: 环境变量未生效

**症状**: 运行脚本显示 `未设置 API Key`

**解决**:
```
新打开命令行窗口/终端，环境变量修改需要重新加载
```

### 问题 3: openai 模块未安装

**症状**: `ModuleNotFoundError: No module named 'openai'`

**解决**:
```bash
pip install openai
pip install --upgrade openai  # 如果已安装但版本过旧
```

### 问题 4: 网络连接失败

**症状**: 超时或连接错误

**解决**:
```bash
# 测试网络连接
ping dashscope.aliyuncs.com

# 使用代理（如需要）
# 在脚本中设置代理...
```

---

## ✅ 检查清单

在使用前，确保完成以下步骤：

- [ ] API Key 已设置为环境变量
- [ ] openai 包已安装 (`pip install openai`)
- [ ] pdfplumber 已安装 (`pip install pdfplumber`)
- [ ] API 连接已验证 (`python scripts/aliyun_dashscope_example.py`)
- [ ] 有有效的 PDF 文件可以处理

---

## 🎓 学习资源

1. **官方文档**
   - [阿里百炼官方网站](https://dashscope.aliyun.com)
   - [API 文档](https://help.aliyun.com/zh/dashscope)
   - [模型信息](https://help.aliyun.com/zh/dashscope/latest/model-square)

2. **项目文档**
   - 详细指南: [ALIYUN_DASHSCOPE_GUIDE.md](ALIYUN_DASHSCOPE_GUIDE.md)
   - 快速参考: [QUICK_START_ALIYUN.md](QUICK_START_ALIYUN.md)
   - 更新日志: [CHANGELOG.md](CHANGELOG.md)

3. **示例代码**
   - [scripts/aliyun_dashscope_example.py](scripts/aliyun_dashscope_example.py)

---

## 🤝 支持

遇到问题？

1. 查看 [ALIYUN_DASHSCOPE_GUIDE.md](ALIYUN_DASHSCOPE_GUIDE.md) 中的常见问题
2. 检查 [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md) 中的技术细节
3. 运行示例脚本进行测试

---

## 📊 项目信息

- **集成状态**: ✅ 完成
- **文档完整性**: ✅ 100%
- **向后兼容性**: ✅ 是
- **最后更新**: 2026-02-16
- **GitHub 仓库**: [MapKnowledge](https://github.com/zh2232560-create/MapKnowledge)

---

**祝你使用愉快！** 🎉

如有任何问题或建议，欢迎反馈。
