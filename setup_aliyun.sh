#!/bin/bash
#
# 阿里百炼大模型快速配置脚本（Linux/Mac）
#
# 功能：设置环境变量并验证 API 连接
#
# 使用方法：
#   chmod +x setup_aliyun.sh
#   ./setup_aliyun.sh

set -e

echo ""
echo "==============================================="
echo "阿里百炼平台大模型快速配置"
echo "==============================================="
echo ""

# 设置 API Key
DASHSCOPE_CLAUDE_API_KEY="sk-69b4138e853648a79659aa01cc859dd6"

echo "[*] 设置 API Key..."

# 检测 shell 类型
if [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    SHELL_RC="$HOME/.bash_profile"
fi

# 添加环境变量
if ! grep -q "DASHSCOPE_CLAUDE_API_KEY" "$SHELL_RC"; then
    echo "export DASHSCOPE_CLAUDE_API_KEY='$DASHSCOPE_CLAUDE_API_KEY'" >> "$SHELL_RC"
    echo "[✓] 环境变量已添加到 $SHELL_RC"
else
    echo "[!] 环境变量已存在于 $SHELL_RC"
fi

# 立即导出
export DASHSCOPE_CLAUDE_API_KEY="$DASHSCOPE_CLAUDE_API_KEY"

echo ""
echo "[*] 验证环境..."

# 检查 Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "[✓] Python 已安装"
    $PYTHON_CMD --version
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "[✓] Python 已安装"
    $PYTHON_CMD --version
else
    echo "[×] 未检测到 Python，请先安装 Python 3.7+"
    exit 1
fi

echo ""
echo "[*] 检查 openai 包..."

# 检查 openai 包
if $PYTHON_CMD -c "import openai" 2>/dev/null; then
    echo "[✓] openai 已安装"
    $PYTHON_CMD -c "import openai; print(f'    版本: {openai.__version__}')"
else
    echo "[!] openai 未安装，正在安装..."
    pip install openai
    if [ $? -eq 0 ]; then
        echo "[✓] openai 安装成功"
    else
        echo "[×] openai 安装失败"
        exit 1
    fi
fi

echo ""
echo "[*] 测试 API 连接..."
echo ""

$PYTHON_CMD << 'EOF'
import os
import sys
from openai import OpenAI

try:
    client = OpenAI(
        base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
        api_key=os.getenv('DASHSCOPE_CLAUDE_API_KEY', 'sk-69b4138e853648a79659aa01cc859dd6')
    )
    
    print('[*] 发送测试请求...')
    response = client.chat.completions.create(
        model='claude-3-5-sonnet',
        messages=[{'role': 'user', 'content': 'Hi'}],
        max_tokens=10
    )
    
    print('[✓] API 连接成功！')
    print('    响应内容:', response.choices[0].message.content)
    sys.exit(0)
except Exception as e:
    print('[×] API 连接失败:', str(e))
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "==============================================="
    echo "[✓] 配置完成！"
    echo "==============================================="
    echo ""
    echo "接下来，你可以："
    echo ""
    echo "1. 运行提取实体脚本："
    echo "   python3 scripts/extract_entities.py data/常识上册.pdf"
    echo ""
    echo "2. 运行示例脚本："
    echo "   python3 scripts/aliyun_dashscope_example.py"
    echo ""
    echo "3. 查看完整文档："
    echo "   cat ALIYUN_DASHSCOPE_GUIDE.md"
    echo ""
    echo "==============================================="
    echo ""
    echo "提示: 新打开的终端窗口会自动加载新的环境变量"
else
    echo ""
    echo "[!] 连接测试失败，请检查："
    echo "    - API Key 是否正确"
    echo "    - 网络连接是否正常"
    echo "    - API Key 是否有有效期和配额"
    echo ""
    exit 1
fi
