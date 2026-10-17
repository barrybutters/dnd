"""Drive the installed packaged desktop app, including its real file chooser."""
import os,sys,time,subprocess,tempfile,urllib.request,socket
from pathlib import Path
with tempfile.TemporaryDirectory() as profile:
    with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
    env=dict(os.environ,LOCALAPPDATA=profile,WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=f'--remote-debugging-port={port} --force-renderer-accessibility')
    app=subprocess.Popen([str(Path(sys.argv[1]).resolve())],env=env)
    try:
        for attempt in range(60):
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/json/version',timeout=1) as r:
                    if r.status==200:break
            except Exception:pass
            if app.poll() is not None:raise RuntimeError('Packaged app exited during startup')
            time.sleep(.5)
        else:raise RuntimeError('The WebView2 test connection did not open')
        code=subprocess.call(['node','tests/native-pack.cjs',str(port),'tests/large pack fixture.zip'])
        if code:raise RuntimeError('Native book import regression test failed')
    finally:subprocess.run(['taskkill','/PID',str(app.pid),'/T','/F'],capture_output=True)
