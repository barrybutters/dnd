import os,tempfile,sys,threading,subprocess,json,zipfile
from pathlib import Path
sandbox=tempfile.TemporaryDirectory();os.environ['EMBER_TABLE_DATA']=sandbox.name
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject,NameObject,DecodedStreamObject
w=PdfWriter();page=w.add_blank_page(width=600,height=800)
font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):w._add_object(font)})})
stream=DecodedStreamObject();stream.set_data(b'BT /F1 16 Tf 40 740 Td (Concentration - local reader test page.) Tj ET')
page[NameObject('/Contents')]=w._add_object(stream)
fixture=server.BASE/'tests'/'rulebook-fixture.pdf'
with fixture.open('wb') as f:w.write(f)
pack=server.BASE/'tests'/'small-pack-fixture.zip'
bid='a'*32;asset='b'*32+'.pdf'
book={'id':bid,'title':'Browser imported pack book','edition':'2024','url':'/assets/'+asset,'pageCount':1,'searchablePages':1,'pages':['Concentration - local reader test page.']}
with zipfile.ZipFile(pack,'w') as z:
 z.writestr('ember-rulepack.json',json.dumps({'format':'ember-rulepack','version':1}))
 z.writestr('assets/'+asset,fixture.read_bytes());z.writestr('rulebooks/'+bid+'.json',json.dumps(book))
http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);http.app_origin=f'http://127.0.0.1:{http.server_port}'
threading.Thread(target=http.serve_forever,daemon=True).start()
try:
 result=subprocess.call(['node','tests/ui-smoke.cjs',http.app_origin],cwd=server.BASE)
 if result==0:result=subprocess.call(['node','tests/expansion.cjs',http.app_origin],cwd=server.BASE)
 if result==0:result=subprocess.call(['node','tests/v05.cjs',http.app_origin],cwd=server.BASE)
 sys.exit(result)
finally:http.shutdown();http.server_close();fixture.unlink(missing_ok=True);pack.unlink(missing_ok=True)
