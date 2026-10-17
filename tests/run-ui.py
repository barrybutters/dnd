import os,tempfile,sys,threading,subprocess
from pathlib import Path
sandbox=tempfile.TemporaryDirectory();os.environ['EMBER_TABLE_DATA']=sandbox.name
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server
http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);http.app_origin=f'http://127.0.0.1:{http.server_port}'
threading.Thread(target=http.serve_forever,daemon=True).start()
try:sys.exit(subprocess.call(['node','tests/ui-smoke.cjs',http.app_origin],cwd=server.BASE))
finally:http.shutdown();http.server_close()
