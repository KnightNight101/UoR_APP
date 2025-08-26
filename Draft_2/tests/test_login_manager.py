import pytest
from PySide6.QtCore import QObject, Signal, Slot, QCoreApplication
import sys
import os

# Patch sys.path to allow importing main.py without db import error
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../app")))

from Draft_2.app.login_manager import LoginManager

class SignalCatcher(QObject):
    def __init__(self):
        super().__init__()
        self.results = []

    @Slot(bool, str)
    def catch(self, success, message):
        self.results.append((success, message))

def test_login_manager_valid_and_invalid(qtbot):
    # Ensure a Qt event loop exists
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication(sys.argv)

    login_manager = LoginManager()
    catcher = SignalCatcher()
    login_manager.loginResult.connect(catcher.catch)

    # Valid credentials
    login_manager.verify_credentials("alice", "password123")
    login_manager.verify_credentials("bob", "securepass")
    login_manager.verify_credentials("admin", "admin")

    # Invalid credentials
    login_manager.verify_credentials("alice", "wrongpass")
    login_manager.verify_credentials("not_a_user", "nopass")

    # Allow signals to process
    QCoreApplication.processEvents()

    # Check results
    expected = [
        (True, "Login successful"),
        (True, "Login successful"),
        (True, "Login successful"),
        (False, "Invalid username or password"),
        (False, "Invalid username or password"),
    ]
    assert catcher.results == expected

def test_no_data_loaded_before_login():
    # LoginManager does not load user/project data at all
    login_manager = LoginManager()
    assert not hasattr(login_manager, "user")
    assert not hasattr(login_manager, "projects")