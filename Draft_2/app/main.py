# main.py - PySide6 QML migration entry point
# -------------------------------------------
# This is a prototype entry point for the QML migration.
# TODO: Integrate backend logic and data models.
# TODO: Add signal/slot connections for login and dashboard.
# TODO: Move business logic from Flask/old UI to PySide6 as needed.

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl

if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Load the QML UI
    qml_file = QUrl.fromLocalFile("Draft_2/app/qml/Main.qml")
    engine.load(qml_file)

    # TODO: Expose Python objects to QML context as needed

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
