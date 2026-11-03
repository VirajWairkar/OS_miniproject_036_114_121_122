#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs
LOG="logs/exp1_system_health.txt"
{
  echo 'EXP 1 - PRE-DEPLOYMENT HEALTH CHECK - KJS-AGR-01'
  echo "Captured (system local): $(date -Is)"
  echo "User: $(whoami)"; echo "Working directory: $(pwd)"
  echo '--- OS and Kernel ---'; cat /etc/os-release | head -n 6; uname -a
  echo '--- CPU ---'; lscpu | grep -E 'Architecture:|CPU\(s\):|Model name:' | head -n 4
  echo '--- RAM ---'; free -h
  echo '--- Disk ---'; df -h .
  echo '--- Uptime and users ---'; uptime; who
  echo '--- Tools ---'
  for tool in bash python3 gcc g++ make; do
    if command -v "$tool" >/dev/null; then echo "$tool: $(command -v "$tool")"; else echo "$tool: NOT FOUND"; fi
  done
  echo '--- Environment/file/process basics ---'
  printenv HOME USER SHELL || true
  ls -ld . data src scripts
  ps -e -o pid,comm | head -n 8
} | tee "$LOG"
echo "Saved: $LOG"
