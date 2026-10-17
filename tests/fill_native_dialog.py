"""Select the synthetic ZIP in the real Windows common Open dialog."""
import sys,time
from pathlib import Path
from pywinauto import Desktop
path=str(Path(sys.argv[1]).resolve())
try:
    # Win32 sees owned common dialogs even when the UIA tree nests them under WebView2.
    dlg=Desktop(backend='win32').window(class_name='#32770',visible_only=True)
    dlg.wait('visible',timeout=25)
    print('Native dialog title:',dlg.window_text(),flush=True)
    field=dlg.child_window(control_id=1148)
    if field.exists(timeout=1):
        try:field.set_edit_text(path)
        except Exception:field.child_window(class_name='Edit').set_edit_text(path)
    else:
        fields=dlg.descendants(class_name='Edit')
        if not fields:raise RuntimeError('No filename edit control in native Open dialog')
        fields[-1].set_edit_text(path)
    dlg.child_window(control_id=1).click()
    print('Selected synthetic ZIP through native Windows dialog',flush=True)
except Exception:
    print('Visible native windows:',[(w.class_name(),w.window_text()) for w in Desktop(backend='win32').windows() if w.is_visible()],flush=True)
    raise
