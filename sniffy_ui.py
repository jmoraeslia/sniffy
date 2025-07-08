from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QLabel,
    QPushButton, QHBoxLayout, QTabWidget, QTreeView
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QStandardItemModel, QStandardItem

import json
import os
import qdarkstyle
import sqlite3
import datetime

LOG_FILE = "requests.log"
DB_FILE = "requests.db"

class SniffyUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sniffy - Request Viewer")
        self.resize(800, 600)

        self.font_size = 12
        self.dark_mode = True

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        self.toggle_theme_btn = QPushButton("Light Theme")
        self.toggle_theme_btn.clicked.connect(self.toggle_theme)
        top_layout.addWidget(self.toggle_theme_btn)

        main_layout.addLayout(top_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.live_tab = QWidget()
        live_layout = QVBoxLayout()
        self.label_live = QLabel("Captured Requests (Live):")
        live_layout.addWidget(self.label_live)
        self.list_widget = QListWidget()
        live_layout.addWidget(self.list_widget)
        self.live_tab.setLayout(live_layout)
        self.tabs.addTab(self.live_tab, "Captura")

        self.history_tab = QWidget()
        history_layout = QVBoxLayout()
        self.label_history = QLabel("Request History (by Date):")
        history_layout.addWidget(self.label_history)

        self.tree_view = QTreeView()
        history_layout.addWidget(self.tree_view)
        self.history_tab.setLayout(history_layout)
        self.tabs.addTab(self.history_tab, "Histórico")

        self.setLayout(main_layout)

        self.last_size = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_requests)
        self.timer.start(1000)  # check every second

        # atualiza histórico ao trocar de aba
        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.update_font_size()
        self.apply_theme()
        self.load_history()

    def update_requests(self):
        # Atualiza lista ao vivo lendo requests.log
        if not os.path.exists(LOG_FILE):
            return

        with open(LOG_FILE, "r") as f:
            f.seek(self.last_size)
            lines = f.readlines()
            self.last_size = f.tell()

        for line in lines:
            try:
                data = json.loads(line)
                display = f"{data['method']} {data['url']}"
                self.list_widget.addItem(display)
            except json.JSONDecodeError:
                continue

    def load_history(self):
        if not os.path.exists(DB_FILE):
            return
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, method, url, timestamp FROM requests ORDER BY timestamp DESC")
        rows = c.fetchall()
        conn.close()

        data_by_day = {}
        for row in rows:
            ts = datetime.datetime.fromtimestamp(row[3])
            date_str = ts.strftime("%Y-%m-%d")
            if date_str not in data_by_day:
                data_by_day[date_str] = []
            data_by_day[date_str].append({
                "id": row[0],
                "method": row[1],
                "url": row[2],
                "timestamp": row[3]
            })

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Request History"])

        for date, requests in sorted(data_by_day.items(), reverse=True):
            date_item = QStandardItem(f"📅 {date}")
            date_item.setEditable(False)

            for req in requests:
                text = f"{req['method']} {req['url']}"
                child_item = QStandardItem(text)
                child_item.setEditable(False)
                date_item.appendRow(child_item)

            model.appendRow(date_item)

        self.tree_view.setModel(model)
        self.tree_view.expandAll()

    def on_tab_changed(self, index):
        if self.tabs.tabText(index) == "Histórico":
            self.load_history()

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
                self.font_size += 1
                self.update_font_size()
            elif event.key() == Qt.Key_Minus:
                self.font_size = max(6, self.font_size - 1)
                self.update_font_size()

    def update_font_size(self):
        font = QFont()
        font.setPointSize(self.font_size)
        self.setFont(font)

        if self.dark_mode:
            base_qss = qdarkstyle.load_stylesheet_pyqt5()
            base_qss += f"""
            QWidget {{
                font-size: {self.font_size}pt;
            }}
            """
            QApplication.instance().setStyleSheet(base_qss)
        else:
            QApplication.instance().setStyleSheet("")
            self.setFont(font)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self.toggle_theme_btn.setText("Dark Theme" if not self.dark_mode else "Light Theme")

    def apply_theme(self):
        if self.dark_mode:
            base_qss = qdarkstyle.load_stylesheet_pyqt5()
            base_qss += f"""
            QWidget {{
                font-size: {self.font_size}pt;
            }}
            """
            QApplication.instance().setStyleSheet(base_qss)
        else:
            QApplication.instance().setStyleSheet("")
            self.update_font_size()
