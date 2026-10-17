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
    class DesktopAPI:
        def choose_rulepack(self):
            try:
                selected=main_window.create_file_dialog(webview.FileDialog.OPEN,allow_multiple=False,file_types=('Ember Table book packs (*.zip)',))
                if not selected:return {'cancelled':True}
                return server.start_book_import(selected[0])
            except Exception as e:return {'error':str(e)}
        def open_display(self):
            webview.create_window('Ember Table · Player Display',http.app_origin+'/display.html',width=1200,height=850)
            return True
    try:
        main_window=webview.create_window('Ember Table 0.3.3',http.app_origin,width=1440,height=960,min_size=(900,650),js_api=DesktopAPI())
        def before_close():
            try:
                pending=main_window.evaluate_js("Boolean(window.__saving || window.__scratchPending || window.__bookImporting)")
                if pending:
                    main_window.evaluate_js("if(typeof save==='function') save(); if(typeof toast==='function') toast('Saving or importing. Please wait until it finishes before closing.');")
                    return False
            except Exception:
                pass
        main_window.events.closing += before_close
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
