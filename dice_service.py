"""Ephemeral local dice presentation. OBS only receives explicitly shared rolls."""
import copy,json,math,threading,time,uuid
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
LOCK=threading.Lock()
CURRENT=None
PUBLIC=None
COMMANDS=[]
OBS_URL=''

def publish(data):
    global CURRENT,PUBLIC
    if data.get('clear'):
        with LOCK:PUBLIC=None;CURRENT=None
        return {'ok':True}
    r=data.get('roll',{})
    values=r.get('values',[]);sides=r.get('sides',0)
    if not isinstance(sides,int) or not 2<=sides<=1000 or not isinstance(values,list) or not 1<=len(values)<=100 or any(type(v)!=int or not 1<=v<=sides for v in values):raise ValueError('Invalid dice')
    if not isinstance(r.get('total'),(int,float)) or not math.isfinite(r['total']):raise ValueError('Invalid total')
    color=data.get('color','#d7b471')
    import re
    if not re.fullmatch('#[0-9a-fA-F]{6}',str(color)):color='#d7b471'
    event={'id':uuid.uuid4().hex,'created':time.time()*1000,'expires':time.time()*1000+15000,'color':color,'roll':{'values':values,'sides':sides,'total':r['total'],'modifier':r.get('modifier',0),'expr':str(r.get('expr',''))[:100],'label':str(r.get('label',''))[:100]}}
    if type(r.get('keptIndex'))==int and 0<=r['keptIndex']<len(values):event['roll']['keptIndex']=r['keptIndex']
    with LOCK:
        CURRENT=event
        if data.get('broadcast') is True:PUBLIC=event
    return {'ok':True}

def snapshot(public=False):
    with LOCK:
        value=PUBLIC if public else CURRENT
        return copy.deepcopy(value) if value and value['expires']>time.time()*1000 else None

def command(data):
    expr=str(data.get('expr','')).strip()
    import re
    if not re.fullmatch(r'\d{1,3}d\d{1,4}([+-]\d{1,5})?',expr,re.I):raise ValueError('Use a dice expression such as 2d6+3')
    with LOCK:
        if len(COMMANDS)>=20:raise ValueError('Dice request queue is full')
        COMMANDS.append({'expr':expr,'broadcast':data.get('broadcast') is True})
    return {'ok':True}

def drain():
    with LOCK:
        rows=COMMANDS[:];COMMANDS.clear();return rows

def start_overlay(base,port=17861):
    global OBS_URL
    class OverlayHandler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            path=self.path.split('?',1)[0]
            if path=='/api/overlay':raw=json.dumps(snapshot(True)).encode();mime='application/json'
            elif path in ['/overlay.html','/overlay.js','/dice3d.js']:
                raw=(Path(base)/'app'/path[1:]).read_bytes();mime='text/html' if path.endswith('.html') else 'application/javascript'
            else:self.send_error(404);return
            self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)));self.end_headers()
            try:self.wfile.write(raw)
            except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):pass
        def do_POST(self):self.send_error(405)
    try:http=ThreadingHTTPServer(('127.0.0.1',port),OverlayHandler)
    except OSError:http=ThreadingHTTPServer(('127.0.0.1',0),OverlayHandler)
    OBS_URL=f'http://127.0.0.1:{http.server_port}/overlay.html'
    threading.Thread(target=http.serve_forever,daemon=True).start()
    return http
