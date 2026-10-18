"""Never wait for the WebView from its blocking native closing callback."""
import threading

class CloseGuard:
    def __init__(self, window, all_windows):
        self.window, self.all_windows = window, all_windows
        self.allowed = False
        self.pending = False
        self.lock = threading.Lock()

    def request(self):
        with self.lock:
            if self.allowed:return True
            if not self.pending:
                self.pending = True
                threading.Thread(target=self._prepare, daemon=True).start()
        return False

    def _prepare(self):
        try:
            self.window.evaluate_js('window.prepareDesktopClose ? window.prepareDesktopClose() : window.pywebview.api.finish_close()')
        except Exception:
            # A failed renderer must not trap the user in a dead window.
            self.finish()

    def cancel(self):
        with self.lock:self.pending = False
        return True

    def finish(self):
        with self.lock:self.allowed = True
        for window in list(self.all_windows()):
            if window is not self.window:
                try:window.destroy()
                except Exception:pass
        self.window.destroy()
        return True
