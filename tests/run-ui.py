import os,tempfile,sys,threading,subprocess
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
http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);http.app_origin=f'http://127.0.0.1:{http.server_port}'
threading.Thread(target=http.serve_forever,daemon=True).start()
try:sys.exit(subprocess.call(['node','tests/ui-smoke.cjs',http.app_origin],cwd=server.BASE))
finally:http.shutdown();http.server_close();fixture.unlink(missing_ok=True)
