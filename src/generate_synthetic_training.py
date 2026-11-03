#!/usr/bin/env python3
"""Reproduce 180 synthetic teaching examples (not real farm observations)."""
import csv
import random
from pathlib import Path
random.seed(42)
stages=['Germination','Tillering','Grand Growth','Maturity']
def label(moisture,temperature,rain):
    if rain>=18 or moisture>=64: return 0
    if moisture<=32 and rain<=8: return 2
    if moisture<=40 and rain<=5 and temperature>=33: return 2
    return 1
rows=[]
for i in range(180):
    m=round(random.uniform(12,85),1)
    t=round(random.uniform(23,41),1)
    r=round(random.uniform(0,35),1)
    s=random.choice(stages)
    rows.append([f'SYN-{i+1:03d}',m,t,r,s,label(m,t,r)])
output=Path(__file__).resolve().parents[1]/'data'/'synthetic_training.csv'
with output.open('w',newline='',encoding='utf-8') as f:
    writer=csv.writer(f)
    writer.writerow(['plot_id','soil_moisture_pct','temperature_c','rainfall_forecast_mm','growth_stage','label'])
    writer.writerows(rows)
print(f'Wrote {len(rows)} reproducible synthetic training rows to {output}')
