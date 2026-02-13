"""
命令行交互式 Cypher 查询工具
替代 Neo4j Browser，不依赖浏览器界面
"""
import os
import sys
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "5211314zhg")


class CypherShell:
    def __init__(self, uri, user, password):
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            print(f"✅ 已连接到 Neo4j: {uri}")
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            sys.exit(1)
    
    def close(self):
        self.driver.close()
    
    def execute(self, query):
        """执行 Cypher 查询并格式化输出"""
        try:
            with self.driver.session() as session:
                result = session.run(query)
                records = list(result)
                
                if not records:
                    print("(无结果)")
                    return
                
                # 获取列名
                keys = records[0].keys()
                
                # 计算列宽
                col_widths = {key: len(key) for key in keys}
                for record in records:
                    for key in keys:
                        value_str = str(record[key])
                        col_widths[key] = max(col_widths[key], len(value_str))
                
                # 打印表头
                header = " | ".join(key.ljust(col_widths[key]) for key in keys)
                print(header)
                print("-" * len(header))
                
                # 打印数据行
                for record in records:
                    row = " | ".join(
                        str(record[key]).ljust(col_widths[key]) 
                        for key in keys
                    )
                    print(row)
                
                print(f"\n({len(records)} 行)")
                
        except Exception as e:
            print(f"❌ 查询错误: {e}")
    
    def run_interactive(self):
        """交互式命令行模式"""
        print("\n" + "="*60)
        print("Neo4j Cypher Shell (命令行版)")
        print("="*60)
        print("输入 Cypher 查询（输入 :exit 退出，:help 查看帮助）")
        print("多行查询以分号(;)结尾\n")
        
        buffer = []
        
        while True:
            try:
                if not buffer:
                    prompt = "neo4j> "
                else:
                    prompt = "    ... "
                
                line = input(prompt).strip()
                
                # 特殊命令
                if line.lower() == ':exit' or line.lower() == ':quit':
                    print("再见！")
                    break
                
                if line.lower() == ':help':
                    self.show_help()
                    continue
                
                if line.lower() == ':clear':
                    buffer = []
                    print("已清除缓冲区")
                    continue
                
                if line.lower() == ':stats':
                    self.show_stats()
                    continue
                
                if line.lower() == ':schema':
                    self.show_schema()
                    continue
                
                # 累积查询
                buffer.append(line)
                
                # 如果以分号结尾，执行查询
                if line.endswith(';'):
                    query = ' '.join(buffer).rstrip(';')
                    print()
                    self.execute(query)
                    print()
                    buffer = []
            
            except KeyboardInterrupt:
                print("\n(使用 :exit 退出)")
                buffer = []
            except EOFError:
                break
    
    def show_help(self):
        """显示帮助信息"""
        print("""
可用命令：
  :help    - 显示此帮助信息
  :exit    - 退出程序
  :clear   - 清除当前查询缓冲区
  :stats   - 显示数据库统计信息
  :schema  - 显示数据库 schema

示例查询：
  MATCH (n) RETURN n LIMIT 5;
  MATCH (p:Person) RETURN p.name, p.occupation;
  MATCH path = (p:Person)-[:KNOWS]-(f) RETURN path;
  
提示：
  - 查询必须以分号(;)结尾
  - 支持多行输入
  - Ctrl+C 可取消当前输入
        """)
    
    def show_stats(self):
        """显示数据库统计"""
        print("\n数据库统计信息：")
        self.execute("""
            MATCH (n)
            RETURN labels(n)[0] as 节点类型, count(*) as 数量
            ORDER BY 数量 DESC
        """)
    
    def show_schema(self):
        """显示 schema 信息"""
        print("\n节点标签：")
        self.execute("CALL db.labels()")
        
        print("\n关系类型：")
        self.execute("CALL db.relationshipTypes()")
        
        print("\n约束：")
        try:
            self.execute("SHOW CONSTRAINTS")
        except:
            print("(需要 Neo4j 4.0+ 支持)")
        
        print("\n索引：")
        try:
            self.execute("SHOW INDEXES")
        except:
            print("(需要 Neo4j 4.0+ 支持)")


def main():
    shell = CypherShell(URI, USER, PASSWORD)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 执行单个查询
        query = ' '.join(sys.argv[1:])
        shell.execute(query)
    else:
        # 交互式模式
        shell.run_interactive()
    
    shell.close()


if __name__ == "__main__":
    main()
