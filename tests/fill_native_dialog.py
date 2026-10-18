"""Select the synthetic ZIP in the real Windows common Open dialog."""
import sys,time
from pathlib import Path
from pywinauto import Desktop
from pywinauto.keyboard import send_keys
path=str(Path(sys.argv[1]).resolve())
try:
    # Win32 sees owned common dialogs even when the UIA tree nests them under WebView2.
    main=Desktop(backend='win32').window(title_re=r'^Ember Table \d',visible_only=True)
    main.wait('visible',timeout=25)
    process=main.process_id()
    print('Ember Table dialog owner PID:',process,flush=True)
    dlg=Desktop(backend='win32').window(title='Open',class_name='#32770',process=process,visible_only=True)
    dlg.wait('visible',timeout=25)
    print('Native dialog title:',dlg.window_text(),flush=True)
    field=dlg.child_window(control_id=1148,class_name='Edit',visible_only=True,enabled_only=True,found_index=0)
    if field.exists(timeout=1):
        try:field.set_edit_text('"'+path+'"')
        except Exception:field.child_window(class_name='Edit').set_edit_text('"'+path+'"')
    else:
        fields=dlg.descendants(class_name='Edit',visible_only=True,enabled_only=True)
        if not fields:raise RuntimeError('No filename edit control in native Open dialog')
        field=fields[-1];field.set_edit_text('"'+path+'"')
    print('Filename value:',field.window_text(),flush=True)
    field.set_focus();send_keys('{ENTER}')
    dlg.wait_not('visible',timeout=15)
    print('Selected synthetic ZIP through native Windows dialog',flush=True)
except Exception:
    print('Visible native windows:',[(w.class_name(),w.window_text()) for w in Desktop(backend='win32').windows() if w.is_visible()],flush=True)
    try:
        print('Dialog controls:',[(c.class_name(),c.control_id(),c.window_text()) for c in dlg.descendants() if c.class_name() in ['Edit','ComboBox','ComboBoxEx32','Button']],flush=True)
    except Exception:pass
    raise
