# ⚡ 快速修复：setup_aliyun.bat 无效

## 🔧 问题原因

`setup_aliyun.bat` 双击没有效果通常是因为：
1. 脚本执行出错后立即关闭窗口
2. Python 路径未配置
3. 权限问题

## ✅ 快速解决方案

### 推荐方法：手动配置（5 分钟）

#### Windows 用户

1. **打开命令提示符**
   ```
   按 Windows + R
   输入：cmd
   按 Enter
   ```

2. **设置 API Key**
   ```batch
   set DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6
   ```

3. **安装依赖**
   ```batch
   pip install openai pdfplumber
   ```

4. **验证**
   ```batch
   python scripts\aliyun_dashscope_example.py
   ```

#### Linux/Mac 用户

```bash
# 1. 设置环境变量
export DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6

# 2. 安装依赖
pip install openai pdfplumber

# 3. 验证
python3 scripts/aliyun_dashscope_example.py
```

---

## 🎯 立即开始使用

设置完上述步骤后，直接运行：

```bash
# 提取 PDF 实体
python scripts/extract_entities.py data/常识上册.pdf

# 或使用示例
python scripts/aliyun_dashscope_example.py
```

---

## 📚 更多帮助

- 详细步骤：[MANUAL_SETUP.md](MANUAL_SETUP.md)
- 完整指南：[START_HERE.md](START_HERE.md)  
- API 文档：[ALIYUN_DASHSCOPE_GUIDE.md](ALIYUN_DASHSCOPE_GUIDE.md)

---

**就这么简单！** 🚀
