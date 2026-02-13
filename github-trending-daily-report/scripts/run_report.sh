#!/bin/bash
# GitHub Trending Report Runner
# Usage: ./run_report.sh
# Env: GITHUB_TOKEN (optional, for higher API rate limits)

set -e

echo "=========================================="
echo "GitHub Trending Report Generator"
echo "Started at: $(date)"
echo "=========================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed"
    exit 1
fi

# Step 1: Fetch trending data with enrichment
echo "Step 1: Fetching GitHub trending data with enrichment..."
if [ -n "$GITHUB_TOKEN" ]; then
    echo "  Using GitHub token for API access (higher rate limits)"
    python3 fetch_trending.py --github-token "$GITHUB_TOKEN"
else
    echo "  No GITHUB_TOKEN set, using unauthenticated API (60 req/hour limit)"
    echo "  Tip: export GITHUB_TOKEN=your_token for better rate limits"
    python3 fetch_trending.py
fi

# Check if we got data
LATEST_JSON=$(ls -t trending-data-*.json 2>/dev/null | head -1)
if [ -z "$LATEST_JSON" ]; then
    echo "Error: No trending data file found"
    exit 1
fi

echo ""
echo "Data saved to: $LATEST_JSON"

# Step 2: Verify enrichment
echo ""
echo "Step 2: Verifying enrichment data..."
python3 -c "
import json
data = json.load(open('$LATEST_JSON'))
total = len(data)
enriched = sum(1 for r in data if r.get('readme_content'))
with_meta = sum(1 for r in data if r.get('metadata'))
print(f'  Total repos: {total}')
print(f'  With metadata: {with_meta}/{total}')
print(f'  With README: {enriched}/{total}')
if enriched < total:
    missing = [r['full_name'] for r in data if not r.get('readme_content')]
    print(f'  Missing README: {', '.join(missing[:5])}')
"

# Step 3: Generate the markdown skeleton report
echo ""
echo "Step 3: Generating skeleton markdown report..."
python3 generate_report.py

# Find the generated report
TODAY=$(date +%Y-%m-%d)
REPORT_FILE="github-trending-report-${TODAY}.md"

if [ -f "$REPORT_FILE" ]; then
    LINES=$(wc -l < "$REPORT_FILE")
    PLACEHOLDERS=$(grep -c "DEEP_ANALYSIS:" "$REPORT_FILE" 2>/dev/null || echo "0")
    echo ""
    echo "=========================================="
    echo "Skeleton report generated successfully!"
    echo "File: $REPORT_FILE"
    echo "Full path: $(pwd)/$REPORT_FILE"
    echo "Lines: $LINES"
    echo "Placeholders for deep analysis: $PLACEHOLDERS"
    echo "=========================================="
    echo ""
    echo "Next step: Use the Claude Code skill to fill in deep analysis:"
    echo "  /github-trending-daily-report"
    echo ""
    echo "This will:"
    echo "  - Analyze each repo's README and metadata"
    echo "  - Generate technical architecture analysis"
    echo "  - Write core features and application directions"
    echo "  - Create dynamic trend summary and investment analysis"
    echo "  - Target: 1000-1500 lines deep analysis report"
else
    echo "Warning: Could not find generated report file"
fi

echo ""
echo "Finished at: $(date)"
