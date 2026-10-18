import unittest,io,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from handouts import render_handout
from pypdf import PdfReader
class Handouts(unittest.TestCase):
 def test_pagination_and_embedding(self):
  for layout in ['document','cards']:
   raw=render_handout('Mara’s letter - café','A carefully reviewed handout.\n\n'+('longword'*70+'\n')*45,layout)
   r=PdfReader(io.BytesIO(raw));self.assertGreater(len(r.pages),1);self.assertIn('carefully reviewed',r.pages[0].extract_text());self.assertTrue(any('/FontFile2' in str(font.get_object().get('/FontDescriptor','')) for font in r.pages[0]['/Resources']['/Font'].get_object().values()))
 def test_input_limits(self):
  for text in ['',None,'x'*200001]:
   with self.assertRaises(ValueError):render_handout('Title',text)
if __name__=='__main__':unittest.main()
