import unittest,tempfile,sys,zipfile,io
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backups import write_folder_backup
class Backups(unittest.TestCase):
 def test_atomic_copies_keep_previous(self):
  b=io.BytesIO()
  with zipfile.ZipFile(b,'w') as z:z.writestr('workspace.json','{"campaigns":[]}')
  with tempfile.TemporaryDirectory() as d:
   a=write_folder_backup(d,b.getvalue());c=write_folder_backup(d,b.getvalue())
   self.assertNotEqual(a['name'],c['name']);self.assertEqual((Path(d)/a['name']).read_bytes(),b.getvalue());self.assertEqual(len(list(Path(d).glob('*.zip'))),2);self.assertFalse(list(Path(d).glob('*.part')))
 def test_bad_destination(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):write_folder_backup(Path(d)/'absent',b'zip')
if __name__=='__main__':unittest.main()
