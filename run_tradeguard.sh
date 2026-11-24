#!/bin/bash

PROJECT_DIR="/home/justi/tradeguard"
cd "$PROJECT_DIR" || exit 1

echo "[$(date)] Starting TradeGuard check..." >> logs/cron.log
"$PROJECT_DIR/venv/bin/python" main.py --scenario normal >> logs/cron.log 2>&1
echo "[$(date)] Completed TradeGuard check." >> logs/cron.log
