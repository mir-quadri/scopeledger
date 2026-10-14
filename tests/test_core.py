import copy,json,sys,unittest,tempfile,threading,urllib.request,urllib.error
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from core import analyze,validate,lines,review_analysis,export_markdown,source_hash
import server
S='Build a contact form.\nBooking is excluded.'
R='Please add booking.\nPlease add a contact form.'
P={'items':[{'request_id':'R1','status':'change','scope_ids':['S2'],'reason':'Booking is excluded.'},{'request_id':'R2','status':'included','scope_ids':['S1'],'reason':'A contact form is included.'}]}
def fake(body):return {'message':{'content':json.dumps(P)},'eval_count':45}
def example():return dict(analyze(S,R,transport=fake),id='a'*32)
def review():return {'rate':'100.25','decisions':[{'request_id':'R1','status':'change','hours':'2.5','approved':True},{'request_id':'R2','status':'included','hours':0,'approved':False}]}
class CoreTests(unittest.TestCase):
 def test_exact_sources_and_order(self):
  a=example();self.assertEqual(a['items'][0]['request_quote'],'Please add booking.');self.assertEqual(a['items'][0]['scope_quotes'],[{'id':'S2','text':'Booking is excluded.'}])
 def test_missing_request(self):
  p=copy.deepcopy(P);p['items'].pop()
  with self.assertRaises(ValueError):validate(p,lines(S,'S'),lines(R,'R'))
 def test_duplicate_request(self):
  p=copy.deepcopy(P);p['items'][1]['request_id']='R1'
  with self.assertRaises(ValueError):validate(p,lines(S,'S'),lines(R,'R'))
 def test_fabricated_citation(self):
  p=copy.deepcopy(P);p['items'][0]['scope_ids']=['S99']
  with self.assertRaises(ValueError):validate(p,lines(S,'S'),lines(R,'R'))
 def test_included_needs_citation(self):
  p=copy.deepcopy(P);p['items'][1]['scope_ids']=[]
  with self.assertRaises(ValueError):validate(p,lines(S,'S'),lines(R,'R'))
 def test_schema_extra_fields(self):
  p=copy.deepcopy(P);p['items'][0]['price']=500
  with self.assertRaises(ValueError):validate(p,lines(S,'S'),lines(R,'R'))
 def test_model_invalid_json(self):
  with self.assertRaises(ValueError):analyze(S,R,transport=lambda _: {'message':{'content':'oops'}})
 def test_no_export_without_review(self):
  with self.assertRaises(ValueError):export_markdown(example())
 def test_decimal_money(self):
  r=review_analysis(example(),review());self.assertEqual(r['total_cents'],25063)
 def test_clarification_cannot_be_approved(self):
  r=review();r['decisions'][0]['status']='clarify'
  with self.assertRaises(ValueError):review_analysis(example(),r)
 def test_zero_hours_cannot_be_approved(self):
  r=review();r['decisions'][0]['hours']=0
  with self.assertRaises(ValueError):review_analysis(example(),r)
 def test_invalid_hours(self):
  for hours in ['NaN','-1','Infinity','0.1',True,{},1001]:
   with self.subTest(hours=hours):
    r=review();r['decisions'][0]['hours']=hours
    with self.assertRaises(ValueError):review_analysis(example(),r)
 def test_invalid_rates(self):
  for rate in ['NaN',0,-1,10001,'1.001',True,{}]:
   with self.subTest(rate=rate):
    r=review();r['rate']=rate
    with self.assertRaises(ValueError):review_analysis(example(),r)
 def test_duplicate_owner_decision(self):
  r=review();r['decisions'][1]['request_id']='R1'
  with self.assertRaises(ValueError):review_analysis(example(),r)
 def test_unapproved_items_excluded(self):
  a=example();a['review']=review_analysis(a,review());text=export_markdown(a)
  self.assertIn('USD 250.63',text);self.assertIn('Please add booking.',text);self.assertNotIn('Please add a contact form.',text);self.assertIn('acceptance is pending',text)
 def test_hash_changes(self):self.assertNotEqual(source_hash(S,R),source_hash(S,R+'!'))
 def test_empty_and_oversize(self):
  for value in ['',None,'x'*12001,'\n'.join(['x']*31)]:
   with self.assertRaises(ValueError):lines(value,'S')
 def test_schema_and_untrusted_prompt_sent(self):
  def transport(body):
   self.assertEqual(body['format']['type'],'object');self.assertIn('UNTRUSTED',body['messages'][0]['content']);return fake(body)
  analyze(S,R,transport=transport)
class HTTPTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();server.DB=Path(cls.tmp.name)/'test.db';cls.original=server.analyze;server.analyze=lambda s,r:analyze(s,r,transport=fake)
  cls.http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start();cls.base='http://127.0.0.1:'+str(cls.http.server_port)
 @classmethod
 def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.thread.join();server.analyze=cls.original;cls.tmp.cleanup()
 def req(self,path,data=None,origin=True,host=None):
  headers={}
  if data is not None:headers={'Content-Type':'application/json','Origin':self.base if origin else 'https://evil.example'}
  if host:headers['Host']=host
  r=urllib.request.Request(self.base+path,data=json.dumps(data).encode() if data is not None else None,headers=headers)
  with urllib.request.urlopen(r) as out:return json.loads(out.read())
 def test_flow_persistence_and_delete(self):
  a=self.req('/api/analyze',{'scope':S,'requests':R});ident=a['id'];self.assertEqual(self.req('/api/analysis/'+ident)['source_hash'],a['source_hash'])
  with self.assertRaises(urllib.error.HTTPError) as e:self.req('/api/export',{'id':ident})
  self.assertEqual(e.exception.code,400)
  reviewed=self.req('/api/review',{'id':ident,'review':review()});self.assertEqual(reviewed['review']['total_cents'],25063)
  self.assertIn('USD 250.63',self.req('/api/export',{'id':ident})['markdown'])
  self.assertTrue(self.req('/api/delete',{'id':ident})['deleted'])
  with self.assertRaises(urllib.error.HTTPError):self.req('/api/analysis/'+ident)
 def test_cross_origin_rejected(self):
  with self.assertRaises(urllib.error.HTTPError) as e:self.req('/api/analyze',{'scope':S,'requests':R},origin=False)
  self.assertEqual(e.exception.code,403)
 def test_dns_rebinding_host_rejected(self):
  with self.assertRaises(urllib.error.HTTPError) as e:self.req('/api/health',host='evil.example')
  self.assertEqual(e.exception.code,403)
 def test_non_object_json_rejected(self):
  with self.assertRaises(urllib.error.HTTPError) as e:self.req('/api/analyze',[])
  self.assertEqual(e.exception.code,400)
 def test_static_sample_is_valid_json(self):
  sample=self.req('/sample.json');self.assertEqual(sample['analysis']['mode'],'sample')
if __name__=='__main__':unittest.main(verbosity=2)
