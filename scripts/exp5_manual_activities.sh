#!/usr/bin/env bash
# Manual questions Q1-Q6 + irrigation-linked follow-up for the shell experiment.
set -euo pipefail
x=10; echo "Q1: x=$x"
xn='Rani'; echo "Q2: xn=$xn"
name='Viraj Wairkar'; echo "Q3: Name=$name; Shell=$SHELL; OS=$OSTYPE; Date=$(date)"
if command -v cal >/dev/null; then cal; else echo 'Install ncal for calendar command'; fi
printf '\nQ4: Student data\n'
printf '%s\t%s\t%s\n' Name Roll TotalMarks 'Aarav' '101' '450' 'Riya' '102' '465' 'Rahul' '103' '440'
a=20; b=6
printf '\nQ5: arithmetic: +%d -%d *%d /%d %% %d\n' "$((a+b))" "$((a-b))" "$((a*b))" "$((a/b))" "$((a%b))"
seconds=3665
printf 'Q6: %d seconds => %d hours, %d minutes\n' "$seconds" "$((seconds/3600))" "$(((seconds%3600)/60))"
echo 'Use-case integration: run scripts/run.sh to validate and launch irrigation workflow.'
