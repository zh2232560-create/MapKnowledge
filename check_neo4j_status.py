#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Neo4j 启动状态检查和诊断工具

功能：
1. 检查 Neo4j 是否正在运行
2. 检查 7687 端口是否开放
3. 测试数据库连接
4. 提供启动/重启指导
"""

import os
import sys
import socket
import time
from pathlib import Path

def check_port_open(host: str = "localhost", port: int = 7687) -> bool:
    """检查 Neo4j 端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"  [ERROR] 检查端口失败: {e}")
        return False


def check_neo4j_running() -> bool:
    """检查 Neo4j 进程是否运行"""
    try:
        import subprocess
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq java.exe"],
            capture_output=True,
            text=True
        )
        return "java.exe" in result.stdout
    except Exception:
        return False


def test_neo4j_connection() -> bool:
    """测试 Neo4j 数据库连接"""
    try:
        from neo4j import GraphDatabase
        
        uri = "bolt://localhost:7687"
        user = "neo4j"
        password = "5211314zhg"
        
        driver = GraphDatabase.driver(uri, auth=(user, password), max_connection_lifetime=3)
        driver.verify_connectivity()
        driver.close()
        return True
    except Exception as e:
        print(f"  [ERROR] 连接失败: {e}")
        return False


def main():
    print("\n" + "="*70)
    print("Neo4j 启动状态诊断")
    print("="*70)
    
    # 检查 1：进程状态
    print("\n[1] 检查 Neo4j 进程状态...")
    if check_neo4j_running():
        print("  ✓ Neo4j 进程正在运行")
    else:
        print("  ✗ Neo4j 进程未运行")
    
    # 检查 2：端口状态
    print("\n[2] 检查 7687 端口状态...")
    if check_port_open():
        print("  ✓ 7687 端口已开放")
    else:
        print("  ✗ 7687 端口未开放（Neo4j 可能未启动）")
    
    # 检查 3：数据库连接
    print("\n[3] 尝试连接 Neo4j 数据库...")
    if test_neo4j_connection():
        print("  ✓ 数据库连接成功！")
        print("\n" + "="*70)
        print("✓ Neo4j 已就绪，可以导入数据")
        print("="*70)
        print("\n运行导入命令:")
        print("  python import_entities.py data/*_entities_extracted.json")
        return 0
    else:
        print("  ✗ 数据库连接失败")
    
    # 诊断信息
    print("\n" + "="*70)
    print("诊断结果：Neo4j 未启动或未响应")
    print("="*70)
    
    print("\n解决方案：")
    print("\n方案 1：启动 Neo4j（推荐）")
    print("  运行命令：start_neo4j.bat")
    print("  或双击：start_neo4j.bat")
    print("  然后等待 10-15 秒让服务完全启动")
    
    print("\n方案 2：使用 Neo4j Desktop（图形界面）")
    print("  1. 打开 Neo4j Desktop")
    print("  2. 启动默认数据库")
    print("  3. 确保端口是 7687")
    
    print("\n方案 3：使用 Neo4j 命令行")
    print("  cd D:\\vsprogram\\mapKnowledge\\neo4j-community-5.26.1\\bin")
    print("  neo4j.bat console")
    
    print("\n方案 4：检查配置")
    print("  检查 neo4j.conf 中的配置：")
    print("  - server.bolt.enabled=true")
    print("  - server.bolt.listen_address=:7687")
    print("  配置文件位置：neo4j-community-5.26.1/conf/neo4j.conf")
    
    print("\n启动后，运行以下命令验证：")
    print("  python check_neo4j_status.py")
    
    print("\n" + "="*70)
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
