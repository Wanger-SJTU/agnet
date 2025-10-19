#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arXiv论文获取器
获取当天cs.AI领域的最新论文
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time
import sys
from typing import List, Dict, Optional


class ArxivFetcher:
    """arXiv论文获取器"""
    
    def __init__(self, base_url: str = "http://export.arxiv.org/api/query"):
        """
        初始化arXiv获取器
        
        Args:
            base_url: arXiv API基础URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ArxivFetcher/1.0)'
        })
    
    def get_recent_papers(self, category: str = "cs.AI", max_results: int = 50, days_back: int = 7) -> List[Dict]:
        """
        获取最近几天指定类别的最新论文
        
        Args:
            category: 论文类别，默认为cs.AI
            max_results: 最大返回结果数
            days_back: 回溯天数，默认为7天
            
        Returns:
            论文信息列表
        """
        # 计算日期范围
        today = datetime.now().date()
        start_date = today - timedelta(days=days_back)
        
        # 构建查询参数 - 按提交日期排序获取最新论文
        query = f"cat:{category}"
        
        params = {
            'search_query': query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # 解析XML响应，过滤最近几天的论文
            papers = self._parse_xml_response(response.text, start_date, today)
            return papers
            
        except requests.RequestException as e:
            print(f"请求arXiv API失败: {e}")
            return []
        except ET.ParseError as e:
            print(f"解析XML响应失败: {e}")
            return []
    
    def _parse_xml_response(self, xml_content: str, start_date: datetime.date, end_date: datetime.date) -> List[Dict]:
        """
        解析arXiv API的XML响应
        
        Args:
            xml_content: XML响应内容
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            解析后的论文信息列表
        """
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # 命名空间处理
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                paper = self._parse_paper_entry(entry, ns, start_date, end_date)
                if paper:
                    papers.append(paper)
                    
        except Exception as e:
            print(f"解析论文条目失败: {e}")
            
        return papers
    
    def _parse_paper_entry(self, entry, ns, start_date: datetime.date, end_date: datetime.date) -> Optional[Dict]:
        """
        解析单个论文条目
        
        Args:
            entry: XML条目元素
            ns: 命名空间
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            论文信息字典或None
        """
        try:
            # 获取论文ID
            id_elem = entry.find('atom:id', ns)
            if id_elem is None:
                return None
            paper_id = id_elem.text.split('/')[-1] if id_elem.text else None
            
            # 获取标题
            title_elem = entry.find('atom:title', ns)
            title = title_elem.text.strip() if title_elem is not None and title_elem.text else "无标题"
            
            # 获取摘要
            summary_elem = entry.find('atom:summary', ns)
            summary = summary_elem.text.strip() if summary_elem is not None and summary_elem.text else "无摘要"
            
            # 获取作者
            authors = []
            for author_elem in entry.findall('atom:author/atom:name', ns):
                if author_elem.text:
                    authors.append(author_elem.text.strip())
            
            # 获取提交日期
            published_elem = entry.find('atom:published', ns)
            if published_elem is None or not published_elem.text:
                return None
                
            published_date = datetime.fromisoformat(published_elem.text.replace('Z', '+00:00')).date()
            
            # 只返回指定日期范围内的论文
            if published_date < start_date or published_date > end_date:
                return None
            
            # 获取分类
            categories = []
            for category_elem in entry.findall('atom:category', ns):
                term = category_elem.get('term')
                if term:
                    categories.append(term)
            
            # 获取PDF链接
            pdf_link = None
            for link_elem in entry.findall('atom:link', ns):
                if link_elem.get('title') == 'pdf' or link_elem.get('type') == 'application/pdf':
                    pdf_link = link_elem.get('href')
                    break
            
            return {
                'id': paper_id,
                'title': title,
                'authors': authors,
                'summary': summary,
                'published_date': published_date.isoformat(),
                'categories': categories,
                'pdf_link': pdf_link,
                'arxiv_url': f"https://arxiv.org/abs/{paper_id}" if paper_id else None
            }
            
        except Exception as e:
            print(f"解析论文条目时出错: {e}")
            return None
    
    def format_papers_output(self, papers: List[Dict]) -> str:
        """
        格式化论文输出
        
        Args:
            papers: 论文信息列表
            
        Returns:
            格式化的输出字符串
        """
        if not papers:
            return "最近7天内没有找到新的cs.AI论文。"
        
        output = []
        output.append(f"📚 arXiv cs.AI 最近7天最新论文 ({len(papers)}篇)")
        output.append("=" * 60)
        
        for i, paper in enumerate(papers, 1):
            output.append(f"\n{i}. {paper['title']}")
            output.append(f"   作者: {', '.join(paper['authors'][:3])}{'等' if len(paper['authors']) > 3 else ''}")
            output.append(f"   论文ID: {paper['id']}")
            output.append(f"   提交日期: {paper['published_date']}")
            output.append(f"   分类: {', '.join(paper['categories'])}")
            output.append(f"   PDF链接: {paper['pdf_link']}")
            html_path = paper['arxiv_url'].replace("abs", "html")
            output.append(f"  html链接: {html_path}")
            output.append(f"   arXiv页面: {paper['arxiv_url']}")
            
            # 摘要前100个字符
            summary_preview = paper['summary'][:100] + "..." if len(paper['summary']) > 100 else paper['summary']
            output.append(f"   摘要: {summary_preview}")
            output.append("-" * 40)
        
        return "\n".join(output)


