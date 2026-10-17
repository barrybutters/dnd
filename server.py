"""Offline Ember Table storage, PDF extraction, portable packages and recovery."""
import sys,json,io,re,os,threading,time,zipfile,uuid,shutil,mimetypes
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'vendor'))
from pypdf import PdfReader
DATA=Path(os.environ.get('EMBER_TABLE_DATA') or (Path(os.environ.get('LOCALAPPDATA',str(Path.home())))/'EmberTable'))
DATA.mkdir(parents=True,exist_ok=True)
ASSETS=DATA/'assets';ASSETS.mkdir(exist_ok=True)
BACKUPS=DATA/'backups';BACKUPS.mkdir(exist_ok=True)
RULES=DATA/'rulebooks';RULES.mkdir(exist_ok=True)
LOCK=threading.RLock()
ASSET_RE=re.compile(r'^[a-f0-9]{32}\.(png|jpg|jpeg|webp|gif|mp3|wav|ogg|m4a|pdf)$')

def validate(data):
    if not isinstance(data,dict) or not isinstance(data.get('campaigns'),list) or len(data['campaigns'])>200:raise ValueError('Invalid workspace')
    for c in data['campaigns']:
        if not isinstance(c,dict) or not isinstance(c.get('name'),str):raise ValueError('Invalid campaign')
    return data

def read_workspace():
    path=DATA/'workspace.json'
    if not path.exists():return None
    try:return validate(json.loads(path.read_text(encoding='utf-8')))
    except (ValueError,OSError):
        for p in sorted(BACKUPS.glob('*.json'),reverse=True):
            try:
                data=validate(json.loads(p.read_text(encoding='utf-8')))
                data['_recovery']='Recovered from automatic backup '+p.name
                return data
            except (ValueError,OSError):continue
        raise ValueError('The saved workspace is damaged. Restore an exported backup. The damaged file has been preserved.')

