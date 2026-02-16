#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
阿里百炼平台大模型 API 使用示例

API 密钥配置:
- API Key: sk-69b4138e853648a79659aa01cc859dd6
- Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
- Model: qwen-max (默认) / claude-3-5-sonnet (需要权限)

Windows 环境变量设置:
set DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6

Linux/Mac 环境变量设置:
export DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6
"""

import os
import json
from typing import Optional
from openai import OpenAI


def init_aliyun_client() -> OpenAI:
    """初始化阿里百炼 OpenAI 客户端"""
    # 优先使用环境变量，如果未设置则使用默认值
    api_key = os.getenv("DASHSCOPE_CLAUDE_API_KEY", "sk-69b4138e853648a79659aa01cc859dd6")
    
    if not api_key:
        raise ValueError(
            "未设置 DASHSCOPE_CLAUDE_API_KEY 环境变量！\n\n"
            "设置方法：\n"
            "Windows (cmd):  set DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6\n"
            "Windows (PS):   $env:DASHSCOPE_CLAUDE_API_KEY = 'sk-69b4138e853648a79659aa01cc859dd6'\n"
            "Linux/Mac:      export DASHSCOPE_CLAUDE_API_KEY=sk-69b4138e853648a79659aa01cc859dd6"
        )
    
    client = OpenAI(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=api_key
    )
    return client


def extract_entities_example():
    """实体抽取示例"""
    client = init_aliyun_client()
    
    system_prompt = """你是一个知识抽取专家。请从给定的文本中抽取关键实体和关系，并返回 JSON 格式的结果。"""
    
    user_prompt = """从以下文本中抽取主要实体（人物、地点、概念等）和它们之间的关系：

文本：
习近平总书记在党中央2024年度工作会议上强调，要深入学习贯彻新时代中国特色社会主义思想，
加强党的建设，推动高质量发展。中国共产党第二十届中央委员会第三次全体会议在北京召开。

返回 JSON 格式：
{
    "entities": [{"name": "...", "type": "..."}],
    "relations": [{"from": "...", "to": "...", "relation": "..."}]
}"""
    
    response = client.chat.completions.create(
        model="qwen3.5-plus",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=1024
    )
    
    return response.choices[0].message.content


def document_classification_example():
    """文档分类示例"""
    client = init_aliyun_client()
    
    system_prompt = """你是一个文档分类专家。请根据文本内容将其分类到以下类别之一：
    - 新闻政务
    - 科技创新
    - 经济金融
    - 教育文化
    - 社会民生
    - 其他
    
    返回 JSON 格式，包含分类结果和置信度。"""
    
    user_prompt = """请对以下文本进行分类：

2024年中央经济工作会议指出，要坚持稳字当头、稳中求进，
加强宏观调控，推动经济社会高质量发展。

返回格式：
{
    "category": "分类结果",
    "confidence": 0.95,
    "reasoning": "分类理由"
}"""
    
    response = client.chat.completions.create(
        model="qwen-max",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content


def summarization_example():
    """文本摘要示例"""
    client = init_aliyun_client()
    
    long_text = """
    人工智能是计算机科学的一个分支，是一门研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统的新的技术科学。
    
    人工智能是包括十分广泛的科学，它甚至包括机器人学。但不管怎样，主要的研究领域包括机器学习、深度学习、自然语言处理、计算机视觉等。
    
    人工智能在现代社会中的应用越来越广泛，从医疗诊断到自动驾驶，从自然语言处理到推荐系统，人工智能正在改变我们的生活方式。
    
    深度学习作为机器学习的一个子集，在图像识别、语音识别和自然语言处理等领域取得了显著的成果，
    推动了整个人工智能领域的发展。
    """
    
    system_prompt = """你是一个专业的文本摘要专家。请用中文对给定的文本进行内容摘要，
    摘要应该保留原文的主要信息，字数在100-200字之间。"""
    
    response = client.chat.completions.create(
        model="qwen-max",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请对以下文本进行摘要：\n\n{long_text}"}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content


def knowledge_qa_example():
    """知识问答示例"""
    client = init_aliyun_client()
    
    system_prompt = """你是一个知识问答系统。请根据所学知识，
    对用户提出的问题进行准确、清晰的回答。"""
    
    questions = [
        "什么是知识图谱？",
        "知识图谱的主要应用领域有哪些？",
        "如何构建一个知识图谱系统？"
    ]
    
    for question in questions:
        response = client.chat.completions.create(
            model="qwen-max",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.3
        )
        
        print(f"\n问题: {question}")
        print(f"回答: {response.choices[0].message.content}")


def batch_processing_example():
    """批量处理示例"""
    client = init_aliyun_client()
    
    texts = [
        "中国是世界上人口最多的国家，位于亚洲东部。",
        "Python 是一种高级编程语言，广泛应用于数据科学和人工智能领域。",
        "知识图谱是一种语义网络，用于表示和管理知识。"
    ]
    
    system_prompt = """你是一个关键词提取专家。请从给定的文本中提取3-5个关键词，
    并返回 JSON 格式的列表。"""
    
    results = []
    for i, text in enumerate(texts, 1):
        response = client.chat.completions.create(
            model="qwen-max",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请从以下文本中提取关键词：\n{text}"}
            ],
            temperature=0.3
        )
        
        results.append({
            "text": text,
            "keywords": response.choices[0].message.content
        })
    
    return results


def main():
    """主函数 - 运行所有示例"""
    print("=" * 60)
    print("阿里百炼平台大模型 API 使用示例")
    print("=" * 60)
    
    try:
        # 实体抽取示例
        print("\n[1] 实体抽取示例")
        print("-" * 40)
        result = extract_entities_example()
        print(result)
        
        # 文档分类示例
        print("\n[2] 文档分类示例")
        print("-" * 40)
        result = document_classification_example()
        print(result)
        
        # 文本摘要示例
        print("\n[3] 文本摘要示例")
        print("-" * 40)
        result = summarization_example()
        print(result)
        
        # 知识问答示例
        print("\n[4] 知识问答示例")
        print("-" * 40)
        knowledge_qa_example()
        
        # 批量处理示例
        print("\n[5] 批量处理示例")
        print("-" * 40)
        results = batch_processing_example()
        for item in results:
            print(f"\n文本: {item['text']}")
            print(f"关键词: {item['keywords']}")
        
        print("\n" + "=" * 60)
        print("所有示例执行完毕！")
        print("=" * 60)
        
    except ValueError as e:
        print(f"\n[ERROR] 错误: {e}")
    except Exception as e:
        print(f"\n[ERROR] 执行出错: {type(e).__name__}: {str(e)}")
        print("\n可能的原因：")
        print("1. 网络连接问题")
        print("2. API Key 无效或过期")
        print("3. openai 包未安装（pip install openai）")
        print("4. 使用了需要权限的模型")
        print("\n更多帮助请查看 ALIYUN_DASHSCOPE_GUIDE.md 或 QUICK_FIX.md")


if __name__ == "__main__":
    main()
