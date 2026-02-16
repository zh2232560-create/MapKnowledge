@echo off
REM 阿里百炼大模型快速配置脚本（Windows）
REM 
REM 功能：设置环境变量并验证 API 连接
REM
REM 使用方法：
REM   双击运行此脚本
REM   或在命令行运行：setup_aliyun.bat

setlocal enabledelayedexpansion

echo.
echo ===============================================
echo 阿里百炼平台大模型快速配置
echo ===============================================
echo.

REM 设置 API Key
set "DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6"

echo [*] 设置 API Key...
setx DASHSCOPE_CLAUDE_API_KEY "%DASHSCOPE_CLAUDE_API_KEY%"
if !errorlevel! equ 0 (
    echo [✓] 环境变量设置成功！
    echo.
    echo API Key: %DASHSCOPE_CLAUDE_API_KEY%
    echo Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
    echo Model: claude-3-5-sonnet
) else (
    echo [×] 设置环境变量失败！
    echo 请以管理员身份运行此脚本
    goto :error
)

echo.
echo [*] 验证环境...

REM 检查 Python
python --version >nul 2>&1
if !errorlevel! equ 0 (
    echo [✓] Python 已安装
    for /f "tokens=*" %%i in ('python --version') do (
        echo     版本: %%i
    )
) else (
    echo [×] 未检测到 Python，请先安装 Python 3.7+
    goto :error
)

echo.
echo [*] 检查 openai 包...
pip show openai >nul 2>&1
if !errorlevel! equ 0 (
    echo [✓] openai 已安装
    for /f "tokens=2" %%i in ('pip show openai ^| findstr Version') do (
        echo     版本: %%i
    )
) else (
    echo [!] openai 未安装，正在安装...
    pip install openai
    if !errorlevel! equ 0 (
        echo [✓] openai 安装成功
    ) else (
        echo [×] openai 安装失败
        goto :error
    )
)

echo.
echo [*] 测试 API 连接...
echo.

python -c "
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
"

if !errorlevel! equ 0 (
    echo.
    echo ===============================================
    echo [✓] 配置完成！
    echo ===============================================
    echo.
    echo 接下来，你可以：
    echo.
    echo 1. 运行提取实体脚本：
    echo    python scripts\extract_entities.py data\常识上册.pdf
    echo.
    echo 2. 运行示例脚本：
    echo    python scripts\aliyun_dashscope_example.py
    echo.
    echo 3. 查看完整文档：
    echo    ALIYUN_DASHSCOPE_GUIDE.md
    echo.
    echo ===============================================
) else (
    echo.
    echo [!] 连接测试失败，请检查：
    echo    - API Key 是否正确
    echo    - 网络连接是否正常
    echo    - API Key 是否有有效期和配额
    echo.
    goto :error
)

goto :end

:error
echo.
echo [×] 配置失败！请参考 ALIYUN_DASHSCOPE_GUIDE.md 文档
echo.

:end
pause
