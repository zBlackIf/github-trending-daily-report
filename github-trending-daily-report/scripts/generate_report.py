#!/usr/bin/env python3
"""
GitHub Trending Daily Report Generator
Generates a dynamic skeleton report with enriched data and placeholder markers
for Claude to fill with deep analysis.
"""

import os
import sys
import json
import glob
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any, Tuple


# Domain classification keywords (topic/description -> domain)
DOMAIN_KEYWORDS = {
    "AI/机器学习": [
        "ai", "ml", "machine-learning", "deep-learning", "neural", "llm",
        "gpt", "transformer", "nlp", "natural-language", "chatbot", "agent",
        "copilot", "claude", "openai", "anthropic", "gemini", "diffusion",
        "stable-diffusion", "generative", "rag", "embedding", "fine-tuning",
        "reinforcement-learning", "computer-vision", "multimodal",
    ],
    "开发工具/DevOps": [
        "devtools", "developer-tools", "ide", "editor", "terminal", "cli",
        "git", "version-control", "ci-cd", "docker", "kubernetes", "devops",
        "build-tool", "package-manager", "linter", "formatter", "debugger",
        "testing", "automation", "workflow", "sdk", "framework", "library",
        "code-generation", "code-quality",
    ],
    "安全/隐私": [
        "security", "vulnerability", "penetration-testing", "encryption",
        "privacy", "authentication", "authorization", "firewall", "scanner",
        "malware", "threat", "audit", "compliance", "zero-trust",
    ],
    "Web/前端": [
        "web", "frontend", "react", "vue", "angular", "svelte", "nextjs",
        "css", "html", "javascript", "typescript", "ui", "ux", "design-system",
        "component", "tailwind", "responsive", "pwa", "browser",
    ],
    "后端/基础设施": [
        "backend", "api", "database", "server", "microservice", "distributed",
        "cloud", "aws", "azure", "gcp", "infrastructure", "networking",
        "message-queue", "cache", "storage", "proxy", "load-balancer",
    ],
    "数据/分析": [
        "data", "analytics", "visualization", "dashboard", "bi",
        "data-science", "statistics", "etl", "pipeline", "streaming",
        "big-data", "sql", "nosql", "graph-database", "time-series",
    ],
    "移动/桌面应用": [
        "mobile", "ios", "android", "react-native", "flutter", "swift",
        "kotlin", "desktop", "electron", "tauri", "cross-platform",
    ],
    "区块链/金融": [
        "blockchain", "crypto", "defi", "web3", "ethereum", "solana",
        "trading", "fintech", "quantitative", "finance", "investment",
    ],
    "系统/底层": [
        "operating-system", "kernel", "embedded", "iot", "firmware",
        "assembly", "compiler", "runtime", "virtual-machine", "wasm",
        "performance", "low-level", "systems-programming",
    ],
}


