import os,sys,tempfile,unittest,io
from pathlib import Path
sandbox=tempfile.TemporaryDirectory();os.environ['EMBER_TABLE_DATA']=sandbox.name
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server
from pypdf import PdfWriter
class Manual(unittest.TestCase):
 def pdf(self,password=None):
  writer=PdfWriter();writer.add_blank_page(width=600,height=800);writer.add_blank_page(width=600,height=800)
  if password is not None:writer.encrypt(password,owner_password='test-owner')
  out=io.BytesIO();writer.write(out);return out.getvalue()
 def test_reconnect_preserves_identity(self):
  b=server.import_rulebook(self.pdf(),'Monster Manual test','2014');self.assertTrue(b['fileAvailable']);(server.ASSETS/b['url'][8:]).unlink()
  import json
  index=json.loads((server.RULES/(b['id']+'.json')).read_text());self.assertFalse(server.book_summary(index)['fileAvailable'])
  fixed=server.import_rulebook(self.pdf(),'Monster Manual test','2014',b['id']);self.assertEqual(fixed['id'],b['id']);self.assertTrue(fixed['fileAvailable']);self.assertNotEqual(b['url'],fixed['url']);self.assertEqual(fixed['pageCount'],2)
 def test_blank_opening_password_and_required_password(self):
  b=server.import_rulebook(self.pdf(''),'Blank password manual','2024');self.assertTrue(b['fileAvailable'])
  with self.assertRaisesRegex(ValueError,'requires a password'):server.import_rulebook(self.pdf('secret'),'Locked manual','2014')
 def test_invalid_replacement_rejected(self):
  with self.assertRaises(ValueError):server.import_rulebook(self.pdf(),'Invalid','2014','../workspace')
if __name__=='__main__':unittest.main()
