#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs exp2_workspace
LOG="logs/exp2_file_commands.txt"
{
  echo 'EXP 2 - LINUX FILE SYSTEM COMMANDS: IRRIGATION EXAMPLE'
  echo "Date: $(date -Is)"
  echo '--- Directory structure ---'
  mkdir -p data outputs logs backups exp2_workspace
  pwd; ls -ld data outputs logs backups exp2_workspace
  echo '--- File handling commands ---'
  cp data/sensor_readings.csv exp2_workspace/sensor_copy.csv
  touch exp2_workspace/notes.tmp
  echo 'Demo sensor file backup' > exp2_workspace/notes.tmp
  mv exp2_workspace/notes.tmp exp2_workspace/notes.txt
  cat exp2_workspace/notes.txt
  echo '--- Search and record count ---'
  find data -maxdepth 1 -name '*.csv' -print
  grep -n 'PLOT' exp2_workspace/sensor_copy.csv || true
  wc -l exp2_workspace/sensor_copy.csv
  echo '--- Restrict permissions (sample record only) ---'
  chmod 640 exp2_workspace/sensor_copy.csv
  ls -l exp2_workspace/sensor_copy.csv
  echo '--- Delete a temporary file and remove an empty directory ---'
  mkdir -p exp2_workspace/remove_me
  touch exp2_workspace/delete_me.tmp
  rm exp2_workspace/delete_me.tmp
  rmdir exp2_workspace/remove_me
  echo '--- Final tree ---'
  find exp2_workspace -maxdepth 2 -print
} | tee "$LOG"
echo "Saved: $LOG"
