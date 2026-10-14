"""Zero-dependency loopback-only server. Python 3.10+."""
import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from core import analyze, review_analysis, export_markdown

ROOT = Path(__file__).parent
DB = Path(os.getenv('SCOPELEDGER_DB', str(Path.home()/'.scopeledger'/'ledger.sqlite3')))
MODEL_LOCK = threading.Lock()

def connect():
    DB.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    con = sqlite3.connect(DB, timeout=15)
    con.execute('CREATE TABLE IF NOT EXISTS analyses (id TEXT PRIMARY KEY, data TEXT NOT NULL)')
    con.execute('CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY, at TEXT, analysis_id TEXT, event TEXT)')
    con.commit()
    try: DB.chmod(0o600)
    except OSError: pass
    return con

def persist(a, event, create=False):
    with connect() as con:
        if create:
            con.execute('INSERT INTO analyses VALUES (?,?)', (a['id'], json.dumps(a)))
        else:
            con.execute('UPDATE analyses SET data=? WHERE id=?', (json.dumps(a), a['id']))
        con.execute('INSERT INTO events(at,analysis_id,event) VALUES (?,?,?)',
                    (datetime.now(timezone.utc).isoformat(), a['id'], event))

def load(ident):
    if not isinstance(ident, str) or len(ident) != 32:
        raise ValueError('Invalid review ID.')
    with connect() as con:
        row = con.execute('SELECT data FROM analyses WHERE id=?', (ident,)).fetchone()
    if not row: raise ValueError('Review not found.')
    return json.loads(row[0])

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass  # Never log source documents or generated results.
    def valid_host(self):
        return self.headers.get('Host') in {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
    def reply(self, status, body, content='application/json'):
        raw = body if isinstance(body,bytes) else json.dumps(body).encode()
        self.send_response(status)
        self.send_header('Content-Type', content+'; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        try:self.wfile.write(raw)
        except BrokenPipeError:pass
    def do_GET(self):
        if not self.valid_host(): return self.reply(403, {'error':'Loopback host required.'})
        path = urlparse(self.path).path
        if path=='/api/health':
            return self.reply(200, {'service':'ScopeLedger', 'model':os.getenv('SCOPELEDGER_MODEL','gemma3:4b'), 'storage':'local SQLite'})
        if path=='/api/history':
            with connect() as con:
                rows = con.execute('SELECT id,data FROM analyses ORDER BY rowid DESC LIMIT 20').fetchall()
            return self.reply(200, {'analyses':[{'id':i,'model':json.loads(d)['model'], 'mode':json.loads(d)['mode']} for i,d in rows]})
        if path.startswith('/api/analysis/'):
            try:return self.reply(200,load(path.rsplit('/',1)[1]))
            except ValueError as e:return self.reply(404,{'error':str(e)})
        files={'/':'index.html','/app.js':'app.js','/style.css':'style.css','/sample.json':'sample.json','/icon.svg':'icon.svg'}
        if path not in files: return self.reply(404, {'error':'Not found.'})
        fp=ROOT/'dist'/files[path]
        mime={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'}[fp.suffix]
        return self.reply(200,fp.read_bytes(),mime)
    def do_POST(self):
        if not self.valid_host():return self.reply(403,{'error':'Loopback host required.'})
        origin=self.headers.get('Origin')
        if origin != 'http://'+self.headers['Host']:
            return self.reply(403,{'error':'Same-origin browser request required.'})
        if self.headers.get('Content-Type','').split(';')[0] != 'application/json':
            return self.reply(415,{'error':'JSON required.'})
        try:
            length=int(self.headers.get('Content-Length',0))
            if length < 1 or length > 64000:raise ValueError('Request must be 1–64,000 bytes.')
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict):raise ValueError('JSON object required.')
            if self.path=='/api/analyze':
                if not MODEL_LOCK.acquire(blocking=False): return self.reply(429,{'error':'Another model review is running. Try again shortly.'})
                try:a=analyze(data.get('scope'),data.get('requests'))
                finally:MODEL_LOCK.release()
                a['id']=uuid.uuid4().hex
                persist(a,'analyzed',create=True)
                return self.reply(200,a)
            if self.path=='/api/review':
                a=load(data.get('id'))
                a['review']=review_analysis(a,data.get('review'))
                persist(a,'owner_reviewed')
                return self.reply(200,a)
            if self.path=='/api/export':
                a=load(data.get('id'))
                text=export_markdown(a)
                persist(a,'draft_exported')
                return self.reply(200,{'markdown':text})
            if self.path=='/api/delete':
                a=load(data.get('id'))
                with connect() as con:
                    con.execute('DELETE FROM events WHERE analysis_id=?',(a['id'],))
                    con.execute('DELETE FROM analyses WHERE id=?',(a['id'],))
                return self.reply(200,{'deleted':True})
            return self.reply(404,{'error':'Not found.'})
        except (ValueError,TypeError) as e:return self.reply(400,{'error':str(e)})
        except RuntimeError as e:return self.reply(503,{'error':str(e)})
        except Exception:return self.reply(500,{'error':'Review failed. Retry; no draft was sent.'})

if __name__=='__main__':
    port=int(os.getenv('PORT','8765'))
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    print(f'ScopeLedger → http://127.0.0.1:{port} (Ctrl+C to stop)',flush=True)
    server.serve_forever()
