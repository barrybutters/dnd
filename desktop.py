"""Native desktop entrypoint; packaged with the Python runtime."""
import sys, threading, traceback
from pathlib import Path
import server

def main():
    import webview
    webview.settings['ALLOW_DOWNLOADS'] = True
    http = server.ThreadingHTTPServer(('127.0.0.1', 0),server.Handler)
    http.app_origin = f'http://127.0.0.1:{http.server_port}'
    threading.Thread(target=http.serve_forever,daemon=True).start()
    try:
        webview.create_window('Ember Table',http.app_origin,width=1440,height=960,min_size=(900,650))
        webview.start(gui='edgechromium',private_mode=False,storage_path=str(server.DATA/'webview'))
    finally:
        http.shutdown()
        http.server_close()

if __name__=='__main__':
    try: main()
    except Exception:
        log=server.DATA/'startup-error.txt'
        log.write_text(traceback.format_exc(),encoding='utf-8')
        import ctypes
        ctypes.windll.user32.MessageBoxW(0,f'Ember Table could not start. Details: {log}\nMake sure Microsoft Edge WebView2 Runtime is installed.','Ember Table',16)
        sys.exit(1)
