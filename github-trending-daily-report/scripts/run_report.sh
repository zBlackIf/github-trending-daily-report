#!/bin/bash
# GitHub Trending Report Runner
# Usage: ./run_report.sh

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

# Fetch trending data
echo "Step 1: Fetching GitHub trending data..."
python3 fetch_trending.py

# Check if we got data
LATEST_JSON=$(ls -t trending-data-*.json 2>/dev/null | head -1)
if [ -z "$LATEST_JSON" ]; then
    echo "Error: No trending data file found"
    exit 1
fi

echo "Data saved to: $LATEST_JSON"
echo ""

# Generate the markdown report
echo "Step 2: Generating markdown report..."
python3 generate_report.py

# Find the generated report
TODAY=$(date +%Y-%m-%d)
REPORT_FILE="github-trending-report-${TODAY}.md"

if [ -f "$REPORT_FILE" ]; then
    echo ""
    echo "=========================================="
    echo "Report generated successfully!"
    echo "File: $REPORT_FILE"
    echo "Full path: $(pwd)/$REPORT_FILE"
    echo "=========================================="
else
    echo "Warning: Could not find generated report file"
fi

echo ""
echo "Finished at: $(date)"
