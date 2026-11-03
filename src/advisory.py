#!/usr/bin/env python3
"""Educational sugarcane irrigation classifier: KNN trained on synthetic labels.
This is not a calibrated agronomic recommendation system.
"""
import csv
import math
import sys
import json
from pathlib import Path

FEATURES = ('soil_moisture_pct', 'temperature_c', 'rainfall_forecast_mm', 'growth_stage')
REQUIRED = ('plot_id',) + FEATURES
STAGES = {'Germination':0, 'Tillering':1, 'Grand Growth':2, 'Maturity':3}
CLASS_NAMES = {0:'NO_IRRIGATION', 1:'MONITOR', 2:'IRRIGATION_REVIEW'}
DURATIONS = {0:0, 1:0, 2:20}  # Demonstration only; not field guidance.
TRAINING = Path('data/synthetic_training.csv')

def load_csv(path, training=False):
    path = Path(path)
    if not path.is_file():
        raise ValueError(f'Missing input file: {path}')
    with path.open(newline='',encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        required = list(REQUIRED) + (['label'] if training else [])
        missing = [x for x in required if x not in fields]
        if missing: raise ValueError('Missing CSV columns: ' + ', '.join(missing))
        rows=[]
        seen=set()
        for number,row in enumerate(reader,start=2):
            if None in row or any(v is None for v in row.values()):
                raise ValueError(f'Row {number}: incorrect column count')
            plot_id=(row['plot_id'] or '').strip()
            if not plot_id or any(c in plot_id for c in '\n\r\t'):
                raise ValueError(f'Row {number}: invalid plot_id')
            if plot_id in seen: raise ValueError(f'Row {number}: duplicate plot_id {plot_id}')
            seen.add(plot_id)
            try:
                moisture=float(row['soil_moisture_pct'])
                temp=float(row['temperature_c'])
                rain=float(row['rainfall_forecast_mm'])
            except (ValueError,TypeError):
                raise ValueError(f'Row {number}: expected numeric moisture, temperature, rainfall')
            stage = (row['growth_stage'] or '').strip()
            if stage not in STAGES: raise ValueError(f'Row {number}: invalid growth_stage {stage!r}')
            if not all(map(math.isfinite,(moisture,temp,rain))):
                raise ValueError(f'Row {number}: non-finite values not allowed')
            if not (0<=moisture<=100 and -5<=temp<=60 and 0<=rain<=250):
                raise ValueError(f'Row {number}: values out of range')
            entry={'plot_id':plot_id,'soil_moisture_pct':moisture,'temperature_c':temp,
                   'rainfall_forecast_mm':rain,'growth_stage':stage}
            if training:
                try: label=int(row['label'])
                except (ValueError,TypeError): raise ValueError(f'Row {number}: invalid label')
                if label not in (0,1,2): raise ValueError(f'Row {number}: label must be 0, 1 or 2')
                entry['label']=label
            rows.append(entry)
    if not rows: raise ValueError(f'Empty CSV: {path}')
    return rows

def vector(row):
    return [row['soil_moisture_pct']/100, (row['temperature_c']+5)/65,
            row['rainfall_forecast_mm']/100, STAGES[row['growth_stage']]/3]

def knn_predict(train,row,k=5):
    x=vector(row)
    # Heavier moisture/rainfall weighting in this synthetic proof-of-concept.
    weights=(2.0,0.4,1.8,0.2)
    distances=[]
    for t in train:
        a=vector(t)
        d=sum(w*(a[i]-x[i])**2 for i,w in enumerate(weights))
        distances.append((d,t['label']))
    neighbors=sorted(distances, key=lambda z:z[0])[:k]
    scores={0:0.0,1:0.0,2:0.0}
    for distance,label in neighbors: scores[label]+=1.0/(distance+0.0001)
    return max((0,1,2),key=lambda lab:(scores[lab],-lab))

def training_split(rows):
    # Fixed split by deterministic shuffle; no live data or external services.
    import random
    shuffled=rows[:]
    random.Random(42).shuffle(shuffled)
    n=max(1,int(len(shuffled)*0.2))
    return shuffled[n:],shuffled[:n]

def validate(input_path):
    data=load_csv(input_path)
    train=load_csv(TRAINING,training=True)
    if len(train)<6: raise ValueError('Not enough synthetic training records')
    print(f'[VALIDATE] {len(data)} plot readings; {len(train)} synthetic training rows; valid')

def predict(input_path,output_csv,metrics_path):
    data=load_csv(input_path)
    training=load_csv(TRAINING, training=True)
    train,holdout=training_split(training)
    correct=sum(knn_predict(train,row)==row['label'] for row in holdout)
    accuracy=round(correct/len(holdout),4)
    out=Path(output_csv); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f)
        writer.writerow(['plot_id','soil_moisture_pct','temperature_c','rainfall_forecast_mm',
                         'growth_stage','predicted_class','illustrative_duration_min','message'])
        for row in data:
            lab=knn_predict(training,row)
            message={0:'No irrigation flag in educational demo',
                     1:'Monitor and recheck sensor conditions',
                     2:'Review irrigation need with field expert'}[lab]
            writer.writerow([row['plot_id'],row['soil_moisture_pct'],row['temperature_c'],
                             row['rainfall_forecast_mm'],row['growth_stage'],CLASS_NAMES[lab],
                             DURATIONS[lab],message])
            print(f"  {row['plot_id']}: {CLASS_NAMES[lab]} - {message}")
    metrics={'model':'k-nearest neighbors (k=5), weighted distance, no external dependencies',
             'training_source':'entirely synthetic labels generated from illustrative heuristic',
             'holdout_size':len(holdout),'training_size':len(train),
             'holdout_accuracy':accuracy,'plots_processed':len(data),
             'disclaimer':'NOT agronomically validated; metrics only assess agreement with synthetic labels'}
    m=Path(metrics_path);m.parent.mkdir(parents=True,exist_ok=True)
    m.write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8')
    print(f'[PREDICT] Processed {len(data)} plots. Synthetic holdout accuracy: {accuracy:.1%}')

