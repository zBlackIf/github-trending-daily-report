---
name: github-trending-daily-report
description: Generate deep analysis reports for GitHub Trending repositories, providing insights on trending popularity, technical implementations, frameworks, and potential application directions. Use when user needs automated daily GitHub Trending analysis, reports on trending repositories with technical deep dives, insights into emerging technology trends, or daily scheduled reports for monitoring GitHub ecosystem changes.
---

# GitHub Trending Daily Report

Generate comprehensive deep analysis reports for GitHub Trending repositories, scheduled daily at 9 AM for the past 24 hours of trending data.

## Quick Start

To generate a complete GitHub Trending daily report:

1. Fetch trending data from https://github.com/t/trending
2. Parse and extract repository information (name, stars, description, language)
3. Generate markdown report with deep analysis for each trending repository
4. Analyze technical trends, frameworks, and potential applications
5. Save report as `github-trending-report-YYYY-MM-DD.md`

## Workflow

### Step 1: Fetch GitHub Trending Data

Use `scripts/fetch_trending.py` to fetch the latest trending repositories:

```bash
python3 scripts/fetch_trending.py
```

This script:
- Fetches HTML from https://github.com/trending
- Parses repository information (name, description, language, stars)
- Saves data to `trending-data-YYYY-MM-DD.json`
- Limits to top 20 repositories

**Output format:** JSON array with each repository containing:
- `full_name`: owner/repo
- `name`: repository name
- `description`: repository description
- `language`: primary programming language
- `today_stars`: stars gained today
- `total_stars`: total star count

### Step 2: Generate Analysis Report

Use `scripts/generate_report.py` to create the markdown analysis:

```bash
python3 scripts/generate_report.py
```

This script:
- Reads latest `trending-data-*.json` file
- Generates comprehensive markdown report
- Saves as `github-trending-report-YYYY-MM-DD.md`

### Step 3: Enhance with Deep Analysis

For each trending repository, add the following analysis sections:

**Technical Principles & Implementation:**
- Core architecture and design patterns
- Key technologies and frameworks used
- Implementation details and innovations

**Core Features:**
- Main capabilities and functionality
- Unique selling points
- Integration options

**Potential Application Directions:**
- Real-world use cases
- Industry applications
- Market opportunities
- Future potential

### Step 4: Trend Summary & Insights

Add analysis sections covering:

**Current Technology Trends:**
- Identify patterns across trending repositories
- Highlight emerging technologies
- Note industry shifts

**Investment Suggestions & Risk Warnings:**
- Technologies worth watching
- Potential market opportunities
- Risks and concerns

## Report Structure

The generated markdown report includes:

1. **Header**: Report date, analysis scope, data source
2. **Executive Summary**: Total repositories analyzed, overview table
3. **Technical Domain Distribution**: Categorized by technology area
4. **Deep Analysis**: Individual repository analysis with:
   - Repository name and URL
   - Star counts (today/total)
   - Primary language
   - Project description
   - Technical principles
   - Core features
   - Potential applications
5. **Trend Summary & Insights**: Technology trends and recommendations

## Scheduling for Daily Execution

Use cron to schedule daily 9 AM execution:

```bash
# Edit crontab
crontab -e

# Add daily 9 AM cron job
0 9 * * * cd /path/to/github-trending-report && ./run_report.sh >> logs/report.log 2>&1
```

The `run_report.sh` script executes both steps sequentially.

## Resources

### scripts/

- `fetch_trending.py`: Fetches and parses GitHub trending HTML data
- `generate_report.py`: Generates comprehensive markdown analysis report
- `run_report.sh`: Shell script to execute full report generation pipeline

### references/

- `report_template.md`: Sample report format for reference
