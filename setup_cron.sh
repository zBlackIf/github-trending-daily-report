#!/bin/bash
# Setup cron job for daily GitHub Trending reports at 9:00 AM

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNNER_SCRIPT="$SCRIPT_DIR/run_report.sh"

# Check if runner script exists
if [ ! -f "$RUNNER_SCRIPT" ]; then
    echo "Error: run_report.sh not found at $RUNNER_SCRIPT"
    exit 1
fi

# Make sure scripts are executable
chmod +x "$RUNNER_SCRIPT"
chmod +x "$SCRIPT_DIR/fetch_trending.py"
chmod +x "$SCRIPT_DIR/generate_report.py"

# Create cron job entry
# Run at 9:00 AM every day
CRON_JOB="0 9 * * * cd $SCRIPT_DIR && /bin/bash $RUNNER_SCRIPT >> $SCRIPT_DIR/cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -F "$RUNNER_SCRIPT" > /dev/null; then
    echo "Cron job already exists. Updating..."
    crontab -l 2>/dev/null | grep -v -F "$RUNNER_SCRIPT" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job set up successfully!"
echo ""
echo "Schedule: Every day at 9:00 AM"
echo "Script: $RUNNER_SCRIPT"
echo "Log file: $SCRIPT_DIR/cron.log"
echo ""
echo "To verify the cron job:"
echo "  crontab -l"
echo ""
echo "To remove the cron job:"
echo "  crontab -l | grep -v 'run_report.sh' | crontab -"
echo ""
echo "To run the report manually:"
echo "  $RUNNER_SCRIPT"
