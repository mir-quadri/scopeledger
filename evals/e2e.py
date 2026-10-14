"""Real-model API-to-export check. Run with Ollama running; uses an ephemeral DB."""
import json,sys,tempfile,threading,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
import server
sample=json.loads((Path(__file__).parents[1]/'dist/sample.json').read_text())
with tempfile.TemporaryDirectory() as d:
 server.DB=Path(d)/'ledger.sqlite3'
 http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
 thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
 base=f'http://127.0.0.1:{http.server_port}'
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 def post(path,data):
  req=urllib.request.Request(base+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','Origin':base})
  with opener.open(req,timeout=240) as r:return json.loads(r.read())
 try:
  a=post('/api/analyze',{'scope':sample['scope'],'requests':sample['requests']})
  assert a['mode']=='live' and len(a['items'])==4
  # Explicit owner decisions, not a claim that the model made these decisions.
  ds=[{'request_id':f'R{i+1}','status':s,'hours':h,'approved':ok} for i,(s,h,ok) in enumerate([('change',3,True),('included',0,False),('change',2,True),('clarify',0,False)])]
  reviewed=post('/api/review',{'id':a['id'],'review':{'rate':100,'decisions':ds}})
  assert reviewed['review']['total_cents']==50000
  exported=post('/api/export',{'id':a['id']})['markdown']
  assert 'USD 500.00' in exported and 'Please adjust the homepage colors' not in exported
  deleted=post('/api/delete',{'id':a['id']});assert deleted['deleted']
  output={'model':a['model'],'mode':'live','analysis':a,'owner_review':reviewed['review'],'markdown':exported,'deleted':True}
  (Path(__file__).parent/'e2e-result.json').write_text(json.dumps(output,indent=2))
  print('Real-model API → local database → owner review → $500 draft → deletion: passed.',flush=True)
 finally:http.shutdown();http.server_close();thread.join()
