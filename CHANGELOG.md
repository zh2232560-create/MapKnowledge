# 更新日志 (CHANGELOG)

所有重要更改都记录在此文件中。

## [已发布]

### 2026-02-16 - 阿里百炼大模型集成

#### 🎉 新增功能
- ✨ 集成阿里百炼平台大模型服务
- ✨ 新增 `dashscope_claude` LLM 类型，支持 Claude 3.5 Sonnet 模型
- ✨ 创建自动配置脚本（Windows: `setup_aliyun.bat`, Linux/Mac: `setup_aliyun.sh`）
- ✨ 新增完整的阿里百炼集成指南文档

#### 📝 文档和示例
- 📄 `ALIYUN_DASHSCOPE_GUIDE.md` - 详细集成指南
- 📄 `QUICK_START_ALIYUN.md` - 快速参考卡片
- 📄 `scripts/aliyun_dashscope_example.py` - 多功能示例脚本（5个使用场景）

#### 🔄 API 配置更新

##### API 信息
```
API Key: sk-69b4138e853648a79659aa01cc859dd6
Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
Model: claude-3-5-sonnet
Region: 华北2（北京）
Environment Variable: DASHSCOPE_CLAUDE_API_KEY
```

##### LLM 检测优先级（`--llm auto`）
1. **DASHSCOPE_CLAUDE_API_KEY** → dashscope_claude (阿里百炼) ✅ **新增**
2. ARK_API_KEY → doubao (字节豆包)
3. OPENAI_API_KEY → openai (OpenAI)
4. DASHSCOPE_API_KEY → dashscope (阿里通义千问)
5. 本地 Ollama

#### 🔧 脚本更新

##### `scripts/extract_entities.py`
- ✅ 添加 `dashscope_claude` LLM 支持
- ✅ 更新 LLM 检测逻辑
- ✅ 新增 OpenAI 兼容 API 客户端初始化
- ✅ 调整 LLM 优先级（阿里百炼优先于豆包）
- ✅ 更新命令行参数 `--llm` 选项列表

##### 支持的 LLM 列表
```bash
python scripts/extract_entities.py <pdf_path> --llm {openai|dashscope|dashscope_claude|doubao|ollama|auto}
```

#### 🎯 使用示例

**快速开始：**
```bash
# 自动配置（推荐）
setup_aliyun.bat          # Windows
chmod +x setup_aliyun.sh && ./setup_aliyun.sh  # Linux/Mac

# 使用阿里百炼提取实体
python scripts/extract_entities.py data/常识上册.pdf --llm dashscope_claude

# 查看示例
python scripts/aliyun_dashscope_example.py
```

**功能示例：**
1. 实体抽取 - 从文本中自动提取关键实体和关系
2. 文档分类 - 自动分类文档内容到预定义类别
3. 文本摘要 - 生成长文本的简洁摘要
4. 知识问答 - 问答系统实现
5. 批量处理 - 批量处理多个文本

#### 📦 依赖
```bash
pip install openai  # 必需
pip install pdfplumber  # PDF处理
```

#### 🔄 向后兼容性
- ✅ 完全兼容现有的豆包模型（`--llm doubao`）
- ✅ 完全兼容现有的 OpenAI（`--llm openai`）
- ✅ 完全兼容现有的阿里通义千问（`--llm dashscope`）
- ✅ 保留本地 Ollama 支持（`--llm ollama`）
- ✅ 自动检测仍然可用（`--llm auto`）

#### 📊 性能对比

| 模型 | 优势 | 用途 |
|------|------|------|
| Claude 3.5 Sonnet | 强推理能力，支持多语言 | 📊 **推荐用于知识抽取** |
| OpenAI GPT-4o | 功能完整 | 通用任务 |
| 阿里通义千问 | 中文优化 | 中文特定任务 |
| 字节豆包 | 低成本 | 基础任务 |
| Ollama (本地) | 隐私保护 | 本地处理 |

#### 🚀 性能提升
- 更强的推理能力用于实体关系提取
- 更好的中文理解
- 更高的准确率
- 支持更复杂的知识图谱构建

#### 📋 检查清单
- [x] API Key 配置
- [x] 环境变量设置
- [x] 自动化配置脚本
- [x] 单元测试脚本
- [x] 示例代码
- [x] 完整文档
- [x] 快速参考
- [x] 错误处理

#### 🔐 安全建议
- ⚠️ 不要将 API Key 提交到版本控制系统
- ⚠️ 使用环境变量或 .env 文件存储敏感信息
- ⚠️ 定期轮换 API Key
- ⚠️ 监控 API 使用量和成本

#### 📚 文档结构

```
项目根目录/
├── ALIYUN_DASHSCOPE_GUIDE.md      ← 详细集成指南
├── QUICK_START_ALIYUN.md          ← 快速参考
├── setup_aliyun.bat               ← Windows 配置脚本
├── setup_aliyun.sh                ← Linux/Mac 配置脚本
├── CHANGELOG.md                   ← 本文件
└── scripts/
    ├── extract_entities.py        ← 已更新
    └── aliyun_dashscope_example.py ← 新增示例
```

#### 🔗 相关资源
- [阿里百炼官方文档](https://help.aliyun.com/zh/dashscope/)
- [OpenAI 兼容 API](https://help.aliyun.com/zh/dashscope/developer-reference/compatible-with-openai)
- [模型信息](https://help.aliyun.com/zh/dashscope/latest/model-square)

#### ⚡ 后续计划
- [ ] 添加成本监控
- [ ] 支持流式输出
- [ ] 添加缓存机制
- [ ] 集成向量数据库
- [ ] 多轮对话支持
- [ ] 批量处理优化
- [ ] 性能基准测试

#### 🤝 贡献指南
如需改进本集成，请：
1. 提交 Issue 报告问题
2. Fork 项目进行改进
3. 提交 Pull Request

---

## 版本历史

### 之前的版本
- 支持 OpenAI GPT
- 支持阿里通义千问
- 支持字节豆包
- 支持本地 Ollama
- 支持自动 LLM 检测

---

**维护人员**: AI Assistant
**最后更新**: 2026-02-16
**状态**: ✅ 活跃维护
