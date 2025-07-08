import subprocess
import sys
from sniffy_ui import SniffyUI
from PyQt5.QtWidgets import QApplication
import os

LOG_FILE = "requests.log"
DB_FILE = "requests.db"

mitm = subprocess.Popen(["mitmdump", "-s", "sniffy_proxy.py"])

app = QApplication(sys.argv)
window = SniffyUI()
window.show()
exit_code = app.exec_()

mitm.terminate()
mitm.wait()

sys.exit(exit_code)
