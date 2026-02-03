"""Chemical Equipment Parameter Visualizer - PyQt5 Desktop Client."""
import sys
import os
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QMessageBox,
    QTabWidget,
    QGroupBox,
    QFormLayout,
    QComboBox,
    QFrame,
    QScrollArea,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from api_client import EquipmentAPI, DEFAULT_BASE

# Add parent so we can load sample CSV from repo root
REPO_ROOT = Path(__file__).resolve().parent.parent


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sign In")
        self.setMinimumWidth(320)
        layout = QFormLayout(self)
        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("Username")
        self.pass_edit = QLineEdit()
        self.pass_edit.setPlaceholderText("Password")
        self.pass_edit.setEchoMode(QLineEdit.Password)
        layout.addRow("Username:", self.user_edit)
        layout.addRow("Password:", self.pass_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        self.api = None
        self.base_url = DEFAULT_BASE

    def accept(self):
        user = self.user_edit.text().strip()
        password = self.pass_edit.text()
        if not user:
            QMessageBox.warning(self, "Error", "Enter username.")
            return
        self.api = EquipmentAPI(self.base_url, user, password)
        try:
            self.api.login(user, password)
        except Exception as e:
            QMessageBox.critical(self, "Login Failed", str(e))
            return
        super().accept()


class SummaryCards(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        layout = QGridLayout(self)
        self.labels = {}
        for i, (key, title) in enumerate(
            [
                ("total", "Total Count"),
                ("flowrate", "Avg Flowrate"),
                ("pressure", "Avg Pressure"),
                ("temperature", "Avg Temperature"),
            ]
        ):
            lab = QLabel("—")
            lab.setStyleSheet("font-size: 18px; font-weight: bold;")
            layout.addWidget(QLabel(title), i // 2, (i % 2) * 2)
            layout.addWidget(lab, i // 2, (i % 2) * 2 + 1)
            self.labels[key] = lab

    def set_summary(self, summary):
        if not summary:
            for k in self.labels:
                self.labels[k].setText("—")
            return
        self.labels["total"].setText(str(summary.get("total_count", "—")))
        av = summary.get("averages", {})
        self.labels["flowrate"].setText(str(av.get("Flowrate", "—")))
        self.labels["pressure"].setText(str(av.get("Pressure", "—")))
        self.labels["temperature"].setText(str(av.get("Temperature", "—")))


class DoughnutCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4):
        self.fig = Figure(figsize=(width, height), facecolor="#1e293b")
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#1e293b")
        self.ax.tick_params(colors="white")
        for spine in self.ax.spines.values():
            spine.set_color("none")

    def plot_distribution(self, type_dist):
        self.ax.clear()
        self.ax.set_facecolor("#1e293b")
        self.ax.tick_params(colors="white")
        if not type_dist:
            self.ax.text(0.5, 0.5, "No data", ha="center", va="center", color="gray", fontsize=14)
            self.draw()
            return
        labels = list(type_dist.keys())
        sizes = list(type_dist.values())
        colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]
        colors = colors[: len(labels)]
        wedges, texts, autotexts = self.ax.pie(
            sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90
        )
        for t in texts + autotexts:
            t.set_color("white")
        centre_circle = plt.Circle((0, 0), 0.5, fc="#1e293b")
        self.ax.add_artist(centre_circle)
        self.draw()


class BarCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4):
        self.fig = Figure(figsize=(width, height), facecolor="#1e293b")
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#1e293b")
        self.ax.tick_params(colors="white")
        for spine in self.ax.spines.values():
            spine.set_color("#334155")

    def plot_averages(self, averages):
        self.ax.clear()
        self.ax.set_facecolor("#1e293b")
        self.ax.tick_params(colors="white")
        for spine in self.ax.spines.values():
            spine.set_color("#334155")
        if not averages:
            self.ax.text(0.5, 0.5, "No data", ha="center", va="center", color="gray", fontsize=14)
            self.draw()
            return
        labels = list(averages.keys())
        values = list(averages.values())
        self.ax.bar(labels, values, color="#3b82f6")
        self.ax.set_ylabel("Value", color="white")
        self.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api = None
        self.current_data = None
        self.setWindowTitle("Chemical Equipment Parameter Visualizer (Desktop)")
        self.setMinimumSize(900, 700)
        self.resize(1000, 750)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Header
        header = QHBoxLayout()
        title = QLabel("Chemical Equipment Parameter Visualizer")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header.addWidget(title)
        header.addStretch()
        self.upload_btn = QPushButton("Upload CSV")
        self.upload_btn.clicked.connect(self.do_upload)
        self.pdf_btn = QPushButton("Generate PDF Report")
        self.pdf_btn.clicked.connect(self.do_pdf)
        self.pdf_btn.setEnabled(False)
        self.logout_btn = QPushButton("Sign Out")
        self.logout_btn.clicked.connect(self.do_logout)
        header.addWidget(self.upload_btn)
        header.addWidget(self.pdf_btn)
        header.addWidget(self.logout_btn)
        layout.addLayout(header)

        # History
        history_box = QGroupBox("History (last 5 datasets)")
        history_layout = QHBoxLayout(history_box)
        self.history_combo = QComboBox()
        self.history_combo.currentIndexChanged.connect(self.on_history_selected)
        history_layout.addWidget(QLabel("Dataset:"))
        history_layout.addWidget(self.history_combo, 1)
        layout.addWidget(history_box)

        # Summary cards
        self.cards = SummaryCards()
        layout.addWidget(self.cards)

        # Charts
        charts_layout = QHBoxLayout()
        doughnut_group = QGroupBox("Equipment Type Distribution")
        doughnut_layout = QVBoxLayout(doughnut_group)
        self.doughnut_canvas = DoughnutCanvas(self, width=4, height=3)
        doughnut_layout.addWidget(self.doughnut_canvas)
        charts_layout.addWidget(doughnut_group, 1)

        bar_group = QGroupBox("Parameter Averages")
        bar_layout = QVBoxLayout(bar_group)
        self.bar_canvas = BarCanvas(self, width=4, height=3)
        bar_layout.addWidget(self.bar_canvas)
        charts_layout.addWidget(bar_group, 1)
        layout.addLayout(charts_layout)

        # Table
        table_group = QGroupBox("Data Table")
        table_layout = QVBoxLayout(table_group)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Equipment Name", "Type", "Flowrate", "Pressure", "Temperature"]
        )
        table_layout.addWidget(self.table)
        layout.addWidget(table_group, 1)

        self.refresh_history()

    def set_current(self, summary, records=None, dataset_id=None):
        self.current_data = {"summary": summary, "records": records or [], "dataset_id": dataset_id}
        self.cards.set_summary(summary)
        if summary:
            self.doughnut_canvas.plot_distribution(summary.get("equipment_type_distribution", {}))
            self.bar_canvas.plot_averages(summary.get("averages", {}))
        else:
            self.doughnut_canvas.plot_distribution({})
            self.bar_canvas.plot_averages({})
        self.pdf_btn.setEnabled(bool(summary and (dataset_id or self.get_selected_history_id())))
        self.populate_table(records or [])

    def get_selected_history_id(self):
        idx = self.history_combo.currentData()
        return idx

    def populate_table(self, records):
        self.table.setRowCount(len(records))
        cols = ["Equipment Name", "Type", "Flowrate", "Pressure", "Temperature"]
        for row, r in enumerate(records):
            for col, key in enumerate(cols):
                val = r.get(key, "")
                self.table.setItem(row, col, QTableWidgetItem(str(val)))
        self.table.resizeColumnsToContents()

    def refresh_history(self):
        if not self.api:
            self.history_combo.clear()
            self.history_combo.addItem("(No history)", None)
            return
        try:
            data = self.api.history()
            self.history_combo.blockSignals(True)
            self.history_combo.clear()
            self.history_combo.addItem("(Select or upload)", None)
            for h in data:
                self.history_combo.addItem(
                    f"{h.get('name', '?')} ({h.get('row_count', 0)} rows)",
                    h.get("id"),
                )
            self.history_combo.blockSignals(False)
            if data and self.history_combo.currentData() is None:
                self.history_combo.setCurrentIndex(1)
        except Exception as e:
            QMessageBox.warning(self, "History", f"Could not load history: {e}")

    def on_history_selected(self):
        did = self.get_selected_history_id()
        if did is None:
            if not self.current_data:
                self.set_current(None)
            return
        try:
            s = self.api.summary(did)
            self.set_current(
                s.get("summary"),
                records=[],
                dataset_id=s.get("id"),
            )
        except Exception as e:
            QMessageBox.warning(self, "Summary", str(e))

    def do_upload(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV", str(REPO_ROOT), "CSV (*.csv);;All (*)"
        )
        if not path:
            return
        try:
            result = self.api.upload_csv(path, name=os.path.basename(path))
            summary = result.get("summary", {})
            records = result.get("records", [])
            dataset_id = result.get("dataset_id")
            self.set_current(summary, records, dataset_id)
            self.refresh_history()
            # Select the newly uploaded one
            for i in range(self.history_combo.count()):
                if self.history_combo.itemData(i) == dataset_id:
                    self.history_combo.setCurrentIndex(i)
                    break
            QMessageBox.information(self, "Upload", "File uploaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Upload Failed", str(e))

    def do_pdf(self):
        did = self.current_data.get("dataset_id") if self.current_data else None
        if not did:
            did = self.get_selected_history_id()
        if not did:
            QMessageBox.warning(self, "PDF", "Select a dataset first.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", f"equipment_report_{did}.pdf", "PDF (*.pdf)"
        )
        if not path:
            return
        try:
            self.api.download_pdf(did, path)
            QMessageBox.information(self, "PDF", f"Report saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "PDF Failed", str(e))

    def do_logout(self):
        self.api = None
        self.current_data = None
        self.set_current(None)
        self.refresh_history()
        self.show_login()

    def show_login(self):
        d = LoginDialog(self)
        if d.exec_() != QDialog.Accepted:
            QApplication.quit()
            return
        self.api = d.api
        self.refresh_history()
        self.on_history_selected()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show_login()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
