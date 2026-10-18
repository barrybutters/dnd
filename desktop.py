"""Native desktop entrypoint; packaged with the Python runtime."""
import sys, threading, traceback
from pathlib import Path
import server
from close_guard import CloseGuard

def main():
    import webview
    webview.settings['ALLOW_DOWNLOADS'] = True
    qa_port=next((int(a.split('=',1)[1]) for a in sys.argv[1:] if a.startswith('--qa-port=')),None)
    if qa_port:
        webview.settings['REMOTE_DEBUGGING_PORT']=qa_port
        webview.settings['OPEN_DEVTOOLS_IN_DEBUG']=False
    http = server.ThreadingHTTPServer(('127.0.0.1', 0),server.Handler)
    overlay=server.dice_service.start_overlay(server.BASE,0 if qa_port else 17861)
    http.app_origin = f'http://127.0.0.1:{http.server_port}'
    threading.Thread(target=http.serve_forever,daemon=True).start()
    def display_trace(message):
        if qa_port:
            with (server.DATA/'display-test-log.txt').open('a',encoding='utf-8') as log:log.write(message+'\n')
    class DesktopAPI:
        def finish_close(self):
            return close_guard.finish()
        def cancel_close(self):
            return close_guard.cancel()
        def open_dice(self):
            for w in webview.windows:
                if w.title == "Ember Table · Dice":
                    w.show(); w.restore(); return True
            webview.create_window("Ember Table · Dice",http.app_origin+"/dice-window.html",width=900,height=650,min_size=(600,450))
            return True
        def backup_to_folder(self):
            from backups import write_folder_backup
            try:
                selected=main_window.create_file_dialog(webview.FileDialog.FOLDER)
                if not selected:return {'cancelled':True}
                return write_folder_backup(selected[0],server.export_package())
            except Exception as e:return {'error':str(e)}
        def choose_rulepack(self):
            def trace(message):
                with (server.DATA/'book-import-log.txt').open('a',encoding='utf-8') as log:log.write(message+'\n')
            try:
                trace('Native book chooser requested')
                selected=main_window.create_file_dialog(webview.FileDialog.OPEN,allow_multiple=False,file_types=('Ember Table book packs (*.zip)',))
                trace('Native chooser returned '+('a selected file' if selected else 'cancelled'))
                if not selected:return {'cancelled':True}
                return server.start_book_import(selected[0])
            except Exception as e:
                trace('Chooser error: '+str(e))
                return {'error':str(e)}
        def display_screens(self):
            display_trace('screens requested')
            result=[{'width':int(s.width),'height':int(s.height)} for s in webview.screens]
            display_trace('screens returned '+str(len(result)))
            return result
        def open_display(self, screen_index=0, fullscreen=False):
            display_trace('open display requested')
            screens=webview.screens
            index=max(0,min(int(screen_index),len(screens)-1))
            class DisplayAPI:
                def fullscreen(self):
                    display_trace('fullscreen requested')
                    display.toggle_fullscreen()
                    display_trace('fullscreen returned')
                    return True
            display=webview.create_window('Ember Table · Player Display',http.app_origin+'/display.html',width=1200,height=850,screen=screens[index] if screens else None,fullscreen=bool(fullscreen),js_api=DisplayAPI())
            display_trace('open display returned')
            return True
    try:
        main_window=webview.create_window('Ember Table 0.6.0',http.app_origin,width=1440,height=960,min_size=(900,650),js_api=DesktopAPI())
        close_guard=CloseGuard(main_window,lambda:webview.windows)
        main_window.events.closing += close_guard.request
        webview.start(gui='edgechromium',debug=bool(qa_port),private_mode=False,storage_path=str(server.DATA/'webview'),icon=str(server.BASE/'app'/'ember-table.ico'))
    finally:
        overlay.shutdown()
        overlay.server_close()
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
