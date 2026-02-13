#!/usr/bin/env python3
"""
GitHub Trending Data Fetcher
Fetches and parses GitHub trending repositories with enriched data
(README, metadata, dependency manifests) for deep analysis.
"""

import requests
import re
import json
import os
import time
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional


# GitHub API base URL
GITHUB_API = "https://api.github.com"
RAW_GITHUB = "https://raw.githubusercontent.com"

# README filename candidates (in priority order)
README_CANDIDATES = ["README.md", "readme.md", "Readme.md", "README.rst", "README.txt", "README"]

# Manifest files by language
MANIFEST_FILES = {
    "Python": ["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt"],
    "JavaScript": ["package.json"],
    "TypeScript": ["package.json"],
    "Rust": ["Cargo.toml"],
    "Go": ["go.mod"],
    "Java": ["pom.xml", "build.gradle"],
    "C#": ["*.csproj"],  # will be handled specially
    "Ruby": ["Gemfile"],
    "PHP": ["composer.json"],
    "Swift": ["Package.swift"],
    "Kotlin": ["build.gradle.kts", "build.gradle"],
    "C++": ["CMakeLists.txt"],
    "C": ["CMakeLists.txt", "Makefile"],
}

# Max content lengths
MAX_README_LENGTH = 10000
MAX_MANIFEST_LENGTH = 5000


def get_github_headers(token: Optional[str] = None) -> dict:
    """Get HTTP headers for GitHub API requests."""
    headers = {
        "User-Agent": "GitHub-Trending-Report/1.0",
        "Accept": "application/vnd.github.v3+json",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def get_web_headers() -> dict:
    """Get HTTP headers for web scraping requests."""
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }


def fetch_github_trending() -> List[Dict[str, Any]]:
    """Fetch trending repositories from GitHub."""
    try:
        response = requests.get(
            "https://github.com/trending",
            headers=get_web_headers(),
            timeout=30,
        )
        response.raise_for_status()
        return parse_trending_html(response.text)
    except Exception as e:
        print(f"Error fetching GitHub trending: {e}")
        return []


def parse_trending_html(html: str) -> List[Dict[str, Any]]:
    """Parse HTML to extract trending repository information."""
    repos = []
    repo_pattern = r'<article[^>]*class="[^"]*Box-row[^"]*"[^>]*>(.*?)</article>'
    repo_blocks = re.findall(repo_pattern, html, re.DOTALL)

    for block in repo_blocks[:20]:
        repo_info = parse_repo_block(block)
        if repo_info:
            repos.append(repo_info)

    return repos


def parse_repo_block(block: str) -> Optional[Dict[str, Any]]:
    """Parse a single repository block from trending HTML."""
    try:
        # Extract repository name
        name_match = re.search(r'<h2[^>]*>\s*<a[^>]*href="/([^"]+)"', block)
        if not name_match:
            return None

        full_name = name_match.group(1).strip()

        # Extract description
        desc_match = re.search(
            r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>', block, re.DOTALL
        )
        description = clean_html(desc_match.group(1)) if desc_match else "No description"

        # Extract language
        lang_match = re.search(
            r'<span[^>]*itemprop="programmingLanguage"[^>]*>(.*?)</span>', block
        )
        language = lang_match.group(1).strip() if lang_match else "Unknown"

        # Extract stars today
        stars_today_match = re.search(
            r'(\d+(?:,\d+)*)\s*stars?\s*today', block, re.IGNORECASE
        )
        if stars_today_match:
            today_stars = stars_today_match.group(1).replace(",", "")
        else:
            alt_match = re.search(
                r'(\d+(?:,\d+)*)\s*\n?\s*stars?', block, re.IGNORECASE
            )
            today_stars = alt_match.group(1).replace(",", "") if alt_match else "0"

        # Extract total stars
        total_stars_match = re.search(
            r'href="[^"]*/stargazers"[^>]*>.*?(\d+(?:,\d+)*)\s*<', block, re.DOTALL
        )
        if total_stars_match:
            total_stars = total_stars_match.group(1).replace(",", "")
        else:
            total_stars_match = re.search(
                r'href="[^"]*/stargazers"[^>]*>.*?(\d+(?:,\d+)*)', block, re.DOTALL
            )
            total_stars = (
                total_stars_match.group(1).replace(",", "")
                if total_stars_match
                else "0"
            )

        return {
            "full_name": full_name,
            "name": full_name.split("/")[-1],
            "description": description,
            "language": language,
            "today_stars": today_stars,
            "total_stars": total_stars,
        }

    except Exception as e:
        print(f"Error parsing repo block: {e}")
        return None


def clean_html(html_text: str) -> str:
    """Remove HTML tags and clean text."""
    text = re.sub(r"<[^>]+>", "", html_text)
    text = (
        text.replace("&quot;", '"')
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
    )
    text = " ".join(text.split())
    return text.strip()


