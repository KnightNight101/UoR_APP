from PySide6.QtCore import QObject, Signal, Slot

class LoginManager(QObject):
    loginResult = Signal(bool, str)  # success, message

    def __init__(self):
        super().__init__()
        # Placeholder: in-memory user store
        self._users = {
            "alice": "password123",
            "bob": "securepass",
            "admin": "admin"
        }

    @Slot(str, str)
    def verify_credentials(self, username, password):
        """Check credentials and emit loginResult signal."""
        if username in self._users and self._users[username] == password:
            self.loginResult.emit(True, "Login successful")
        else:
            self.loginResult.emit(False, "Invalid username or password")