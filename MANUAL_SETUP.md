# 手动配置指南

如果 `setup_aliyun.bat` 脚本运行有问题，可以按照以下步骤手动配置：

## 🪟 Windows 手动配置

### 方式 1: 命令提示符（推荐）

1. **打开命令提示符**
   - Windows + R
   - 输入 `cmd`
   - 按 Enter

2. **设置环境变量**（临时，仅当前会话有效）
   ```batch
   set DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6
   ```

3. **验证设置**
   ```batch
   echo %DASHSCOPE_CLAUDE_API_KEY%
   ```
   应该输出：`sk-69b4138e853648a79659aa01cc859dd6`

4. **安装依赖**
   ```batch
   pip install openai
   pip install pdfplumber
   ```

5. **测试 API**
   ```batch
   python scripts\aliyun_dashscope_example.py
   ```

### 方式 2: PowerShell

1. **打开 PowerShell**
   - Windows + X
   - 选择 "Windows PowerShell"

2. **设置环境变量**（临时，仅当前会话有效）
   ```powershell
   $env:DASHSCOPE_CLAUDE_API_KEY = "sk-69b4138e853648a79659aa01cc859dd6"
   ```

3. **验证设置**
   ```powershell
   $env:DASHSCOPE_CLAUDE_API_KEY
   ```

4. **后续步骤同上**

### 方式 3: 永久设置环境变量（系统级别）

1. **打开系统环境变量设置**
   - Windows + X
   - 选择"系统"
   - 点击"高级系统设置"
   - 点击"环境变量"

2. **添加新变量**
   - 点击"新建"（用户变量）
   - 变量名：`DASHSCOPE_CLAUDE_API_KEY`
   - 变量值：`sk-69b4138e853648a79659aa01cc859dd6`
   - 点击"确定"

3. **重启 VS Code 或命令行工具使其生效**

---

## 🐧 Linux/Mac 手动配置

### 方式 1: 临时设置（仅当前会话）

```bash
export DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6

# 验证
echo $DASHSCOPE_CLAUDE_API_KEY
```

### 方式 2: 永久设置

编辑 shell 配置文件：

**Bash 用户（~/.bashrc）：**
```bash
echo 'export DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6' >> ~/.bashrc
source ~/.bashrc
```

**Zsh 用户（~/.zshrc）：**
```bash
echo 'export DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6' >> ~/.zshrc
source ~/.zshrc
```

**Fish 用户（~/.config/fish/config.fish）：**
```fish
set -Ux DASHSCOPE_CLAUDE_API_KEY sk-69b4138e853648a79659aa01cc859dd6
```

---

## 📦 安装依赖

```bash
# Python 3.7+ 必需
pip install openai pdfplumber

# 或分别安装
pip install openai
pip install pdfplumber
```

---

## ✅ 验证配置

### 方法 1: 查看环境变量

```bash
# Windows (cmd)
echo %DASHSCOPE_CLAUDE_API_KEY%

# Windows (PowerShell)
$env:DASHSCOPE_CLAUDE_API_KEY

# Linux/Mac
echo $DASHSCOPE_CLAUDE_API_KEY
```

### 方法 2: 运行 Python 脚本

```bash
python scripts/aliyun_dashscope_example.py
```

预期输出应包含 `[✓] API 连接成功` 或类似信息。

### 方法 3: 简单测试

```python
import os
print(os.getenv('DASHSCOPE_CLAUDE_API_KEY'))
```

---

## 🚀 开始使用

设置完环境变量后，就可以使用项目了：

```bash
# 提取 PDF 实体
python scripts/extract_entities.py data/常识上册.pdf

# 运行示例
python scripts/aliyun_dashscope_example.py

# 查看帮助
python scripts/extract_entities.py --help
```

---

## 🔍 排查问题

| 问题 | 解决方案 |
|------|--------|
| `ModuleNotFoundError: No module named 'openai'` | 运行 `pip install openai` |
| `ModuleNotFoundError: No module named 'pdfplumber'` | 运行 `pip install pdfplumber` |
| `DASHSCOPE_CLAUDE_API_KEY 未定义` | 检查环境变量是否正确设置 |
| `API 连接失败` | 检查网络连接和 API Key 是否正确 |
| 命令行中文显示乱码 | 改用 UTF-8 编码或查看原始输出 |

---

## 💡 提示

- 环境变量修改后，需要重新打开命令行或 IDE 才能生效
- API Key 是敏感信息，不要提交到版本控制系统
- 建议使用 `.env` 文件或环境变量管理 API Key
- 每个操作系统的设置方式略有不同，请根据您的系统选择

---

**需要帮助？** 查看 [START_HERE.md](START_HERE.md) 或 [ALIYUN_DASHSCOPE_GUIDE.md](ALIYUN_DASHSCOPE_GUIDE.md)