def fetch_repo_metadata(
    full_name: str, token: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Fetch repository metadata from GitHub API.

    Returns topics, license, forks, open issues, dates, homepage, default branch.
    """
    try:
        url = f"{GITHUB_API}/repos/{full_name}"
        response = requests.get(url, headers=get_github_headers(token), timeout=15)
        response.raise_for_status()
        data = response.json()

        return {
            "topics": data.get("topics", []),
            "license": (
                data.get("license", {}).get("spdx_id", "Unknown")
                if data.get("license")
                else "Unknown"
            ),
            "forks": data.get("forks_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "created_at": (
                data.get("created_at", "")[:10] if data.get("created_at") else ""
            ),
            "updated_at": (
                data.get("updated_at", "")[:10] if data.get("updated_at") else ""
            ),
            "homepage": data.get("homepage", ""),
            "default_branch": data.get("default_branch", "main"),
            "size_kb": data.get("size", 0),
            "watchers": data.get("subscribers_count", 0),
            "archived": data.get("archived", False),
        }
    except Exception as e:
        print(f"  Warning: Failed to fetch metadata for {full_name}: {e}")
        return None


def fetch_repo_readme(
    full_name: str,
    default_branch: str = "main",
    token: Optional[str] = None,
) -> Optional[str]:
    """Fetch README content from the repository.

    Tries multiple README filename candidates. Returns truncated content.
    """
    for readme_name in README_CANDIDATES:
        try:
            url = f"{RAW_GITHUB}/{full_name}/{default_branch}/{readme_name}"
            response = requests.get(
                url, headers=get_web_headers(), timeout=15
            )
            if response.status_code == 200:
                content = response.text[:MAX_README_LENGTH]
                return content
        except Exception:
            continue

    print(f"  Warning: No README found for {full_name}")
    return None


def fetch_dependency_info(
    full_name: str,
    language: str,
    default_branch: str = "main",
    token: Optional[str] = None,
) -> Optional[str]:
    """Fetch dependency manifest file based on project language.

    Returns the content of package.json, pyproject.toml, Cargo.toml, etc.
    """
    candidates = MANIFEST_FILES.get(language, [])
    if not candidates:
        return None

    for manifest_name in candidates:
        # Skip glob patterns like *.csproj
        if "*" in manifest_name:
            continue
        try:
            url = f"{RAW_GITHUB}/{full_name}/{default_branch}/{manifest_name}"
            response = requests.get(
                url, headers=get_web_headers(), timeout=15
            )
            if response.status_code == 200:
                content = response.text[:MAX_MANIFEST_LENGTH]
                return content
        except Exception:
            continue

    return None


def enrich_repo(
    repo: Dict[str, Any],
    token: Optional[str] = None,
    delay: float = 1.0,
) -> Dict[str, Any]:
    """Enrich a single repo dict with metadata, README, and manifest content."""
    full_name = repo["full_name"]
    language = repo.get("language", "Unknown")
    errors = []

    print(f"  Enriching {full_name}...")

    # 1. Fetch metadata
    time.sleep(delay)
    metadata = fetch_repo_metadata(full_name, token)
    if metadata:
        repo["metadata"] = metadata
        default_branch = metadata.get("default_branch", "main")
    else:
        errors.append("metadata_fetch_failed")
        default_branch = "main"

    # 2. Fetch README
    time.sleep(delay)
    readme = fetch_repo_readme(full_name, default_branch, token)
    if readme:
        repo["readme_content"] = readme
    else:
        errors.append("readme_fetch_failed")

    # 3. Fetch dependency manifest
    time.sleep(delay)
    manifest = fetch_dependency_info(full_name, language, default_branch, token)
    if manifest:
        repo["manifest_content"] = manifest
    # Not an error if no manifest found - many repos don't have one at root

    if errors:
        repo["_fetch_errors"] = errors

    return repo


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fetch GitHub Trending data")
    parser.add_argument(
        "--skip-enrichment",
        action="store_true",
        help="Skip fetching README, metadata, and manifests (fast mode)",
    )
    parser.add_argument(
        "--github-token",
        type=str,
        default=None,
        help="GitHub personal access token for higher API rate limits",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay in seconds between API calls (default: 1.0)",
    )
    args = parser.parse_args()

    # Token from arg or environment
    token = args.github_token or os.environ.get("GITHUB_TOKEN")

    print(f"[{datetime.now().isoformat()}] Fetching GitHub trending data...")

    repos = fetch_github_trending()

    if not repos:
        print("Failed to fetch trending data")
        return []

    print(f"Successfully fetched {len(repos)} trending repositories")

    # Enrich repos with metadata, README, and manifest
    if not args.skip_enrichment:
        print(f"\nEnriching repository data (token: {'yes' if token else 'no'})...")
        for repo in repos:
            enrich_repo(repo, token=token, delay=args.delay)

        enriched_count = sum(1 for r in repos if r.get("readme_content"))
        print(f"\nEnrichment complete: {enriched_count}/{len(repos)} repos have README data")
    else:
        print("Skipping enrichment (--skip-enrichment flag)")

    # Save to JSON file
    output_file = f"trending-data-{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(repos, f, ensure_ascii=False, indent=2)

    print(f"\nData saved to {output_file}")

    # Print summary
    print("\nTop 10 Trending Repositories:")
    print("-" * 80)
    for i, repo in enumerate(repos[:10], 1):
        print(
            f"{i:2}. {repo['full_name'][:40]:40} | +{repo['today_stars']:>6} ⭐ | {repo['language'][:10]:10}"
        )

    return repos


if __name__ == "__main__":
    main()
