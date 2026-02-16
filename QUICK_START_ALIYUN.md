# 阿里百炼大模型快速参考

## 🔑 API 密钥信息

```
API Key: sk-69b4138e853648a79659aa01cc859dd6
Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
Model: claude-3-5-sonnet
Region: 华北2（北京）
```

## ⚙️ 环境变量配置

### Windows (命令提示符)
```batch
set DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6
```

### Windows (PowerShell)
```powershell
$env:DASHSCOPE_CLAUDE_API_KEY = "sk-69b4138e853648a79659aa01cc859dd6"
```

### Linux/Mac
```bash
export DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6
```

## 🚀 快速开始

### 1. 自动配置（推荐）

**Windows:**
```
双击运行 setup_aliyun.bat
```

**Linux/Mac:**
```bash
chmod +x setup_aliyun.sh
./setup_aliyun.sh
```

### 2. 验证安装

```bash
pip install openai
python -m scripts.aliyun_dashscope_example
```

### 3. 使用提取脚本

```bash
python scripts/extract_entities.py data/常识上册.pdf --llm dashscope_claude
```

## 📝 Python 代码示例

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-69b4138e853648a79659aa01cc859dd6"
)

response = client.chat.completions.create(
    model="claude-3-5-sonnet",
    messages=[
        {"role": "system", "content": "你是一个中文助手"},
        {"role": "user", "content": "请介绍一下你自己"}
    ],
    temperature=0.3
)

print(response.choices[0].message.content)
```

## 🔄 LLM 类型对比

| 类型 | 环境变量 | 描述 | 优先级 |
|------|--------|------|-------|
| `dashscope_claude` | DASHSCOPE_CLAUDE_API_KEY | 阿里百炼 Claude | 1️⃣ **最高** |
| `doubao` | ARK_API_KEY | 字节豆包 | 2️⃣ |
| `openai` | OPENAI_API_KEY | OpenAI | 3️⃣ |
| `dashscope` | DASHSCOPE_API_KEY | 阿里通义千问 | 4️⃣ |
| `ollama` | - | 本地模型 | 5️⃣ |
| `auto` | - | 自动选择 | - |

## 📚 主要文件

| 文件 | 说明 |
|------|------|
| `ALIYUN_DASHSCOPE_GUIDE.md` | 完整集成指南 |
| `setup_aliyun.bat` | Windows 自动配置脚本 |
| `setup_aliyun.sh` | Linux/Mac 自动配置脚本 |
| `scripts/aliyun_dashscope_example.py` | 功能示例脚本 |
| `scripts/extract_entities.py` | 实体抽取脚本（已更新） |

## ✨ 支持的功能

- ✅ 实体抽取
- ✅ 文档分类
- ✅ 文本摘要
- ✅ 知识问答
- ✅ 关键词提取
- ✅ 批量处理
- ✅ 知识图谱构建

## 🛠️ 命令速查

```bash
# 提取 PDF 实体（自动使用阿里百炼）
python scripts/extract_entities.py data/常识上册.pdf

# 显式指定阿里百炼
python scripts/extract_entities.py data/常识上册.pdf --llm dashscope_claude

# 指定输出文件
python scripts/extract_entities.py data/常识上册.pdf -o output.json

# 指定页码范围
python scripts/extract_entities.py data/常识上册.pdf --pages 1-10

# 仅预览 PDF 结构
python scripts/extract_entities.py data/常识上册.pdf --preview

# 运行示例脚本
python scripts/aliyun_dashscope_example.py
```

## 🔗 相关链接

- [阿里百炼官方网站](https://dashscope.aliyun.com)
- [API 文档](https://help.aliyun.com/zh/dashscope)
- [OpenAI 兼容 API](https://help.aliyun.com/zh/dashscope/developer-reference/compatible-with-openai)
- [模型列表](https://help.aliyun.com/zh/dashscope/latest/model-square)

## ❓ 常见问题

**Q: 如何测试 API 是否有效？**
```bash
python scripts/aliyun_dashscope_example.py
```

**Q: 环境变量设置后仍然无法使用？**
```
需要重新打开命令窗口/终端才能加载新的环境变量
```

**Q: 如何切换到其他模型？**
```bash
python scripts/extract_entities.py data/常识上册.pdf --llm openai
python scripts/extract_entities.py data/常识上册.pdf --llm ollama
```

**Q: 支持哪些语言？**
```
Claude 3.5 Sonnet 支持 100+ 种语言，包括中文、英文、日文等
```

---

**最后更新**: 2026-02-16  
**状态**: ✅ 已集成，可直接使用
