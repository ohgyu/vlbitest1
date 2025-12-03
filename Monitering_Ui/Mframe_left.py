# Monitering_Ui/Mframe_left.py
from PyQt6.QtWidgets import (
    QScrollArea, QWidget, QVBoxLayout, QPushButton,
    QLabel, QFrame, QHBoxLayout, QGridLayout
)
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl, Qt, pyqtSignal
from Monitering_Ui.threshold_manager import ThresholdManager
from db_manager import get_connection
import os
import time


class MFrameLeft(QScrollArea):

    device_selected = pyqtSignal(str)

    DEVICE_TABLE_MAP = {
        "2GHz 수신기": "frontend_2ghz",
        "8GHz 수신기": "frontend_8ghz",
        "22GHz 수신기": "frontend_22ghz",
        "43GHz 수신기": "frontend_43ghz",
        "S/X 다운컨버터": "SXDownConverter",
        "K 다운컨버터": "KDownConverter",
        "Q 다운컨버터": "QDownConverter",
        "Video Converter 1": None,
        "Video Converter 2": "VideoConverter2",
        "IF Selector": "IFselector",
    }

    # 여러 줄을 합쳐야 하는 테이블에 대한 row 개수 정의
    ROW_MERGE_COUNT = {
        "SXDownConverter": 3,
        "KDownConverter": 3,
        "QDownConverter": 3,
        "IFselector": 3,
        "VideoConverter2": 5,
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setStyleSheet("background-color:#0F172A; border-radius:10px;")

        self.content = QWidget()
        self.setWidget(self.content)

        self.main_layout = QVBoxLayout(self.content)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(12)

        self.device_widgets = {}

        title = QLabel("REAL-TIME DEVICE STATUS")
        title.setStyleSheet("color:#38BDF8; font-size:20pt; font-weight:bold;")
        self.main_layout.addWidget(title)

        for device in self.DEVICE_TABLE_MAP.keys():
            self._create_device_row(device)

        self.main_layout.addStretch()

        # ===================================================
        # Threshold Manager
        # ===================================================
        self.thresholds = ThresholdManager()

        # ===================================================
        # 안정 버전: QSoundEffect 절대 크래시 방지
        # ===================================================
        self.alarm = QSoundEffect()
        wav_path = os.path.abspath("alarm.wav")

        if os.path.exists(wav_path):
            self.alarm.setSource(QUrl.fromLocalFile(wav_path))
            self.sound_enabled = True
        else:
            print("[경고] alarm.wav 파일 없음 → 알람 비활성화 (크래시 방지)")
            self.sound_enabled = False

        self.alarm.setVolume(0.9)
        self.last_alarm = 0

    # ---------------------------------------------------------
    def _create_device_row(self, device_name: str):
        btn = QPushButton(device_name)
        btn.setCheckable(True)
        btn.setStyleSheet(self._btn_style_default())
        self.main_layout.addWidget(btn)

        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(20, 5, 10, 5)
        panel_layout.setSpacing(6)
        panel.setVisible(False)
        self.main_layout.addWidget(panel)

        btn.clicked.connect(lambda checked, name=device_name: self._toggle_panel(name))

        self.device_widgets[device_name] = {
            "button": btn,
            "panel": panel,
        }

    # ---------------------------------------------------------
    def _btn_style_default(self):
        return """
        QPushButton {
            text-align:left;
            background-color:#1E293B;
            color:white;
            padding:10px;
            border-radius:8px;
            font-size:16pt;
        }
        QPushButton:hover { background-color:#334155; }
        QPushButton:checked {
            background-color:#2563EB;
            font-weight:bold;
        }
        """

    # ---------------------------------------------------------
    def _toggle_panel(self, device_name: str):
        info = self.device_widgets.get(device_name)
        if not info:
            return

        btn = info["button"]
        panel = info["panel"]

        if panel.isVisible():
            panel.setVisible(False)
            btn.setChecked(False)
        else:
            panel.setVisible(True)
            btn.setChecked(True)
            self._reload_panel(device_name)

        self.device_selected.emit(device_name)

    # ---------------------------------------------------------
    def refresh_expanded(self):
        for device_name, info in self.device_widgets.items():
            if info["panel"].isVisible():
                self._reload_panel(device_name)

    # ---------------------------------------------------------
    def _fetch_latest_row_with_merge(self, table: str, conn):
        """
        테이블에서 가장 최신 데이터를 읽되,
        ROW_MERGE_COUNT에 정의된 경우 여러 줄을 합쳐서 하나의 row처럼 반환한다.
        반환값: (col_names, row_tuple 또는 None)
        """
        merge_count = self.ROW_MERGE_COUNT.get(table, 1)
        cur = conn.cursor()

        # 병합 불필요: 기존 방식 그대로
        if merge_count <= 1:
            cur.execute(f"SELECT * FROM {table} ORDER BY datetime DESC LIMIT 1")
            row = cur.fetchone()
            col_names = [d[0] for d in cur.description] if row else []
            return col_names, row

        # 병합 필요한 테이블: 최근 merge_count 줄을 가져와 병합
        cur.execute(
            f"SELECT * FROM {table} ORDER BY datetime DESC LIMIT {merge_count}"
        )
        rows = cur.fetchall()
        if not rows:
            return [], None

        col_names = [d[0] for d in cur.description]

        # 각 컬럼별로 첫 번째 non-NULL 값 선택 (최신 row부터 순서대로)
        merged = [None] * len(col_names)
        for row in rows:
            for idx, val in enumerate(row):
                if merged[idx] is None and val is not None:
                    merged[idx] = val

        # datetime 컬럼이 있다면 가장 최신 row의 값 최소 보장
        try:
            dt_idx = col_names.index("datetime")
            if merged[dt_idx] is None:
                merged[dt_idx] = rows[0][dt_idx]
        except ValueError:
            # datetime 컬럼이 없는 경우는 무시
            pass

        return col_names, tuple(merged)

    # ---------------------------------------------------------
    def _reload_panel(self, device_name: str):

        info = self.device_widgets.get(device_name)
        if not info:
            return

        try:
            self.thresholds.load()
        except Exception as e:
            print("Threshold reload error:", e)

        panel = info["panel"]
        layout = panel.layout()

        self._clear_layout(layout)

        table = self.DEVICE_TABLE_MAP.get(device_name)
        if not table:
            layout.addWidget(self._make_label("실시간 데이터 미구성 (테이블 없음)"))
            return

        try:
            conn = get_connection(readonly=True)
            col_names, row = self._fetch_latest_row_with_merge(table, conn)

            if not row:
                layout.addWidget(self._make_label("데이터가 없습니다."))
                return

        except Exception as e:
            layout.addWidget(self._make_label(f"DB 오류: {e}"))
            return

        finally:
            try:
                conn.close()
            except:
                pass

        # -------------------------
        # 임계값 검사 (상/하한)
        # -------------------------
        upper_warnings = []
        upper_errors = []
        lower_warnings = []
        lower_errors = []

        level_map = {}  # ★ 필수

        for col, raw_val in zip(col_names, row):
            try:
                val = float(raw_val)
            except:
                val = None

            th = self.thresholds.get_threshold(table, col)
            level = None

            if th and val is not None:
                ly = th.get("lower_yellow")
                lr = th.get("lower_red")
                uy = th.get("upper_yellow")
                ur = th.get("upper_red")

                # 하한 RED
                if lr is not None and val <= lr:
                    level = "red"
                    lower_errors.append(f"{device_name} - {col}: {val}")

                # 하한 YELLOW
                elif ly is not None and val <= ly:
                    level = "yellow"
                    lower_warnings.append(f"{device_name} - {col}: {val}")

                # 상한 RED
                elif ur is not None and val >= ur:
                    level = "red"
                    upper_errors.append(f"{device_name} - {col}: {val}")

                # 상한 YELLOW
                elif uy is not None and val >= uy:
                    level = "yellow"
                    upper_warnings.append(f"{device_name} - {col}: {val}")

            level_map[col] = level

        # ===================================================
        # 알람
        # ===================================================
        all_errors = upper_errors + lower_errors

        if all_errors and self.sound_enabled:
            now = time.time()
            if now - self.last_alarm > 5:
                self.alarm.stop()
                self.alarm.play()
                self.last_alarm = now

        # ===================================================
        # UI 표시 (3열 Grid)
        # ===================================================
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        grid.setContentsMargins(10, 5, 10, 5)
        layout.addLayout(grid)

        row_idx, col_idx = 0, 0

        for col, val in zip(col_names, row):
            level = level_map.get(col)
            card = self._make_value_card(col, val, level)
            grid.addWidget(card, row_idx, col_idx)

            col_idx += 1
            if col_idx >= 3:
                col_idx = 0
                row_idx += 1

    # ---------------------------------------------------------
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    # ---------------------------------------------------------
    def _make_label(self, text: str):
        lbl = QLabel(text)
        lbl.setStyleSheet("color:#9CA3AF; font-size:12pt;")
        lbl.setWordWrap(True)
        return lbl

    # ---------------------------------------------------------
    def _make_value_card(self, name, value, level=None):

        card = QFrame()

        color_border = "#1E293B"
        color_bg = "#020617"

        if level == "yellow":
            color_border = "#facc15"
            color_bg = "#4a3f05"

        elif level == "red":
            color_border = "#f87171"
            color_bg = "#5c1f1f"

        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color_bg};
                border-radius: 8px;
                border: 2px solid {color_border};
            }}
        """)

        hl = QHBoxLayout(card)
        hl.setContentsMargins(10, 5, 10, 5)
        hl.setSpacing(8)

        lbl_name = QLabel(str(name))
        lbl_name.setStyleSheet("color:#9CA3AF; font-size:12pt;")

        lbl_val = QLabel("" if value is None else str(value))
        lbl_val.setStyleSheet("color:white; font-size:14pt; font-weight:bold;")
        lbl_val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        hl.addWidget(lbl_name, 3)
        hl.addWidget(lbl_val, 2)

        return card

    def update_all_thresholds(self):

        upper_warnings = []
        upper_errors = []
        lower_warnings = []
        lower_errors = []

        # 모든 장비 스캔
        for device, table in self.DEVICE_TABLE_MAP.items():
            if not table:
                continue

            try:
                conn = get_connection(readonly=True)
                col_names, row = self._fetch_latest_row_with_merge(table, conn)
                if not row:
                    continue
            finally:
                try:
                    conn.close()
                except:
                    pass

            for col, raw_val in zip(col_names, row):
                try:
                    val = float(raw_val)
                except:
                    continue

                th = self.thresholds.get_threshold(table, col)
                if not th:
                    continue

                ly = th.get("lower_yellow")
                lr = th.get("lower_red")
                uy = th.get("upper_yellow")
                ur = th.get("upper_red")

                # ---- 하한 경고/주의 ----
                if lr is not None and val <= lr:
                    lower_errors.append(f"{device} - {col}: {val}")
                elif ly is not None and val <= ly:
                    lower_warnings.append(f"{device} - {col}: {val}")

                # ---- 상한 경고/주의 ----
                if ur is not None and val >= ur:
                    upper_errors.append(f"{device} - {col}: {val}")
                elif uy is not None and val >= uy:
                    upper_warnings.append(f"{device} - {col}: {val}")

        # Summary 업데이트
        if hasattr(self, "summary") and self.summary:
            self.summary.update_alerts(
                upper_warnings, upper_errors,
                lower_warnings, lower_errors
            )

        # 경고음 (상/하한 합산)
        all_errors = upper_errors + lower_errors
        if all_errors and self.sound_enabled:
            now = time.time()
            if now - self.last_alarm > 5:
                self.alarm.play()
                self.last_alarm = now
