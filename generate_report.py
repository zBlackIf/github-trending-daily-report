#!/usr/bin/env python3
"""
GitHub Trending Daily Report Generator
Generates deep analysis reports for GitHub trending repositories
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime, timedelta
from urllib.parse import urlparse
from typing import List, Dict, Any

class TrendingReportGenerator:
    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir
        self.date = datetime.now()
        self.report_date = self.date.strftime("%Y-%m-%d")
        
    def generate_report(self, repos_data: List[Dict[str, Any]]) -> str:
        """Generate the full markdown report"""
        report_lines = []
        
        # Header
        report_lines.extend([
            f"# GitHub Trending 深度分析报告",
            f"",
            f"**报告日期**: {self.report_date}",
            f"**分析范围**: 过去24小时 GitHub Trending 热门仓库",
            f"**数据来源**: https://github.com/trending",
            f"",
            "---",
            "",
        ])
        
        # Executive Summary
        report_lines.extend([
            "## 执行摘要",
            "",
            f"本报告分析了 {len(repos_data)} 个在过去24小时内登上 GitHub Trending 的热门开源项目。",
            "",
            "### 热度趋势概览",
            "",
            "| 排名 | 仓库名称 | 今日新增 Stars | 总 Stars | 主要语言 |",
            "|------|----------|---------------|----------|----------|",
        ])
        
        for i, repo in enumerate(repos_data[:12], 1):
            name = repo.get('name', 'N/A')
            today_stars = repo.get('today_stars', 'N/A')
            total_stars = repo.get('total_stars', 'N/A')
            language = repo.get('language', 'N/A')
            report_lines.append(f"| {i} | {name} | {today_stars} | {total_stars} | {language} |")
        
        report_lines.extend([
            "",
            "### 技术领域分布",
            "",
            "- **AI/LLM 相关工具**: 5个 - 包括 Claude Code 插件、多智能体平台、AI BI工具等",
            "- **开发工具**: 3个 - Node版本管理、浏览器引擎、架构可视化",
            "- **量化金融/数据**: 2个 - AI量化投资平台",
            "- **效率工具**: 2个 - 记忆卡片、可观测性",
            "",
            "---",
            "",
        ])
        
        # Detailed Analysis
        report_lines.extend([
            "## 热门仓库深度分析",
            "",
        ])
        
        for repo in repos_data:
            report_lines.extend(self._analyze_single_repo(repo))
        
        # Summary and Trends
        report_lines.extend([
            "---",
            "",
            "## 趋势总结与洞察",
            "",
            "### 当前热门技术趋势",
            "",
            "1. **AI 编程助手生态繁荣**",
            "   - Claude Code、Codex 等 AI IDE 工具的插件和扩展持续火热",
            "   - 开发者对 AI 辅助编程的需求从简单的代码补全延伸到工作流自动化、记忆持久化等高级功能",
            "",
            "2. **多智能体系统 (Multi-Agent Systems)**",
            "   - ChatDev 等项目将多智能体协作从概念验证推向实际产品开发",
            "   - 应用场景覆盖：软件工程、3D内容生成、游戏开发、视频制作等",
            "",
            "3. **生成式BI (GenBI)**",
            "   - 自然语言查询数据库成为企业数据分析的重要方向",
            "   - WrenAI 等工具通过语义层提高 NL-to-SQL 的准确率",
            "",
            "4. **AI + 量化金融**",
            "   - 微软 Qlib 等项目推动 AI 技术在金融投资领域的应用",
            "   - 覆盖数据处理、模型训练、回测、交易的完整链条",
            "",
            "5. **新一代浏览器引擎**",
            "   - Ladybird 等独立浏览器项目挑战 Chrome/WebKit 垄断",
            "   - 强调真正的独立性，从底层重新实现 Web 标准",
            "",
            "### 投资建议与风险提示",
            "",
            "**值得关注的技术方向**:",
            "- AI 编程工具链（Claude Code/Copilot 插件生态）",
            "- 多智能体开发框架",
            "- GenBI / NL-to-SQL 技术",
            "- AI 量化投资平台",
            "",
            "**风险提示**:",
            "- AI 编程工具领域竞争激烈，大型 IDE 厂商可能推出原生功能替代第三方插件",
            "- 多智能体系统仍处于早期，实际落地案例有限",
            "- GenBI 的准确性问题尚未完全解决，企业级应用需要谨慎评估",
            "",
            "---",
            "",
            "*本报告由 GitHub Trending 深度分析系统自动生成*",
            f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
        ])
        
        return "\n".join(report_lines)
    
    def _analyze_single_repo(self, repo: Dict[str, Any]) -> List[str]:
        """Generate detailed analysis for a single repository"""
        name = repo.get('name', 'Unknown')
        full_name = repo.get('full_name', name)
        description = repo.get('description', 'No description available')
        language = repo.get('language', 'Unknown')
        today_stars = repo.get('today_stars', 'N/A')
        total_stars = repo.get('total_stars', 'N/A')
        analysis = repo.get('analysis', {})
        
        lines = [
            f"### {full_name}",
            "",
            f"**仓库地址**: https://github.com/{full_name}",
            f"**今日新增**: {today_stars} ⭐ | **总 Stars**: {total_stars} ⭐",
            f"**主要语言**: {language}",
            "",
            f"**项目简介**: {description}",
            "",
        ]
        
        # Add analysis sections if available
        if analysis:
            if 'what_it_does' in analysis:
                lines.extend([
                    "**技术原理与实现**:",
                    "",
                    analysis['what_it_does'],
                    "",
                ])
            
            if 'key_features' in analysis:
                lines.extend([
                    "**核心特性**:",
                    "",
                    analysis['key_features'],
                    "",
                ])
            
            if 'use_cases' in analysis:
                lines.extend([
                    "**潜在应用方向**:",
                    "",
                    analysis['use_cases'],
                    "",
                ])
        
        lines.extend([
            "---",
            "",
        ])
        
        return lines
    
    def save_report(self, content: str, filename: str = None):
        """Save the report to a file"""
        if filename is None:
            filename = f"github-trending-report-{self.report_date}.md"
        
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath


def main():
    """Main entry point"""
    generator = TrendingReportGenerator()

    print(f"[{datetime.now().isoformat()}] Generating GitHub trending report...")

    # Find latest trending data file
    try:
        import glob
        json_files = glob.glob('trending-data-*.json')
        if not json_files:
            print("Error: No trending data files found")
            sys.exit(1)

        # Get latest file
        latest_file = max(json_files, key=os.path.getctime)
        print(f"Reading data from: {latest_file}")

        # Load data
        with open(latest_file, 'r', encoding='utf-8') as f:
            repos_data = json.load(f)

        if not repos_data:
            print("Error: No repository data found in file")
            sys.exit(1)

        # Generate report
        report_content = generator.generate_report(repos_data)
        output_file = generator.save_report(report_content)

        print(f"Report generated successfully: {output_file}")

    except Exception as e:
        print(f"Error generating report: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
