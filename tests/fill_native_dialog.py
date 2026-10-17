"""Select the synthetic ZIP using the actual Windows file dialog."""
import sys,time
from pathlib import Path
from pywinauto import Desktop
path=str(Path(sys.argv[1]).resolve())
try:
    dlg=Desktop(backend='uia').window(class_name='#32770',title_re='.*(Open|Select).*')
    dlg.wait('visible',timeout=30);dlg.set_focus()
    field=dlg.child_window(auto_id='1148',control_type='Edit')
    if not field.exists(timeout=2):
        fields=dlg.descendants(control_type='Edit')
        if not fields:raise RuntimeError('No filename entry found in the native dialog')
        field=fields[-1]
    field.set_edit_text(path)
    button=dlg.child_window(auto_id='1',control_type='Button')
    if not button.exists(timeout=2):button=dlg.child_window(title='Open',control_type='Button')
    button.invoke()
    print('Selected synthetic ZIP through native Windows dialog',flush=True)
except Exception:
    try:dlg.print_control_identifiers()
    except Exception:pass
    raise