def report(pred_csv,report_path):
    rows=list(csv.DictReader(open(pred_csv,newline='',encoding='utf-8')))
    if not rows: raise ValueError('Empty prediction file')
    counts={name:sum(row['predicted_class']==name for row in rows) for name in CLASS_NAMES.values()}
    lines=['SMART IRRIGATION - EDUCATIONAL OS MINI-PROJECT','='*52,
           'KJS-AGR-01 | Sugarcane irrigation advisory proof-of-concept',
           'INPUT: synthetic sensor and weather observations',
           'METHOD: weighted k-nearest neighbors trained on SYNTHETIC labels',
           'WARNING: This output is NOT for field irrigation decisions.','',
           f'Plots processed: {len(rows)}']
    lines += [f'{name}: {count}' for name,count in counts.items()]
    lines += ['', 'PLOT-WISE OUTPUTS:']
    lines += [f"- {r['plot_id']}: {r['predicted_class']} | {r['message']}" for r in rows]
    target=Path(report_path);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'[REPORT] Wrote {target}')

def main():
    try:
        cmd=sys.argv[1]
        if cmd=='validate' and len(sys.argv)==3: validate(sys.argv[2])
        elif cmd=='predict' and len(sys.argv)==5: predict(*sys.argv[2:])
        elif cmd=='report' and len(sys.argv)==4: report(*sys.argv[2:])
        else: raise ValueError('Usage: advisory.py validate INPUT | predict INPUT OUTPUT_CSV METRICS_JSON | report PRED_CSV REPORT_TXT')
    except (ValueError, OSError, IndexError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);sys.exit(2)
if __name__=='__main__':main()
