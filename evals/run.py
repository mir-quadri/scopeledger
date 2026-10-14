"""Run semantic evaluation against a real local model, never fixtures."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from core import analyze
p=argparse.ArgumentParser();p.add_argument('--model',default='gemma3:4b');p.add_argument('--output',default='evals/results.json');args=p.parse_args()
rows=[]
for case in json.loads(Path(__file__).with_name('cases.json').read_text()):
 try:
  a=analyze(case['scope'],case['requests'],model=args.model)
  actual=[r['status'] for r in a['items']]
  row={'name':case['name'],'expected':case['expected'],'actual':actual,'passed':actual==case['expected'],'analysis':a}
 except Exception as e:row={'name':case['name'],'expected':case['expected'],'passed':False,'error':str(e)}
 rows.append(row);print(row['name'],row['passed'],flush=True)
report={'model':args.model,'cases':len(rows),'passed':sum(r['passed'] for r in rows),'results':rows}
Path(args.output).write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='results'}))
sys.exit(0 if report['passed']==report['cases'] else 1)
