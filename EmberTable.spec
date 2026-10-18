# Build on Windows with PyInstaller. Bundles Python and the app's assets.
from PyInstaller.utils.hooks import collect_all
web_datas, web_bins, web_hidden = collect_all('webview')
pdf_datas, pdf_bins, pdf_hidden = collect_all('pypdf')
handout_datas, handout_bins, handout_hidden = collect_all('reportlab')
a = Analysis(['desktop.py'],pathex=['vendor'],binaries=web_bins+pdf_bins+handout_bins,
    datas=[('app','app'),('vendor/pypdf-LICENSE.txt','licenses')]+web_datas+pdf_datas+handout_datas,
    hiddenimports=web_hidden+pdf_hidden+handout_hidden,hookspath=[],hooksconfig={},runtime_hooks=[],excludes=['PyQt5','PyQt6','PySide2','PySide6'],noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz,a.scripts,[],exclude_binaries=True,name='EmberTable',debug=False,bootloader_ignore_signals=False,strip=False,upx=False,console=False)
coll = COLLECT(exe,a.binaries,a.datas,strip=False,upx=False,name='EmberTable')
