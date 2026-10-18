"""Ephemeral local dice presentation. OBS only receives explicitly shared rolls."""
import copy,json,math,threading,time,uuid,secrets,re
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
LOCK=threading.RLock()
CURRENT=None
PUBLIC=None
COMMANDS=[]
OBS_URL=''
LAST_POLL=0

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
    expr=str(data.get('expr','')).strip().replace(' ','')
    match=re.fullmatch(r'(\d{1,3})d(\d{1,4})([+-]\d{1,5})?',expr,re.I)
    if not match:raise ValueError('Use a dice expression such as 2d6+3')
    count,sides=int(match[1]),int(match[2]);modifier=int(match[3] or 0)
    if not 1<=count<=100 or not 2<=sides<=1000:raise ValueError('Use 1–100 dice with 2–1000 sides')
    # Generate and publish on the local server, even if WebView timers are suspended.
    with LOCK:
        if len(COMMANDS)>=100:raise ValueError('Return to the main window to sync your roll history')
        values=[secrets.randbelow(sides)+1 for _ in range(count)]
        roll={'expr':expr,'values':values,'sides':sides,'modifier':modifier,'total':sum(values)+modifier,'label':str(data.get('label',''))[:100]}
        publish({'roll':roll,'color':data.get('color','#d7b471'),'broadcast':data.get('broadcast') is True})
        event=snapshot()
        COMMANDS.append({'roll':event['roll'],'eventId':event['id'],'broadcast':data.get('broadcast') is True})
    return {'ok':True,'eventId':event['id']}

def drain():
    with LOCK:
        rows=COMMANDS[:];COMMANDS.clear();return rows

def start_overlay(base,port=17861):
    global OBS_URL
    class OverlayHandler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            global LAST_POLL
            path=self.path.split('?',1)[0]
            if path=='/api/overlay':
                LAST_POLL=time.time()
                raw=json.dumps(snapshot(True)).encode();mime='application/json'
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
