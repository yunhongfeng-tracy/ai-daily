#!/usr/bin/env bash
set -e
cd /root/.openclaw/workspace/ai-daily
UPDATE_TRIGGER=manual bash test-cron.sh
