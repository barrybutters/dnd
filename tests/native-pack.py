"""Drive the installed packaged desktop app, including its real file chooser."""
import os,sys,time,subprocess,tempfile,urllib.request,socket
from pathlib import Path
with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as profile:
    with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
    env=dict(os.environ,LOCALAPPDATA=profile,WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=f'--remote-debugging-port={port} --force-renderer-accessibility')
    app=subprocess.Popen([str(Path(sys.argv[1]).resolve()),f'--qa-port={port}'],env=env)
    try:
        for attempt in range(60):
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/json/version',timeout=1) as r:
                    if r.status==200:break
            except Exception:pass
            if app.poll() is not None:raise RuntimeError('Packaged app exited during startup')
            time.sleep(.5)
        else:raise RuntimeError('The WebView2 test connection did not open')
        code=subprocess.run(['node','tests/native-pack.cjs',str(port),'tests/large pack fixture.zip'],timeout=180).returncode
        if code:raise RuntimeError('Native book import regression test failed')
    finally:
        for name in ['book-import-log.txt','display-test-log.txt','startup-error.txt']:
            log=Path(profile)/'EmberTable'/name
            if log.exists():print(name+':\n'+log.read_text(encoding='utf-8'),flush=True)
        subprocess.run(['taskkill','/PID',str(app.pid),'/T','/F'],capture_output=True)
