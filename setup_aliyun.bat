@echo off
REM 阿里百炼大模型快速配置脚本（Windows）
REM 功能：设置环境变量并验证 API 连接
REM 使用：双击运行或在命令行运行

setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

cls
echo.
echo ===============================================
echo  阿里百炼平台大模型快速配置
echo ===============================================
echo.

REM 设置本地环境变量
set "DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6"

echo [1/4] 设置环境变量...
echo  - API Key: %DASHSCOPE_CLAUDE_API_KEY%
echo  - Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
echo  - Model: claude-3-5-sonnet
echo.

REM 尝试设置永久环境变量（不影响继续）
reg add "HKCU\Environment" /v DASHSCOPE_CLAUDE_API_KEY /d "%DASHSCOPE_CLAUDE_API_KEY%" /f >nul 2>&1
if !errorlevel! equ 0 (
    echo [✓] 永久环境变量设置成功
) else (
    echo [!] 提示：未能设置永久环境变量
)
echo.

REM 检查 Python
echo [2/4] 检查 Python 环境...
python --version >nul 2>&1
if !errorlevel! equ 0 (
    echo [✓] Python 已安装
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo    版本: %%i
) else (
    echo [!] 未找到 Python
    echo    请先安装 Python 3.7+ 或将 Python 添加到 PATH
)
echo.

REM 检查并安装 openai
echo [3/4] 检查 openai 包...
python -m pip show openai >nul 2>&1
if !errorlevel! equ 0 (
    echo [✓] openai 已安装
) else (
    echo [!] openai 未安装，正在安装...
    python -m pip install -q openai 2>nul
    if !errorlevel! equ 0 (
        echo [✓] openai 安装成功
    ) else (
        echo [!] openai 安装可能失败
    )
)
echo.

REM 测试 API 连接
echo [4/4] 测试 API 连接...
python << PYEOF
import os
import sys
try:
    from openai import OpenAI
    api_key = os.getenv('DASHSCOPE_CLAUDE_API_KEY', 'sk-69b4138e853648a79659aa01cc859dd6')
    client = OpenAI(
        base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
        api_key=api_key
    )
    print('[*] 发送测试请求...')
    response = client.chat.completions.create(
        model='claude-3-5-sonnet',
        messages=[{'role': 'user', 'content': 'test'}],
        max_tokens=5
    )
    print('[OK] API 连接成功！')
except ImportError:
    print('[!] openai 模块未安装')
except Exception as e:
    if '401' in str(e):
        print('[!] API Key 无效')
    else:
        print('[!] 连接失败: ' + str(e)[:80])
PYEOF

echo.
echo ===============================================
echo  配置完成！
echo ===============================================
echo.
echo 下一步：
echo.
echo 1. 关闭本窗口并打开新命令窗口
echo.
echo 2. 测试 API 连接：
echo    python scripts\aliyun_dashscope_example.py
echo.
echo 3. 提取 PDF 实体：
echo    python scripts\extract_entities.py data\常识上册.pdf
echo.
echo 4. 查看文档：
echo    - START_HERE.md
echo    - ALIYUN_DASHSCOPE_GUIDE.md
echo.
echo ===============================================
echo.
echo 按任意键退出...
pause >nul