class TrendingReportGenerator:
    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir
        self.date = datetime.now()
        self.report_date = self.date.strftime("%Y-%m-%d")

    def generate_report(self, repos_data: List[Dict[str, Any]]) -> str:
        """Generate the full markdown report with dynamic content and placeholders."""
        report_lines = []

        # Header
        report_lines.extend([
            "# GitHub 趋势深度分析报告",
            "",
            f"**报告日期：** {self.report_date}",
            "**数据来源：** GitHub Trending",
            f"**报告仓库数量：** {len(repos_data)}个",
            "**分析维度：** 技术原理与实现、核心特性、潜在应用方向",
            "",
            "---",
            "",
        ])

        # Executive Summary
        report_lines.extend(self._generate_executive_summary(repos_data))

        # Technology Domain Distribution (dynamic)
        report_lines.extend(self._generate_domain_distribution(repos_data))

        # Detailed Analysis per repo
        report_lines.extend([
            "## 深度技术分析",
            "",
        ])
        for i, repo in enumerate(repos_data, 1):
            report_lines.extend(self._analyze_single_repo(repo, i))

        # Trend Summary placeholder (for Claude to fill)
        report_lines.extend(self._generate_trend_summary_skeleton(repos_data))

        # Footer
        report_lines.extend([
            "---",
            "",
            "*本报告由 GitHub Trending 深度分析系统自动生成*",
            f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
        ])

        return "\n".join(report_lines)

    def _generate_executive_summary(self, repos_data: List[Dict[str, Any]]) -> List[str]:
        """Generate executive summary with overview table."""
        lines = [
            "## 执行摘要",
            "",
            f"本报告基于{self.report_date}的GitHub Trending数据，对{len(repos_data)}个热门开源项目进行深度技术分析。",
            "",
            "<!-- DEEP_ANALYSIS: executive_summary_intro -->",
            "[请基于以下项目数据，补充1-2句概括性描述，说明本次趋势涵盖的主要技术领域和显著特征]",
            "",
            "### 趋势项目概览表",
            "",
            "| 排名 | 仓库名称 | 组织/作者 | 主要语言 | 今日星标 | 总星标 | 许可证 |",
            "|------|---------|----------|---------|---------|--------|--------|",
        ]

        for i, repo in enumerate(repos_data, 1):
            full_name = repo.get("full_name", "N/A")
            parts = full_name.split("/")
            org = parts[0] if len(parts) > 1 else "N/A"
            name = repo.get("name", "N/A")
            language = repo.get("language", "N/A")
            today_stars = repo.get("today_stars", "N/A")
            total_stars = repo.get("total_stars", "N/A")
            license_info = repo.get("metadata", {}).get("license", "N/A")
            lines.append(
                f"| {i} | {name} | {org} | {language} | {today_stars} | {total_stars} | {license_info} |"
            )

        lines.extend(["", "---", ""])
        return lines

    def _classify_repo_domain(self, repo: Dict[str, Any]) -> str:
        """Classify a repo into a technology domain based on topics and description."""
        # Gather all searchable text
        topics = repo.get("metadata", {}).get("topics", [])
        description = (repo.get("description", "") or "").lower()
        readme_excerpt = (repo.get("readme_content", "") or "")[:500].lower()
        search_text = " ".join(topics) + " " + description + " " + readme_excerpt

        # Score each domain
        domain_scores: Dict[str, int] = defaultdict(int)
        for domain, keywords in DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in search_text:
                    domain_scores[domain] += 1

        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        return "其他"

    def _generate_domain_distribution(self, repos_data: List[Dict[str, Any]]) -> List[str]:
        """Generate dynamic technology domain distribution analysis."""
        # Classify all repos
        domain_repos: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for repo in repos_data:
            domain = self._classify_repo_domain(repo)
            domain_repos[domain].append(repo)

        # Sort domains by number of repos (descending)
        sorted_domains = sorted(domain_repos.items(), key=lambda x: len(x[1]), reverse=True)

        lines = [
            "## 技术领域分布分析",
            "",
        ]

        for idx, (domain, repos) in enumerate(sorted_domains, 1):
            repo_names = ", ".join(r.get("name", "N/A") for r in repos)
            total_stars = sum(int(r.get("total_stars", 0)) for r in repos)
            total_stars_display = f"{total_stars:,}"

            lines.extend([
                f"### {idx}. {domain}（{len(repos)}个）",
                f"**代表项目：** {repo_names}",
                "",
                f"该领域项目总星标数超过{total_stars_display}。",
                "",
                "<!-- DEEP_ANALYSIS: domain_analysis -->",
                f"[请基于以上{domain}领域的{len(repos)}个项目，分析该领域的特征和子分类，每个子分类用1行描述]",
                "",
            ])

        lines.extend(["---", ""])
        return lines

    def _analyze_single_repo(self, repo: Dict[str, Any], rank: int) -> List[str]:
        """Generate detailed analysis skeleton for a single repository."""
        name = repo.get("name", "Unknown")
        full_name = repo.get("full_name", name)
        description = repo.get("description", "No description available")
        language = repo.get("language", "Unknown")
        today_stars = repo.get("today_stars", "N/A")
        total_stars = repo.get("total_stars", "N/A")

        # Metadata
        metadata = repo.get("metadata", {})
        topics = metadata.get("topics", [])
        license_info = metadata.get("license", "N/A")
        forks = metadata.get("forks", "N/A")
        homepage = metadata.get("homepage", "")
        created_at = metadata.get("created_at", "")

        # README excerpt for context
        readme = repo.get("readme_content", "")
        readme_excerpt = readme[:800] if readme else ""

        lines = [
            f"### {rank}. {full_name}",
            "",
            f"**仓库地址**: https://github.com/{full_name}",
        ]

        if homepage:
            lines.append(f"**项目主页**: {homepage}")

        lines.extend([
            f"**今日星标**: {today_stars} | **总星标**: {total_stars} | **Forks**: {forks}",
            f"**主要语言**: {language} | **许可证**: {license_info}" + (f" | **创建时间**: {created_at}" if created_at else ""),
        ])

        if topics:
            lines.append(f"**标签**: {', '.join(topics[:10])}")

        lines.extend([
            "",
            f"**项目简介**: {description}",
            "",
        ])

        # Include README excerpt as context for Claude
        if readme_excerpt:
            lines.extend([
                "<details>",
                "<summary>README 摘要（点击展开）</summary>",
                "",
                "```",
                readme_excerpt,
                "```",
                "",
                "</details>",
                "",
            ])

        # Deep analysis placeholder sections
        lines.extend([
            "#### 技术原理与实现",
            "",
            "<!-- DEEP_ANALYSIS: technical_principles -->",
            "[请基于 README 和项目信息，分析核心技术架构。要求：",
            "- 4-5个编号要点，每个要点包含2-3个子项",
            "- 必须引用项目实际使用的技术栈、框架、设计模式",
            "- 包含具体的架构组件和工作流程描述]",
            "",
            "#### 核心特性",
            "",
            "<!-- DEEP_ANALYSIS: core_features -->",
            "[请基于 README 和项目信息，列出核心特性。要求：",
            "- 5-6个编号特性，每个包含2-3个子项",
            "- 特性名称必须来自项目实际功能，不可泛泛而谈",
            "- 包含具体的技术指标或性能数据（如有）]",
            "",
            "#### 潜在应用方向",
            "",
            "<!-- DEEP_ANALYSIS: potential_applications -->",
            "[请基于项目定位和技术特点，分析应用方向。要求：",
            "- 5个编号方向，每个包含3个具体子项",
            "- 应用场景必须与项目实际能力匹配",
            "- 包含行业应用、技术场景、商业机会]",
            "",
            "---",
            "",
        ])

        return lines

    def _generate_trend_summary_skeleton(self, repos_data: List[Dict[str, Any]]) -> List[str]:
        """Generate trend summary skeleton with placeholders for Claude to fill."""
        repo_names = ", ".join(r.get("name", "N/A") for r in repos_data)

        lines = [
            "---",
            "",
            "## 趋势总结与洞察",
            "",
            "<!-- DEEP_ANALYSIS: trend_summary -->",
            f"[以下趋势总结需基于本次分析的 {len(repos_data)} 个项目: {repo_names}]",
            "",
            "### 当前热门技术趋势",
            "",
            "<!-- DEEP_ANALYSIS: technology_trends -->",
            "[请分析5个技术趋势，要求：",
            "- 每个趋势必须引用至少2个当天实际项目名称作为佐证",
            "- 每个趋势包含粗体标题 + 2个解释性子项",
            "- 趋势必须从实际项目中归纳，不可使用预设模板]",
            "",
            "### 投资建议与风险提示",
            "",
            "#### 高优先级关注方向",
            "",
            "<!-- DEEP_ANALYSIS: high_priority_investment -->",
            "[请列出2-3个高优先级关注方向，每个包含：",
            "- **投资逻辑**：为什么值得关注",
            "- **重点关注**：具体的项目名称",
            "- **投资建议**：具体的行动建议]",
            "",
            "#### 中优先级关注方向",
            "",
            "<!-- DEEP_ANALYSIS: medium_priority_investment -->",
            "[请列出2-3个中优先级关注方向，格式同上]",
            "",
            "### 风险分析",
            "",
            "<!-- DEEP_ANALYSIS: risk_analysis -->",
            "[请从4个维度分析风险，每个维度2-3个具体要点：",
            "- **技术风险**：技术成熟度、替代方案等",
            "- **市场风险**：竞争格局、商业化前景等",
            "- **安全合规风险**：许可证、数据安全等",
            "- **社区维护风险**：维护者活跃度、社区规模等]",
            "",
        ]

        return lines

    def save_report(self, content: str, filename: str = None):
        """Save the report to a file."""
        if filename is None:
            filename = f"github-trending-report-{self.report_date}.md"

        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath


