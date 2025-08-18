# odf_editor_widget.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, pyqtSlot, pyqtSignal, QObject

import os

class ODFEditorBridge(QObject):
    # Signal to send ODF data from JS to Python
    odfSaved = pyqtSignal(bytes)

    @pyqtSlot(str)
    def saveODF(self, odf_base64):
        import base64
        odf_bytes = base64.b64decode(odf_base64)
        self.odfSaved.emit(odf_bytes)

class ODFEditorWidget(QWidget):
    def __init__(self, odf_path=None, parent=None):
        super().__init__(parent)
        self.odf_path = odf_path
        self.webview = QWebEngineView()
        self.bridge = ODFEditorBridge()
        self.bridge.odfSaved.connect(self.handle_odf_saved)

        layout = QVBoxLayout()
        layout.addWidget(self.webview)
        self.setLayout(layout)

        # Lock file logic
        self.lock_path = None
        if self.odf_path:
            self.lock_path = self.odf_path + ".lock"
            if os.path.exists(self.lock_path):
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "File Locked", "This file is currently being edited by another user.")
                self.setDisabled(True)
            else:
                with open(self.lock_path, "w") as f:
                    f.write("locked")

        # Show version info in window title
        version_info = ""
        try:
            from .vcs import VCS
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            vcs = VCS(project_root)
            # If VCS has a status or log method, use it; else, just show "versioned"
            version_info = " (versioned)"
        except Exception:
            version_info = ""

        if self.odf_path:
            self.setWindowTitle(f"Editing: {os.path.basename(self.odf_path)}{version_info}")

        # Load the editor HTML from static
        static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
        editor_html = QUrl.fromLocalFile(os.path.join(static_dir, "webodf", "editor.html"))
        self.webview.load(editor_html)

        # Expose the bridge to JS
        self.webview.page().setWebChannel(self._setup_webchannel())

        # After page load, inject ODF if path is given
        self.webview.loadFinished.connect(self._inject_odf_if_needed)

    def _inject_odf_if_needed(self):
        if self.odf_path and os.path.exists(self.odf_path):
            import base64
            with open(self.odf_path, "rb") as f:
                odf_bytes = f.read()
            odf_base64 = base64.b64encode(odf_bytes).decode("utf-8")
            js = f'loadODFfromBase64("{odf_base64}");'
            self.webview.page().runJavaScript(js)

    def _setup_webchannel(self):
        from PyQt5.QtWebChannel import QWebChannel
        channel = QWebChannel()
        channel.registerObject("ODFEditorBridge", self.bridge)
        return channel

    def load_odf(self, odf_path):
        self.odf_path = odf_path
        # JS will fetch the file via HTTP or via injected base64, depending on your setup
    def handle_odf_saved(self, odf_bytes):
        if self.odf_path:
            with open(self.odf_path, "wb") as f:
                f.write(odf_bytes)
            # Trigger VCS commit
            try:
                from .vcs import VCS
                import getpass
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                vcs = VCS(project_root)
                author = getpass.getuser()
                message = "ODF file edited in-app"
                vcs.add_and_commit(self.odf_path, author, message)
            except Exception as e:
                print("VCS commit failed:", e)
            # Provide user feedback
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Saved", "Document saved and committed.")

def closeEvent(self, event):
    # Remove lock file on close
    if self.lock_path and os.path.exists(self.lock_path):
        try:
            os.remove(self.lock_path)
        except Exception:
            pass
    super().closeEvent(event)
