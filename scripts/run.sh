#!/usr/bin/env bash
# Exp 5: validates, backs up, compiles, runs workflow, and records logs.
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
INPUT="${1:-data/sensor_readings.csv}"
mkdir -p logs backups outputs build
RUN_ID="$(date -u +'%Y%m%dT%H%M%SZ')_$$"
LOG="logs/run_${RUN_ID}.log"
log(){ printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }
fail(){ log "ERROR: $*"; exit 2; }
trap 'code=$?; if [[ $code -ne 0 ]]; then log "FAILED with exit code $code"; fi' EXIT
command -v python3 >/dev/null || fail 'python3 not installed'
command -v g++ >/dev/null || fail 'g++ not installed'
[[ -f "$INPUT" ]] || fail "Input CSV missing: $INPUT"
[[ -s "$INPUT" ]] || fail "Input CSV is empty: $INPUT"
log "SMART IRRIGATION - EXP 5 SHELL AUTOMATION"
log "Input: $INPUT"
# Do not back up synthetic training here, which is already versioned; back up the readings.
cp -- "$INPUT" "backups/sensor_${RUN_ID}.csv"
log "Backup stored: backups/sensor_${RUN_ID}.csv"
log "Input line count: $(wc -l < "$INPUT")"
log "Checking data with validation stage..."
python3 src/advisory.py validate "$INPUT" 2>&1 | tee -a "$LOG"
log "Compiling Exp 4 system-call program..."
make all 2>&1 | tee -a "$LOG"
log "Running the 3-stage OS pipeline..."
./build/os_pipeline "$INPUT" outputs 2>&1 | tee -a "$LOG"
log "Outputs: outputs/predictions.csv, outputs/advisory_report.txt, outputs/metrics.json, outputs/os_execution_summary.txt"
log 'SUCCESS - view outputs with cat and inspect logs for proof of execution.'
