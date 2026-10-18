"""Click the actual native title-bar close path without blocking the test driver."""
from pywinauto import Desktop
import ctypes
w=Desktop(backend='win32').window(title_re=r'^Ember Table \d')
w.wait('visible',timeout=10)
ctypes.windll.user32.PostMessageW(w.handle,0x0010,0,0)
