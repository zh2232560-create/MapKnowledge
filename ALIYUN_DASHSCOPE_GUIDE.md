# 阿里百炼平台大模型集成指南

## 概览

本项目已集成阿里百炼平台的大模型服务，用于替换原有的豆包模型。阿里百炼平台提供了 OpenAI 兼容的 API 接口，支持多种强大的大模型。

## API 配置信息

### 基本信息
- **API Key**: `sk-69b4138e853648a79659aa01cc859dd6`
- **Base URL**: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- **Model**: `claude-3-5-sonnet`
- **所属地域**: 华北2（北京）

### 支持的模型列表
- `claude-3-5-sonnet` - Claude 3.5 Sonnet (推荐)
- `claude-3-5-haiku` - Claude 3.5 Haiku
- `claude-3-opus` - Claude 3 Opus
- 其他阿里百炼支持的模型

## 环境变量配置

### Windows 系统

在命令行中设置环境变量：

```batch
set DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6
```

或者使用 PowerShell：

```powershell
$env:DASHSCOPE_CLAUDE_API_KEY = "sk-69b4138e853648a79659aa01cc859dd6"
```

### Linux/Mac 系统

```bash
export DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6
```

添加到 `~/.bashrc` 或 `~/.zshrc` 进行持久化：

```bash
echo 'export DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6' >> ~/.bashrc
source ~/.bashrc
```

## 使用方法

### 1. 安装依赖

```bash
pip install openai
```

### 2. 在 Python 中使用

#### 方式一：自动检测（推荐）

```bash
# 设置环境变量后，自动使用阿里百炼
python scripts/extract_entities.py data/常识上册.pdf
```

#### 方式二：显式指定

```bash
# 明确指定使用 dashscope_claude
python scripts/extract_entities.py data/常识上册.pdf --llm dashscope_claude
```

#### 方式三：直接编程

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
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ]
)

print(response.choices[0].message.content)
```

## 功能示例

### 示例脚本位置

查看 `scripts/aliyun_dashscope_example.py` 文件，包含以下功能示例：

1. **实体抽取** - 从文本中抽取关键实体和关系
2. **文档分类** - 自动分类文档内容
3. **文本摘要** - 生成文本内容摘要
4. **知识问答** - 问答系统实现
5. **批量处理** - 批量处理多个文本

### 运行示例

```bash
# 设置环境变量
set DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6

# 运行示例脚本
python scripts/aliyun_dashscope_example.py
```

## 在知识图谱项目中使用

### 提取 PDF 实体

```bash
# 自动使用阿里百炼（已设置 DASHSCOPE_CLAUDE_API_KEY 环境变量）
python scripts/extract_entities.py data/常识上册.pdf

# 或显式指定
python scripts/extract_entities.py data/常识上册.pdf --llm dashscope_claude --output output.json
```

### 支持的 LLM 选项

```bash
python scripts/extract_entities.py <pdf_path> --llm {openai|dashscope|dashscope_claude|doubao|ollama|auto}
```

| 选项 | 说明 | 环境变量 |
|------|------|---------|
| `dashscope_claude` | 阿里百炼大模型 | DASHSCOPE_CLAUDE_API_KEY |
| `dashscope` | 阿里通义千问 | DASHSCOPE_API_KEY |
| `openai` | OpenAI GPT | OPENAI_API_KEY |
| `doubao` | 字节豆包 | ARK_API_KEY |
| `ollama` | 本地 Ollama | 无 |
| `auto` | 自动检测 | 按优先级检测 |

### 自动检测优先级

当使用 `--llm auto` 时，按以下优先级自动选择：

1. `DASHSCOPE_CLAUDE_API_KEY` → 阿里百炼大模型 ✓ **新增**
2. `ARK_API_KEY` → 字节豆包
3. `OPENAI_API_KEY` → OpenAI GPT
4. `DASHSCOPE_API_KEY` → 阿里通义千问
5. 本地 Ollama

## API 使用注意事项

### 请求限制
- 确保 API Key 有效且有足够的配额
- 根据实际需求选择合适的模型
- 合理设置 temperature 参数（0-2，默认 0.3）

### 错误处理

```python
try:
    response = client.chat.completions.create(...)
except Exception as e:
    print(f"API 调用失败: {e}")
```

### 成本考虑
- 不同模型的定价不同
- Claude 3.5 Sonnet 在性能和成本之间取得平衡
- 建议监控 API 使用量

## 常见问题

### Q: 如何验证 API Key 是否有效？

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-69b4138e853648a79659aa01cc859dd6"
)

try:
    response = client.chat.completions.create(
        model="claude-3-5-sonnet",
        messages=[{"role": "user", "content": "测试"}],
        max_tokens=10
    )
    print("API Key 有效")
except Exception as e:
    print(f"API Key 无效或请求失败: {e}")
```

### Q: 如何切换回豆包模型？

如果已设置 `ARK_API_KEY` 环境变量，使用 `--llm auto` 会自动选择阿里百炼。
要强制使用豆包，使用：

```bash
python scripts/extract_entities.py <pdf_path> --llm doubao
```

### Q: 支持哪些输入语言？

Claude 3.5 Sonnet 支持多种语言，包括：
- 中文（简体/繁体）✓
- 英文 ✓
- 日文 ✓
- 韩文 ✓
- 及其他 100+ 种语言

### Q: 如何提高处理速度？

1. 减少 token 消耗
2. 使用更小的模型（Haiku）
3. 启用批量处理

## 更新日志

### 2026-02-16

✅ 添加阿里百炼平台大模型支持
✅ 新增 `dashscope_claude` LLM 类型
✅ 优先级调整：阿里百炼优先于豆包
✅ 创建示例脚本 `aliyun_dashscope_example.py`
✅ 完整的集成文档

## 技术支持

如遇到问题，请：
1. 检查环境变量是否正确设置
2. 确认 API Key 有效期和配额
3. 查看 [阿里百炼官方文档](https://help.aliyun.com/zh/dashscope/)
4. 检查网络连接状态

## 相关文档

- [阿里百炼 API 文档](https://dashscope.aliyun.com/api-overview)
- [OpenAI 兼容 API 说明](https://help.aliyun.com/zh/dashscope/developer-reference/compatible-with-openai)
- [模型列表](https://help.aliyun.com/zh/dashscope/latest/model-square)
