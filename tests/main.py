
from datetime import datetime


from src.agent import LLMAgent
from src.config_loader import ConfigLoader
from src.arxiv_fetcher import ArxivFetcher
from src.html2md import html2markdown

# llm = LLMAgent(provider="deepseek", config_path="/home/wanger/codes/arxiv_agent/config/config.yaml")
llm = LLMAgent(provider="alibaba", config_path="/home/wanger/codes/arxiv_agent/config/config.yaml")

print(llm.ask("你是谁"))
print()
"""主函数"""
print("🚀 开始获取arXiv cs.AI最新论文...")

fetcher = ArxivFetcher()

# 获取最近7天的论文
papers = fetcher.get_recent_papers(category="cs.AI", max_results=50, days_back=10)

for paper in papers:
    html_path = paper['arxiv_url'].replace("abs", "html")
    
    # 获取htmlpath对应链接内容
    try:
        import requests
        
        # 发送HTTP请求获取HTML内容
        response = requests.get(html_path)
        response.raise_for_status()  # 检查请求是否成功
        
        # 获取HTML内容
        html_content = response.text
        
        # 打印成功信息
        print(f"成功获取HTML内容，链接: {html_path}")
        print(f"内容长度: {len(html_content)} 字符")
        print(llm.ask(f" {html2markdown(html_path)} 给出论文的10个关键词"))
        exit(0)
    except requests.RequestException as e:
        print(f"获取 {html_path} 失败: {e}")
