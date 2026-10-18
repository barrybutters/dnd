import os,sys,tempfile,unittest,io,json,zipfile,threading,urllib.request,urllib.error
from pathlib import Path
sandbox=tempfile.TemporaryDirectory();os.environ['EMBER_TABLE_DATA']=sandbox.name
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject,NameObject,TextStringObject,ArrayObject,NumberObject

class Storage(unittest.TestCase):
    def setUp(self):
        self.state={'campaigns':[{'id':'test','name':'Test campaign','maps':[]}]}
    def test_01_atomic_save_and_backup_recovery(self):
        server.write_workspace(self.state)
        next_state={'campaigns':[{'id':'test','name':'Second revision'}]}
        server.write_workspace(next_state)
        self.assertTrue(list(server.BACKUPS.glob('*.json')))
        self.assertEqual(server.read_workspace(),next_state)
        (server.DATA/'workspace.json').write_text('broken')
        recovered=server.read_workspace()
        self.assertIn('_recovery',recovered)
        server.write_workspace(recovered)
        self.assertTrue(list(server.DATA.glob('damaged-*.json')))
    def test_02_portable_assets_and_zip_path_rejection(self):
        name='a'*32+'.png';(server.ASSETS/name).write_bytes(b'local-image')
        server.write_workspace(self.state)
        package=server.export_package()
        (server.ASSETS/name).unlink()
        server.import_package(package)
        self.assertEqual((server.ASSETS/name).read_bytes(),b'local-image')
        bad=io.BytesIO()
        with zipfile.ZipFile(bad,'w') as z:z.writestr('workspace.json',json.dumps(self.state));z.writestr('../escape.txt','x')
        with self.assertRaises(ValueError):server.import_package(bad.getvalue())
        self.assertFalse((server.DATA.parent/'escape.txt').exists())
    def test_03_pdf_fields(self):
        w=PdfWriter();p=w.add_blank_page(width=600,height=800);refs=[]
        for name,value in [('CharacterName','Test Hero'),('HPMax','32'),('AC','17'),('STR','16')]:
            f=DictionaryObject({NameObject('/FT'):NameObject('/Tx'),NameObject('/T'):TextStringObject(name),NameObject('/V'):TextStringObject(value),NameObject('/Rect'):ArrayObject([NumberObject(0)]*4),NameObject('/Subtype'):NameObject('/Widget')});refs.append(w._add_object(f))
        p[NameObject('/Annots')]=ArrayObject(refs);w._root_object[NameObject('/AcroForm')]=DictionaryObject({NameObject('/Fields'):ArrayObject(refs)})
        raw=io.BytesIO();w.write(raw);r=server.parse_pdf(raw.getvalue())
        self.assertEqual((r['name'],r['maxHp'],r['ac'],r['abilities']['str']),('Test Hero',32,17,16))
    def test_05_rulebooks_and_portable_index(self):
        from pypdf.generic import DecodedStreamObject
        w=PdfWriter();p=w.add_blank_page(width=600,height=800)
        font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
        p[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):w._add_object(font)})})
        stream=DecodedStreamObject();stream.set_data(b'BT /F1 12 Tf 20 700 Td (Concentration test reference.) Tj ET');p[NameObject('/Contents')]=w._add_object(stream)
        raw=io.BytesIO();w.write(raw)
        book=server.import_rulebook(raw.getvalue(),'Rules test','2014')
        self.assertEqual(book['searchablePages'],1)
        saved=json.loads((server.RULES/(book['id']+'.json')).read_text(encoding='utf-8'))
        self.assertIn('Concentration',saved['pages'][0])
        server.write_workspace(self.state);package=server.export_package()
        (server.RULES/(book['id']+'.json')).unlink();server.import_package(package)
        self.assertTrue((server.RULES/(book['id']+'.json')).exists())

    def test_06_private_book_pack_keeps_campaigns(self):
        before={'campaigns':[{'id':'keep','name':'Keep my campaign'}]}
        server.write_workspace(before)
        bid='d'*32;asset='e'*32+'.pdf'
        book={'id':bid,'title':'Monster reference test','edition':'2014','url':'/assets/'+asset,'pageCount':1,'searchablePages':1,'pages':['test content']}
        raw=io.BytesIO()
        with zipfile.ZipFile(raw,'w') as z:
            z.writestr('ember-rulepack.json',json.dumps({'format':'ember-rulepack','version':1}))
            z.writestr('assets/'+asset,b'%PDF-test')
            z.writestr('rulebooks/'+bid+'.json',json.dumps(book))
        self.assertEqual(server.import_rulepack(raw.getvalue())['imported'],1)
        self.assertEqual(server.read_workspace(),before)
        self.assertEqual(server.import_rulepack(raw.getvalue())['imported'],1)
        self.assertEqual((server.ASSETS/asset).read_bytes(),b'%PDF-test')

    def test_07_empty_workspace_persists(self):
        server.write_workspace({'campaigns':[]})
        self.assertEqual(server.read_workspace()['campaigns'],[])

    def test_04_local_api(self):
        http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);http.app_origin=f'http://127.0.0.1:{http.server_port}'
        threading.Thread(target=http.serve_forever,daemon=True).start()
        try:
            origin=http.app_origin
            req=urllib.request.Request(origin+'/api/workspace',data=json.dumps(self.state).encode(),headers={'Origin':origin,'Content-Type':'application/json'})
            self.assertTrue(json.load(urllib.request.urlopen(req))['saved'])
            req=urllib.request.Request(origin+'/api/workspace',data=b'{}',headers={'Origin':'https://example.com'})
            with self.assertRaises(urllib.error.HTTPError) as caught:urllib.request.urlopen(req)
            self.assertEqual(caught.exception.code,403)
        finally:http.shutdown();http.server_close()

class ConcurrentReads(unittest.TestCase):
    def test_reads_observe_complete_revisions(self):
        server.write_workspace({'campaigns':[],'revision':0})
        errors=[];finished=threading.Event()
        def reader():
            while not finished.is_set():
                try:
                    data=server.read_workspace()
                    if data.get('_recovery') or not isinstance(data.get('revision'),int):errors.append(data)
                except Exception as e:errors.append(str(e))
        t=threading.Thread(target=reader);t.start()
        try:
            for n in range(1,41):server.write_workspace({'campaigns':[],'revision':n})
        finally:finished.set();t.join(timeout=5)
        self.assertEqual(errors,[]);self.assertEqual(server.read_workspace()['revision'],40)

if __name__=='__main__':unittest.main()
