"""Generate a large synthetic pack for Windows CI. No supplied books are used."""
from pathlib import Path
import io,json,os,zipfile,hashlib
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject,NameObject,DecodedStreamObject
out=Path('tests/large pack fixture.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_STORED) as z:
    z.writestr('ember-rulepack.json',json.dumps({'format':'ember-rulepack','version':1}))
    for i in range(5):
        w=PdfWriter();page=w.add_blank_page(width=600,height=800)
        font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
        page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):w._add_object(font)})})
        stream=DecodedStreamObject();stream.set_data(b'BT /F1 16 Tf 40 740 Td (Concentration - native import regression test.) Tj ET');page[NameObject('/Contents')]=w._add_object(stream)
        padding=DecodedStreamObject();padding.set_data(os.urandom(78*1024*1024));w._add_object(padding)
        raw=io.BytesIO();w.write(raw);pdf=raw.getvalue();bid=f'{i+1:032x}';asset=f'{i+101:032x}'+'.pdf'
        book={'id':bid,'title':'Native test book '+str(i+1),'edition':'2014' if i<3 else '2024','url':'/assets/'+asset,'pageCount':1,'searchablePages':1,'pages':['Concentration - native import regression test.'],'sha256':hashlib.sha256(pdf).hexdigest()}
        z.writestr('assets/'+asset,pdf);z.writestr('rulebooks/'+bid+'.json',json.dumps(book))
        print('Created native fixture book',i+1,flush=True)
print('Large pack bytes:',out.stat().st_size)
