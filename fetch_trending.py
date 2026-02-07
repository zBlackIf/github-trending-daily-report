#!/usr/bin/env python3
"""
GitHub Trending Data Fetcher
Fetches and parses GitHub trending repositories
"""

import requests
import re
import json
from datetime import datetime
from typing import List, Dict, Any


def fetch_github_trending() -> List[Dict[str, Any]]:
    """Fetch trending repositories from GitHub"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get('https://github.com/trending', headers=headers, timeout=30)
        response.raise_for_status()
        html = response.text
        
        repos = parse_trending_html(html)
        return repos
        
    except Exception as e:
        print(f"Error fetching GitHub trending: {e}")
        return []


def parse_trending_html(html: str) -> List[Dict[str, Any]]:
    """Parse HTML to extract trending repository information"""
    
    repos = []
    
    # Pattern to match repository entries
    # GitHub trending page structure
    repo_pattern = r'<article[^>]*class="[^"]*Box-row[^"]*"[^>]*>(.*?)</article>'
    repo_blocks = re.findall(repo_pattern, html, re.DOTALL)
    
    for block in repo_blocks[:20]:  # Limit to top 20
        repo_info = parse_repo_block(block)
        if repo_info:
            repos.append(repo_info)
    
    return repos


def parse_repo_block(block: str) -> Dict[str, Any]:
    """Parse a single repository block"""
    
    try:
        # Extract repository name
        name_match = re.search(r'<h2[^>]*>\s*<a[^>]*href="/([^"]+)"', block)
        if not name_match:
            return None
        
        full_name = name_match.group(1).strip()
        
        # Extract description
        desc_match = re.search(r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>', block, re.DOTALL)
        description = clean_html(desc_match.group(1)) if desc_match else "No description"
        
        # Extract language
        lang_match = re.search(r'<span[^>]*itemprop="programmingLanguage"[^>]*>(.*?)</span>', block)
        language = lang_match.group(1).strip() if lang_match else "Unknown"
        
        # Extract stars today
        stars_today_match = re.search(r'(\d+(?:,\d+)*)\s*stars?\s*today', block, re.IGNORECASE)
        if stars_today_match:
            today_stars = stars_today_match.group(1).replace(',', '')
        else:
            # Try to find any star count
            alt_match = re.search(r'(\d+(?:,\d+)*)\s*\n?\s*stars?', block, re.IGNORECASE)
            today_stars = alt_match.group(1).replace(',', '') if alt_match else "0"
        
        # Extract total stars from stargazers link (with possible SVG)
        total_stars_match = re.search(r'href="[^"]*/stargazers"[^>]*>.*?(\d+(?:,\d+)*)\s*<', block, re.DOTALL)
        if total_stars_match:
            total_stars = total_stars_match.group(1).replace(',', '')
        else:
            # Try alternative method
            total_stars_match = re.search(r'href="[^"]*/stargazers"[^>]*>.*?(\d+(?:,\d+)*)', block, re.DOTALL)
            if total_stars_match:
                total_stars = total_stars_match.group(1).replace(',', '')
            else:
                total_stars = "0"
        
        return {
            'full_name': full_name,
            'name': full_name.split('/')[-1],
            'description': description,
            'language': language,
            'today_stars': today_stars,
            'total_stars': total_stars
        }
        
    except Exception as e:
        print(f"Error parsing repo block: {e}")
        return None


def clean_html(html_text: str) -> str:
    """Remove HTML tags and clean text"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_text)
    # Replace HTML entities
    text = text.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    # Normalize whitespace
    text = ' '.join(text.split())
    return text.strip()


def main():
    """Main entry point"""
    print(f"[{datetime.now().isoformat()}] Fetching GitHub trending data...")
    
    repos = fetch_github_trending()
    
    if repos:
        print(f"Successfully fetched {len(repos)} trending repositories")
        
        # Save to JSON file
        output_file = f"trending-data-{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(repos, f, ensure_ascii=False, indent=2)
        
        print(f"Data saved to {output_file}")
        
        # Print summary
        print("\nTop 10 Trending Repositories:")
        print("-" * 80)
        for i, repo in enumerate(repos[:10], 1):
            print(f"{i:2}. {repo['full_name'][:40]:40} | +{repo['today_stars']:>6} ⭐ | {repo['language'][:10]:10}")
        
        return repos
    else:
        print("Failed to fetch trending data")
        return []


if __name__ == "__main__":
    main()
