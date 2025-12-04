from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer
from Monitering_Ui.threshold_manager import ThresholdManager
import csv


class ThresholdDialog(QDialog):

    DEVICE_TABLE_MAP = {
        "2GHz 수신기": "frontend_2ghz",
        "8GHz 수신기": "frontend_8ghz",
        "22GHz 수신기": "frontend_22ghz",
        "43GHz 수신기": "frontend_43ghz",
        "Video Converter 2": "VideoConverter2",
        "IF Selector": "IFselector",
        "S/X 다운컨버터": "SXDown",
        "K 다운컨버터": "KDown",
        "Q 다운컨버터": "QDown",
    }

    FRONTEND_COLUMNS = [
        "RF_RHCP", "RF_LHCP", "RF_LO",
        "Cryo_ColdPlate", "Cryo_ShieldBox",
        "Pressure",
        "NormalTemp_RF", "NormalTemp_Noise", "NormalTemp_Load",
        "LNA_LHCP_Vg1", "LNA_LHCP_Vg2", "LNA_LHCP_Vg3", "LNA_LHCP_Vg4",
        "LNA_LHCP_Vd1", "LNA_LHCP_Vd2", "LNA_LHCP_Vd3", "LNA_LHCP_Vd4",
        "LNA_LHCP_Id1", "LNA_LHCP_Id2", "LNA_LHCP_Id3", "LNA_LHCP_Id4",
        "LNA_RHCP_Vg1", "LNA_RHCP_Vg2", "LNA_RHCP_Vg3", "LNA_RHCP_Vg4",
        "LNA_RHCP_Vd1", "LNA_RHCP_Vd2", "LNA_RHCP_Vd3", "LNA_RHCP_Vd4",
        "LNA_RHCP_Id1", "LNA_RHCP_Id2", "LNA_RHCP_Id3", "LNA_RHCP_Id4",
    ]

    VIDEO2_COLUMNS = [
        "LEVELU_ch1", "LEVELU_ch2", "LEVELU_ch3", "LEVELU_ch4",
        "LEVELU_ch5", "LEVELU_ch6", "LEVELU_ch7", "LEVELU_ch8",
        "LEVELL_ch1", "LEVELL_ch2", "LEVELL_ch3", "LEVELL_ch4",
        "LEVELL_ch5", "LEVELL_ch6", "LEVELL_ch7", "LEVELL_ch8",
        "LOCK_ch1", "LOCK_ch2", "LOCK_ch3", "LOCK_ch4",
        "LOCK_ch5", "LOCK_ch6", "LOCK_ch7", "LOCK_ch8",
        "ATT_ch1", "ATT_ch2", "ATT_ch3", "ATT_ch4",
        "ATT_ch5", "ATT_ch6", "ATT_ch7", "ATT_ch8",
        "ATT_ch5", "ATT_ch6", "ATT_ch7", "ATT_ch8",
        "FRQALL_ch1", "FRQALL_ch2", "FRQALL_ch3", "FRQALL_ch4",
        "FRQALL_ch5", "FRQALL_ch6", "FRQALL_ch7", "FRQALL_ch8",
    ]

    IF_COLUMNS = [
        "OUT2IN_ch1", "OUT2IN_ch2", "OUT2IN_ch3", "OUT2IN_ch4",
        "OUT2IN_ch5", "OUT2IN_ch6", "OUT2IN_ch7", "OUT2IN_ch8",
        "OUT2IN_ch9", "OUT2IN_ch10", "OUT2IN_ch11", "OUT2IN_ch12",
        "OUT2IN_ch13", "OUT2IN_ch14", "OUT2IN_ch15", "OUT2IN_ch16",

        "ATT_ch1", "ATT_ch2", "ATT_ch3", "ATT_ch4",
        "ATT_ch5", "ATT_ch6", "ATT_ch7", "ATT_ch8",
        "ATT_ch9", "ATT_ch10", "ATT_ch11", "ATT_ch12",
        "ATT_ch13", "ATT_ch14", "ATT_ch15", "ATT_ch16",

        "LEVEL_ch1", "LEVEL_ch2", "LEVEL_ch3", "LEVEL_ch4",
        "LEVEL_ch5", "LEVEL_ch6", "LEVEL_ch7", "LEVEL_ch8",
        "LEVEL_ch9", "LEVEL_ch10", "LEVEL_ch11", "LEVEL_ch12",
        "LEVEL_ch13", "LEVEL_ch14", "LEVEL_ch15", "LEVEL_ch16",
    ]

    TABLE_COLUMNS = {
        "frontend_2ghz": FRONTEND_COLUMNS,
        "frontend_8ghz": FRONTEND_COLUMNS,
        "frontend_22ghz": FRONTEND_COLUMNS,
        "frontend_43ghz": FRONTEND_COLUMNS,
        "VideoConverter2": VIDEO2_COLUMNS,
        "IFselector": IF_COLUMNS,
        "SXDown": ["SLEVEL", "X1LEVEL", "X2LEVEL"],
        "KDown": ["K1LEVEL", "K2LEVEL", "K3LEVEL", "K4LEVEL"],
        "QDown": ["Q1LEVEL", "Q2LEVEL", "Q3LEVEL", "Q4LEVEL"],
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("임계값 설정")
        self.resize(500, 520)

        self.tm = ThresholdManager()

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.setStyleSheet("""
            QDialog { background-color:#0F172A; color:white; }
            QLabel { color:white; }
            QComboBox {
                color:white; background-color:#1E293B;
                border:1px solid #334155;
                padding:6px; border-radius:5px;
            }
            QLineEdit {
                color:white; background-color:#1E293B;
                border:1px solid #334155;
                padding:6px; border-radius:5px;
            }
            QPushButton {
                background-color:#2563EB; color:white;
                padding:10px; border-radius:8px; font-weight:bold;
            }
            QPushButton:hover { background-color:#1E40AF; }
        """)

        layout.addWidget(QLabel("장비 선택"))
        self.combo_device = QComboBox()
        layout.addWidget(self.combo_device)

        for dev, tab in self.DEVICE_TABLE_MAP.items():
            self.combo_device.addItem(dev, tab)

        layout.addWidget(QLabel("컬럼 선택"))
        self.combo_column = QComboBox()
        layout.addWidget(self.combo_column)

        layout.addWidget(QLabel("하한 주의 (LOW YELLOW)"))
        self.input_ly = QLineEdit()
        layout.addWidget(self.input_ly)

        layout.addWidget(QLabel("하한 경고 (LOW RED)"))
        self.input_lr = QLineEdit()
        layout.addWidget(self.input_lr)

        layout.addWidget(QLabel("상한 주의 (UPPER YELLOW)"))
        self.input_uy = QLineEdit()
        layout.addWidget(self.input_uy)

        layout.addWidget(QLabel("상한 경고 (UPPER RED)"))
        self.input_ur = QLineEdit()
        layout.addWidget(self.input_ur)

        btn_save = QPushButton("저장")
        btn_save.clicked.connect(self.save_threshold)
        layout.addWidget(btn_save)

        # -------------------------------
        # CSV 내보내기 / 불러오기 버튼
        # -------------------------------
        btn_export = QPushButton("CSV 내보내기")
        btn_export.clicked.connect(self.export_csv)
        layout.addWidget(btn_export)

        btn_import = QPushButton("CSV 불러오기")
        btn_import.clicked.connect(self.import_csv)
        layout.addWidget(btn_import)

        QTimer.singleShot(0, self._late_init)

    # ----------------------------------------------------------
    # 초기 UI 로드
    # ----------------------------------------------------------
    def _late_init(self):
        self.combo_device.currentIndexChanged.connect(self._reload_columns)
        self.combo_column.currentIndexChanged.connect(self._load_existing_threshold)
        self._reload_columns()

    def _reload_columns(self):
        table = self.combo_device.currentData()
        self.combo_column.clear()

        for c in self.TABLE_COLUMNS.get(table, []):
            self.combo_column.addItem(c)

        self._load_existing_threshold()

    def _load_existing_threshold(self):
        table = self.combo_device.currentData()
        col = self.combo_column.currentText()

        self.input_ly.clear()
        self.input_lr.clear()
        self.input_uy.clear()
        self.input_ur.clear()

        th = self.tm.get_threshold(table, col)
        if not th:
            return

        if th.get("lower_yellow") is not None:
            self.input_ly.setText(str(th["lower_yellow"]))
        if th.get("lower_red") is not None:
            self.input_lr.setText(str(th["lower_red"]))
        if th.get("upper_yellow") is not None:
            self.input_uy.setText(str(th["upper_yellow"]))
        if th.get("upper_red") is not None:
            self.input_ur.setText(str(th["upper_red"]))

    # ----------------------------------------------------------
    # 저장 버튼
    # ----------------------------------------------------------
    def save_threshold(self):
        table = self.combo_device.currentData()
        col = self.combo_column.currentText()

        try:
            ly = float(self.input_ly.text())
            lr = float(self.input_lr.text())
            uy = float(self.input_uy.text())
            ur = float(self.input_ur.text())
        except:
            QMessageBox.warning(self, "입력 오류", "모든 임계값에 숫자를 입력하세요.")
            return

        self.tm.set_threshold(table, col, ly, lr, uy, ur)
        QMessageBox.information(self, "저장 완료", "임계값이 저장되었습니다.")
        self.close()

    # ----------------------------------------------------------
    # CSV 내보내기
    # ----------------------------------------------------------
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "임계값 CSV 내보내기", "thresholds.csv", "CSV Files (*.csv)"
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["table", "column",
                             "lower_yellow", "lower_red",
                             "upper_yellow", "upper_red"])

            for table, cols in self.tm.thresholds.items():
                for col, th in cols.items():
                    writer.writerow([
                        table,
                        col,
                        th.get("lower_yellow", ""),
                        th.get("lower_red", ""),
                        th.get("upper_yellow", th.get("yellow", "")),
                        th.get("upper_red", th.get("red", "")),
                    ])

        QMessageBox.information(self, "완료", "CSV로 내보내기 완료되었습니다.")

    # ----------------------------------------------------------
    # CSV 불러오기
    # ----------------------------------------------------------
    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "CSV 선택", "", "CSV Files (*.csv)"
        )
        if not path:
            return

        new_data = {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    table = row["table"]
                    col = row["column"]

                    if table not in new_data:
                        new_data[table] = {}

                    def to_float(x):
                        try:
                            return float(x)
                        except:
                            return None

                    new_data[table][col] = {
                        "lower_yellow": to_float(row["lower_yellow"]),
                        "lower_red": to_float(row["lower_red"]),
                        "upper_yellow": to_float(row["upper_yellow"]),
                        "upper_red": to_float(row["upper_red"]),
                    }

            self.tm.thresholds = new_data
            self.tm.save()

            QMessageBox.information(self, "완료", "CSV에서 임계값이 불러와졌습니다.")

            self._reload_columns()

        except Exception as e:
            QMessageBox.warning(self, "오류", f"CSV 불러오기 실패: {e}")

