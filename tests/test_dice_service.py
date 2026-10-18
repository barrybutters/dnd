import unittest,sys,threading,json,urllib.request,urllib.error
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import dice_service as d
from close_guard import CloseGuard
class Dice(unittest.TestCase):
 def setUp(self):d.publish({'clear':True});d.drain()
 def test_privacy_validation_and_overlay(self):
  event={'roll':{'values':[20],'sides':20,'total':20,'expr':'1d20','label':'Public test'},'broadcast':False}
  d.publish(event);self.assertIsNone(d.snapshot(True));self.assertEqual(d.snapshot()['roll']['total'],20)
  event['broadcast']=True;d.publish(event);self.assertEqual(d.snapshot(True)['roll']['label'],'Public test');self.assertNotIn('campaign',d.snapshot(True))
  h=d.start_overlay(Path(__file__).resolve().parents[1],0)
  try:
   origin=d.OBS_URL.removesuffix('/overlay.html')
   with urllib.request.urlopen(origin+'/api/overlay') as r:self.assertEqual(json.load(r)['roll']['total'],20)
   for path in ['/api/workspace','/api/dice-state','/../server.py']:
    with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(origin+path)
  finally:h.shutdown();h.server_close()
  d.publish({'clear':True});self.assertIsNone(d.snapshot(True))
  for value in [0,21,True,'20']:
   with self.assertRaises(ValueError):d.publish({'roll':{'values':[value],'sides':20,'total':20}})
 def test_queue_once(self):
  d.command({'expr':'2d6+3','broadcast':True});self.assertEqual(d.drain(),[{'expr':'2d6+3','broadcast':True}]);self.assertEqual(d.drain(),[])
 def test_close_callback_does_not_wait_on_renderer(self):
  entered=threading.Event();release=threading.Event();called=[]
  class Window:
   def evaluate_js(self,code):entered.set();release.wait(2);called.append(threading.get_ident())
   def destroy(self):called.append('destroy')
  w=Window();g=CloseGuard(w,lambda:[w]);thread=threading.get_ident()
  self.assertFalse(g.request());self.assertTrue(entered.wait(1));self.assertFalse(g.request());release.set()
  g.finish();self.assertTrue(g.request());self.assertIn('destroy',called)
if __name__=='__main__':unittest.main()
