"""Streaming, staged book-pack import. Never buffers a full pack/PDF in memory."""
import hashlib,json,os,re,shutil,tempfile,zipfile
from pathlib import Path
ID_RE=re.compile(r'^[a-f0-9]{32}$')
ASSET_RE=re.compile(r'^[a-f0-9]{32}\.pdf$')

def import_pack(source,data_dir,lock,progress=lambda **kw:None):
    data_dir=Path(data_dir);assets_dir=data_dir/'assets';books_dir=data_dir/'rulebooks'
    assets_dir.mkdir(parents=True,exist_ok=True);books_dir.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(source) as z:
        infos=z.infolist();total=sum(i.file_size for i in infos)
        if len(infos)>1000 or total>1024*1024*1024:raise ValueError('Book pack exceeds the 1 GB expanded limit.')
        names=[i.filename for i in infos]
        if len(names)!=len(set(names)):raise ValueError('The pack has duplicate file paths.')
        if 'ember-rulepack.json' not in names:raise ValueError('This is not an Ember Table book pack. Select Ember-Table-Rulebook-Pack.zip without extracting it.')
        if z.getinfo('ember-rulepack.json').file_size>65536:raise ValueError('Invalid pack manifest.')
        manifest=json.loads(z.read('ember-rulepack.json'))
        if manifest.get('format')!='ember-rulepack' or manifest.get('version')!=1:raise ValueError('Unsupported book pack format.')
        books={};assets={}
        for info in infos:
            name=info.filename
            if name=='ember-rulepack.json':continue
            if name.startswith('assets/') and ASSET_RE.fullmatch(name[7:]):assets[name[7:]]=info
            elif name.startswith('rulebooks/') and re.fullmatch(r'[a-f0-9]{32}\.json',name[10:]):
                if info.file_size>30*1024*1024:raise ValueError('A book search index is too large.')
                b=json.loads(z.read(info))
                if b.get('id')+'.json'!=name[10:] or not ID_RE.fullmatch(b.get('id','')) or b.get('edition') not in ['2014','2024']:raise ValueError('Invalid book index identity.')
                pages=b.get('pages')
                if not isinstance(pages,list) or not 1<=len(pages)<=2000 or not all(isinstance(p,str) for p in pages):raise ValueError('Invalid page search index.')
                b['pageCount']=len(pages);b['searchablePages']=sum(bool(p.strip()) for p in pages)
                b['title']=str(b.get('title') or 'Rulebook')[:200]
                if not re.fullmatch(r'/assets/[a-f0-9]{32}\.pdf',b.get('url','')):raise ValueError('Invalid book PDF reference.')
                books[name[10:]]=b
            else:raise ValueError('The book pack contains an unexpected file path.')
        if not books:raise ValueError('The pack contains no rulebooks.')
        for b in books.values():
            if b['url'][8:] not in assets:raise ValueError('The pack is missing a referenced PDF.')
        if shutil.disk_usage(data_dir).free<total+20*1024*1024:raise ValueError('Not enough free disk space to import this pack.')
        done=0;progress(phase='Validating',percent=2,message='Checking '+str(len(books))+' books',booksTotal=len(books),booksDone=0)
        with tempfile.TemporaryDirectory(prefix='book-import-',dir=data_dir) as staging:
            staging=Path(staging)
            for n,(name,info) in enumerate(assets.items(),1):
                title=next((b['title'] for b in books.values() if b['url'].endswith(name)),name)
                digest=hashlib.sha256();target=staging/name
                with z.open(info) as src,target.open('wb') as dst:
                    first=True
                    while True:
                        block=src.read(1024*1024)
                        if not block:break
                        if first and not block.startswith(b'%PDF-'):raise ValueError(title+' is not a valid PDF file.')
                        first=False;dst.write(block);digest.update(block);done+=len(block)
                        progress(phase='Copying PDFs',percent=min(92,2+int(done/max(1,total)*90)),message=title,booksTotal=len(books),booksDone=n-1)
                expected=next((b.get('sha256') for b in books.values() if b['url'].endswith(name)),None)
                if expected and digest.hexdigest()!=expected:raise ValueError('Checksum mismatch for '+title+'. Download the pack again.')
                existing=assets_dir/name
                if existing.exists():
                    with existing.open('rb') as f:existing_hash=hashlib.file_digest(f,'sha256').hexdigest()
                    if existing_hash!=digest.hexdigest():raise ValueError('An existing local book conflicts with '+title)
            with lock:
                progress(phase='Installing',percent=95,message='Installing books and search indexes',booksTotal=len(books),booksDone=len(books))
                for name in assets:
                    if not (assets_dir/name).exists():os.replace(staging/name,assets_dir/name)
                for name,b in books.items():
                    tmp=books_dir/(name+'.tmp');tmp.write_text(json.dumps(b,ensure_ascii=False),encoding='utf-8');os.replace(tmp,books_dir/name)
        summaries=[{k:b[k] for k in ['id','title','edition','url','pageCount','searchablePages']} for b in books.values()]
        progress(phase='Complete',percent=100,message='Added '+str(len(books))+' books',booksTotal=len(books),booksDone=len(books))
        return {'imported':len(books),'books':summaries}
