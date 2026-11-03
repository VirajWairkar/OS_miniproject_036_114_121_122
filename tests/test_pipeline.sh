#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
make all >/dev/null
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
say(){ printf '%s\n' "$*"; }
expect_failure(){
  local title="$1" input="$2"
  if ./build/os_pipeline "$input" "$TMP/out_$title" >"$TMP/$title.log" 2>&1; then
    echo "FAIL $title: program unexpectedly accepted invalid input"; exit 1
  fi
  say "PASS $title - rejected expected failure"
}
./build/os_pipeline data/sensor_readings.csv "$TMP/valid" > "$TMP/valid.log" 2>&1
[[ -s "$TMP/valid/predictions.csv" && -s "$TMP/valid/advisory_report.txt" && -s "$TMP/valid/metrics.json" ]]
say 'PASS valid dataset - prediction, report, and metrics produced'
expect_failure missing "$TMP/missing.csv"
printf 'plot_id,soil_moisture_pct,temperature_c,rainfall_forecast_mm,growth_stage\nINVALID,not_number,33,1,Tillering\n' > "$TMP/bad_numeric.csv"
expect_failure bad_numeric "$TMP/bad_numeric.csv"
printf 'plot_id,soil_moisture_pct,temperature_c,rainfall_forecast_mm,growth_stage\nOUTRANGE,105,33,1,Tillering\n' > "$TMP/out_of_range.csv"
expect_failure out_of_range "$TMP/out_of_range.csv"
printf 'plot_id,soil_moisture_pct,temperature_c,rainfall_forecast_mm,growth_stage\n' > "$TMP/empty_rows.csv"
expect_failure empty_rows "$TMP/empty_rows.csv"
say 'RESULT: 5/5 tests passed; these were run in this environment. Repeat in Ubuntu VirtualBox for your own evidence.'
