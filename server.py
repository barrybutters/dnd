"""Ember Table: local-only server. Python 3.10+, no installation required."""
import sys, json, io, re, os, webbrowser, threading
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / 'vendor'))
from pypdf import PdfReader
DATA = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'EmberTable'
DATA.mkdir(parents=True, exist_ok=True)

def parse_pdf(raw):
    reader = PdfReader(io.BytesIO(raw))
    if reader.is_encrypted:
        raise ValueError('Password-protected PDFs are not supported. Export an unlocked character sheet.')
    if len(reader.pages)>40:
        raise ValueError('Use a character sheet with 40 pages or fewer.')
    fields = {str(k).lower().replace(' ', '').replace('_',''): str(v.get('/V','')) for k,v in (reader.get_fields() or {}).items()}
    text = '\n'.join(p.extract_text() or '' for p in reader.pages)
    def field(*names):
        for n in names:
            v=fields.get(n.lower().replace(' ', '').replace('_',''))
            if v and v!='None': return v
        return ''
    def num(v,default):
        m=re.search(r'\d+',v)
        return int(m.group()) if m else default
    name=field('CharacterName','CharacterName2','character_name')
    hp=field('HPMax','MaxHitPoints','HitPointMaximum')
    ac=field('AC','ArmorClass')
    cl=field('ClassLevel','ClassAndLevel','Class')
    if not text.strip() and not fields:
        raise ValueError('No readable text found. This may be a scanned PDF; OCR is not included. Enter your character manually.')
    return {'name':name,'class':cl,'level':num(field('Level'),num(cl,1)), 'hp':num(field('HPCurrent','CurrentHitPoints'),num(hp,10)), 'maxHp':num(hp,10),'ac':num(ac,10),'details':'PDF import — review all values. Unrecognized values use defaults.\n\n'+ '\n'.join(f'{k}: {v}' for k,v in fields.items())+'\n\n'+text,'needsReview':True}

class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(BASE/'app'),**kwargs)
    def reply(self,obj,code=200):
        data=json.dumps(obj).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if self.path=='/api/workspace':
            try:self.reply(json.loads((DATA/'workspace.json').read_text()))
            except FileNotFoundError:self.reply(None)
        else:super().do_GET()
    def do_POST(self):
        # Require same-origin browser requests, including the expected local host.
        if self.headers.get('Origin') != self.server.app_origin or self.headers.get('Host')!=self.server.app_origin.removeprefix('http://'):
            self.reply({'error':'Only the local app can write data.'},403);return
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n<1 or n>25*1024*1024:raise ValueError('File must be under 25 MB.')
            raw=self.rfile.read(n)
            if self.path=='/api/pdf':self.reply(parse_pdf(raw))
            elif self.path=='/api/workspace':
                data=json.loads(raw)
                if not isinstance(data.get('campaigns'),list):raise ValueError('Invalid workspace')
                tmp=DATA/'workspace.tmp';tmp.write_text(json.dumps(data),encoding='utf-8');os.replace(tmp,DATA/'workspace.json');self.reply({'saved':True})
            else:self.reply({'error':'Not found'},404)
        except Exception as e:self.reply({'error':str(e)},400)