def main():
    """Main entry point."""
    generator = TrendingReportGenerator()

    print(f"[{datetime.now().isoformat()}] Generating GitHub trending report...")

    # Find latest trending data file
    json_files = glob.glob("trending-data-*.json")
    if not json_files:
        print("Error: No trending data files found")
        sys.exit(1)

    # Get latest file
    latest_file = max(json_files, key=os.path.getctime)
    print(f"Reading data from: {latest_file}")

    # Load data
    with open(latest_file, "r", encoding="utf-8") as f:
        repos_data = json.load(f)

    if not repos_data:
        print("Error: No repository data found in file")
        sys.exit(1)

    # Check enrichment status
    enriched_count = sum(1 for r in repos_data if r.get("readme_content"))
    print(f"Data: {len(repos_data)} repos, {enriched_count} with README enrichment")

    # Generate report
    report_content = generator.generate_report(repos_data)
    output_file = generator.save_report(report_content)

    print(f"Report generated successfully: {output_file}")

    # Count placeholders
    placeholder_count = report_content.count("<!-- DEEP_ANALYSIS:")
    print(f"Placeholders for Claude deep analysis: {placeholder_count}")
    if placeholder_count > 0:
        print("Note: Use the Claude Code skill to fill in deep analysis sections")


if __name__ == "__main__":
    main()