def write_workspace(data):
    validate(data)
    with LOCK:
        current=DATA/'workspace.json'
        if current.exists():
            # Preserve even a damaged current file; rotate only valid autosaves.
            try:validate(json.loads(current.read_text(encoding='utf-8')))
            except (ValueError,OSError):shutil.copy2(current,DATA/('damaged-'+str(time.time_ns())+'.json'))
            else:shutil.copy2(current,BACKUPS/(str(time.time_ns())+'.json'))
        raw=json.dumps(data,ensure_ascii=False).encode('utf-8')
        tmp=DATA/'workspace.tmp'
        with tmp.open('wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
        os.replace(tmp,current)
        for p in sorted(BACKUPS.glob('*.json'),reverse=True)[30:]:p.unlink()

def parse_pdf(raw):
    reader=PdfReader(io.BytesIO(raw))
    if reader.is_encrypted:raise ValueError('Export an unlocked PDF; encrypted PDFs are not supported.')
    if len(reader.pages)>40:raise ValueError('Character sheets must have 40 pages or fewer.')
    fields={re.sub(r'[\s_]','',str(k)).lower():str(v.get('/V','')) for k,v in (reader.get_fields() or {}).items()}
    text='\n'.join(p.extract_text() or '' for p in reader.pages)
    def field(*names):
        for n in names:
            v=fields.get(re.sub(r'[\s_]','',n).lower())
            if v and v!='None':return v
        return ''
    def number(v,default):
        m=re.search(r'-?\d+',v);return int(m.group()) if m else default
    def textnum(labels,default):
        for label in labels:
            m=re.search(label+r'\s*[:\n]?\s*(\d+)',text,re.I)
            if m:return int(m.group(1))
        return default
    if not text.strip() and not fields:raise ValueError('No readable text. Scanned PDFs need manual entry; OCR is not included.')
    name=field('CharacterName','CharacterName2')
    cl=field('ClassLevel','ClassAndLevel','Class')
    maximum=number(field('HPMax','MaxHitPoints','HitPointMaximum'),textnum(['Hit Point Maximum','Maximum Hit Points'],10))
    out={'name':name,'class':cl,'level':number(field('Level'),number(cl,1)),'hp':number(field('HPCurrent','CurrentHitPoints'),maximum),'maxHp':maximum,'ac':number(field('AC','ArmorClass'),textnum(['Armor Class'],10)),'abilities':{},'skills':{},'details':'PDF import — review values; missing fields use defaults.\n\n'+'\n'.join(f'{k}: {v}' for k,v in fields.items())+'\n\n'+text,'needsReview':True}
    for short,long in [('str','Strength'),('dex','Dexterity'),('con','Constitution'),('int','Intelligence'),('wis','Wisdom'),('cha','Charisma')]:out['abilities'][short]=number(field(short,long,long+'Score'),10)
    for skill in ['Acrobatics','Animal Handling','Arcana','Athletics','Deception','History','Insight','Intimidation','Investigation','Medicine','Nature','Perception','Performance','Persuasion','Religion','Sleight of Hand','Stealth','Survival']:
        v=field(skill,skill.replace(' ',''))
        if v:out['skills'][skill]=number(v,0)
    out['recognized']=sorted(k for k,v in fields.items() if v and v!='None')
    return out

def export_package():
    with LOCK:
        data=read_workspace()
        if data is None:raise ValueError('No workspace to export yet.')
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('workspace.json',json.dumps(data,ensure_ascii=False))
            for p in ASSETS.iterdir():
                if ASSET_RE.fullmatch(p.name):z.write(p,'assets/'+p.name)
            for p in RULES.glob('*.json'):
                if re.fullmatch(r'[a-f0-9]{32}\.json',p.name):z.write(p,'rulebooks/'+p.name)
        return b.getvalue()

def import_package(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        infos=z.infolist()
        if len(infos)>2000 or sum(i.file_size for i in infos)>500*1024*1024:raise ValueError('Package too large (500 MB expanded maximum).')
        if 'workspace.json' not in z.namelist():raise ValueError('Missing workspace.json')
        data=validate(json.loads(z.read('workspace.json')))
        assets={};books={}
        for i in infos:
            if i.filename=='workspace.json':continue
            if i.filename.startswith('rulebooks/') and re.fullmatch(r'[a-f0-9]{32}\.json',i.filename[10:]):
                book=json.loads(z.read(i));validate_book(book);books[i.filename[10:]]=z.read(i)
            elif i.filename.startswith('assets/') and ASSET_RE.fullmatch(i.filename[7:]):assets[i.filename[7:]]=z.read(i)
            else:raise ValueError('Invalid package path')
        with LOCK:
            for name,content in assets.items():
                p=ASSETS/name
                if p.exists() and p.read_bytes()!=content:raise ValueError('Asset identifier conflict. Restore into a fresh data folder.')
            for name,content in assets.items():(ASSETS/name).write_bytes(content)
            for name,content in books.items():(RULES/name).write_bytes(content)
            write_workspace(data)
    return data


def validate_book(book):
    if not isinstance(book,dict) or not re.fullmatch(r'[a-f0-9]{32}',book.get('id','')) or book.get('edition') not in ['2014','2024'] or not isinstance(book.get('pages'),list):raise ValueError('Invalid rulebook index')
    if not all(isinstance(p,str) for p in book['pages']):raise ValueError('Invalid book text')
    return book

def book_summary(book):
    return {k:book[k] for k in ['id','title','edition','url','pageCount','searchablePages']}

def import_rulebook(raw,title,edition):
    if edition not in ['2014','2024']:raise ValueError('Choose a rules edition.')
    if len(raw)>200*1024*1024:raise ValueError('Rulebook PDFs must be under 200 MB.')
    reader=PdfReader(io.BytesIO(raw))
    if reader.is_encrypted:raise ValueError('Use an unlocked PDF.')
    if not 1<=len(reader.pages)<=2000:raise ValueError('Use a PDF with 1 to 2000 pages.')
    pages=[]
    for page in reader.pages:
        try:pages.append((page.extract_text() or '')[:100000])
        except Exception:pages.append('')
    bid=uuid.uuid4().hex;asset_name=uuid.uuid4().hex+'.pdf'
    book={'id':bid,'title':str(title or 'Rulebook')[:200],'edition':edition,'url':'/assets/'+asset_name,'pageCount':len(pages),'searchablePages':sum(bool(p.strip()) for p in pages),'pages':pages}
    with LOCK:
        (ASSETS/asset_name).write_bytes(raw)
        tmp=RULES/(bid+'.tmp');tmp.write_text(json.dumps(book,ensure_ascii=False),encoding='utf-8');os.replace(tmp,RULES/(bid+'.json'))
    return book_summary(book)


def import_rulepack(raw):
    from book_import import import_pack
    return import_pack(io.BytesIO(raw),DATA,LOCK)

IMPORT_JOBS={}
IMPORT_JOB_LOCK=threading.Lock()
def start_book_import(path):
    from book_import import import_pack
    job_id=uuid.uuid4().hex
    with IMPORT_JOB_LOCK:
        if any(j.get('status')=='running' for j in IMPORT_JOBS.values()):raise ValueError('A book import is already running. Wait for it to finish.')
        IMPORT_JOBS[job_id]={'status':'running','phase':'Starting','percent':0,'message':'Opening book pack','booksDone':0,'booksTotal':0}
    def progress(**kw):
        with IMPORT_JOB_LOCK:IMPORT_JOBS[job_id].update(kw)
    def work():
        try:
            result=import_pack(path,DATA,LOCK,progress)
            with IMPORT_JOB_LOCK:IMPORT_JOBS[job_id].update(status='complete',result=result)
        except Exception as e:
            with IMPORT_JOB_LOCK:IMPORT_JOBS[job_id].update(status='error',error=str(e),message=str(e))
    threading.Thread(target=work,daemon=True).start()
    return {'job_id':job_id}

class Handler(SimpleHTTPRequestHandler):
    def guess_type(self,path):
        return 'application/javascript' if str(path).endswith('.mjs') else super().guess_type(path)
    def log_message(self,*args):pass
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(BASE/'app'),**kw)
    def send_bytes(self,data,mime,filename=None):
        self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)))
        if filename:self.send_header('Content-Disposition','attachment; filename="'+filename+'"')
        self.end_headers();self.wfile.write(data)
    def reply(self,obj,code=200):
        raw=json.dumps(obj).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        path=urlparse(self.path).path
        try:
            if path=='/api/workspace':self.reply(read_workspace())
            elif path=='/api/backups':self.reply([{'id':p.name,'time':p.stat().st_mtime} for p in sorted(BACKUPS.glob('*.json'),reverse=True)])
            elif path=='/api/export':self.send_bytes(export_package(),'application/zip','Ember-Table-Campaigns.zip')
            elif path.startswith('/api/import-status/'):
                job_id=path.rsplit('/',1)[-1]
                with IMPORT_JOB_LOCK:job=dict(IMPORT_JOBS.get(job_id,{}))
                if not job:self.reply({'error':'Import job not found'},404)
                else:self.reply(job)
            elif path=='/api/rules':
                books=[]
                for p in RULES.glob('*.json'):
                    try:books.append(book_summary(validate_book(json.loads(p.read_text(encoding='utf-8')))))
                    except (ValueError,KeyError):continue
                self.reply(books)
            elif path.startswith('/api/rules/'):
                bid=path.rsplit('/',1)[-1]
                if not re.fullmatch(r'[a-f0-9]{32}',bid):raise ValueError('Invalid book')
                book=validate_book(json.loads((RULES/(bid+'.json')).read_text(encoding='utf-8')))
                q=parse_qs(urlparse(self.path).query).get('q',[''])[0].strip()[:200]
                matches=[]
                if q:
                    for i,text in enumerate(book['pages']):
                        n=text.casefold().find(q.casefold())
                        if n>=0:matches.append({'page':i+1,'snippet':text[max(0,n-80):n+180]})
                self.reply({'book':book_summary(book),'matches':matches[:200],'total':len(matches)})
            elif path=='/api/display':
                s=read_workspace() or {};c=next((c for c in s.get('campaigns',[]) if c.get('id')==s.get('selected')),{});m=next((m for m in c.get('maps',[]) if m.get('id')==c.get('activeMap')),None)
                if m:
                    # This display omits DM records and hidden tokens.
                    m=dict(m);m['tokens']=[t for t in m.get('tokens',[]) if not t.get('hidden')];m.pop('notes',None)
                self.reply({'name':c.get('name','Ember Table'),'map':m,'round':c.get('round',1)})
            elif path.startswith('/assets/') and ASSET_RE.fullmatch(path[8:]):
                p=ASSETS/path[8:]
                if not p.exists():self.reply({'error':'Asset missing'},404)
                else:self.send_bytes(p.read_bytes(),mimetypes.guess_type(p.name)[0] or 'application/octet-stream')
            else:super().do_GET()
        except Exception as e:self.reply({'error':str(e)},500)
    def do_POST(self):
        if self.headers.get('Origin')!=self.server.app_origin or self.headers.get('Host')!=self.server.app_origin.removeprefix('http://'):
            self.reply({'error':'Only the local app can write data.'},403);return
        try:
            n=int(self.headers.get('Content-Length','0'))
            route=urlparse(self.path).path
            limit=600 if route=='/api/rules/pack' else 250 if route in ['/api/import','/api/rules'] else 100
            if n<1 or n>limit*1024*1024:raise ValueError('Request exceeds the size limit.')
            path=urlparse(self.path).path
            if path=='/api/rules/pack':
                import tempfile
                from book_import import import_pack
                with tempfile.TemporaryFile() as upload:
                    remaining=n
                    while remaining:
                        block=self.rfile.read(min(1024*1024,remaining))
                        if not block:raise ValueError('The file upload ended early. Try again.')
                        upload.write(block);remaining-=len(block)
                    upload.seek(0);self.reply(import_pack(upload,DATA,LOCK))
                return
            raw=self.rfile.read(n)
            if path=='/api/rules':
                args=parse_qs(urlparse(self.path).query)
                self.reply(import_rulebook(raw,args.get('title',['Rulebook'])[0],args.get('edition',['2014'])[0]))
            elif path.startswith('/api/import-status/'):
                job_id=path.rsplit('/',1)[-1]
                with IMPORT_JOB_LOCK:job=dict(IMPORT_JOBS.get(job_id,{}))
                if not job:self.reply({'error':'Import job not found'},404)
                else:self.reply(job)
            elif path=='/api/rules/remove':
                bid=json.loads(raw).get('id','')
                if not re.fullmatch(r'[a-f0-9]{32}',bid):raise ValueError('Invalid book')
                (RULES/(bid+'.json')).unlink(missing_ok=True);self.reply({'removed':True})
            elif path=='/api/pdf':self.reply(parse_pdf(raw))
            elif path=='/api/workspace':write_workspace(json.loads(raw));self.reply({'saved':True})
            elif path=='/api/import':self.reply(import_package(raw))
            elif path=='/api/recover':
                name=json.loads(raw).get('id','')
                if not re.fullmatch(r'\d+\.json',name):raise ValueError('Invalid backup')
                data=validate(json.loads((BACKUPS/name).read_text(encoding='utf-8')));write_workspace(data);self.reply(data)
            elif path=='/api/assets':
                ext=parse_qs(urlparse(self.path).query).get('ext',[''])[0].lower()
                name=uuid.uuid4().hex+'.'+ext
                if not ASSET_RE.fullmatch(name):raise ValueError('Unsupported file type')
                if len(raw)>40*1024*1024:raise ValueError('Asset must be under 40 MB.')
                (ASSETS/name).write_bytes(raw);self.reply({'url':'/assets/'+name,'size':len(raw)})
            else:self.reply({'error':'Not found'},404)
        except Exception as e:self.reply({'error':str(e)},400)
