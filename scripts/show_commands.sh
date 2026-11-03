#!/usr/bin/env bash
# Optional reference commands, safe to run; screenshots must be made by student in VM.
set -euo pipefail
cd "$(dirname "$0")/.."
echo 'OS COMMAND EVIDENCE'
whoami; pwd; uname -r; ls -la; ps -e -o pid,comm | head -n 12
printf '\nProjects and logs:\n'; find outputs logs -maxdepth 1 -type f -print | head -n 30
printf '\nOutput record count:\n'; wc -l outputs/predictions.csv
printf '\nProcess info from saved run:\n'; cat outputs/os_execution_summary.txt
