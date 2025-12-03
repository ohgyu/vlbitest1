from typing import TYPE_CHECKING
from PyQt6.QtWidgets import (
    QFrame, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QWidget,
    QDialog, QListWidget, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve

# MonitoringWindow 타입 힌트
if TYPE_CHECKING:
    from MoniteringMain import MonitoringWindow

from Monitering_Ui.threshold_dialog import ThresholdDialog


# ======================================================
# MiniCard (경고/주의 개별 카드)
# ======================================================
class MiniCard(QFrame):
    def __init__(self, name, color, parent=None):
        super().__init__(parent)

        # 전체 박스만 외곽선 있음
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #0F172A;
                border-radius: 10px;
                border: 2px solid {color};
            }}
            QLabel {{
                background: transparent;
                color:white;
                font-size:16pt;
                font-weight:bold;
                border: none;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(10)

        self.label_name = QLabel(name)
        self.label_value = QLabel("0")

        layout.addWidget(self.label_name)
        layout.addWidget(self.label_value)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # 깜빡임 효과 그대로 유지
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)

        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(600)
        self.anim.setStartValue(0.3)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.setLoopCount(-1)

    def set_count(self, c):
        self.label_value.setText(f"{c}")

        if c >= 1:
            self.anim.start()
        else:
            self.anim.stop()
            self.effect.setOpacity(1.0)


# ======================================================
# GroupCard (상한/하한 박스)
# ======================================================
class GroupCard(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QFrame {
                background-color:transparent;
                border-radius:14px;
                border:2px solid #2563EB;
            }
            QLabel {
                border:none;
                color:white;
                font-size:15pt;
                font-weight:bold;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(20)

        # 제목
        self.title_label = QLabel(title)
        layout.addWidget(self.title_label)

        # 경고/주의 카드
        self.card_red = MiniCard("Critical", "#f87171")
        self.card_yellow = MiniCard("Warning", "#facc15")

        layout.addWidget(self.card_red)
        layout.addWidget(self.card_yellow)

        layout.addStretch()

    def update(self, red_count: int, yellow_count: int):
        self.card_red.set_count(red_count)
        self.card_yellow.set_count(yellow_count)


# ======================================================
# FrameSummary (전체 Summary UI)
# ======================================================
class FrameSummary(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("background-color:#0F172A; border-radius:10px;")

        # 리스트 데이터
        self.upper_warnings = []
        self.upper_errors = []
        self.lower_warnings = []
        self.lower_errors = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 25, 20, 20)
        layout.setSpacing(25)

        # --------------------- 상한/하한 박스 ---------------------
        self.card_upper = GroupCard("Threshold Upper", self)
        self.card_lower = GroupCard("Threshold Lower", self)

        layout.addWidget(self.card_upper)
        layout.addWidget(self.card_lower)
        layout.addStretch()

        # --------------------- 음소거 버튼 ---------------------
        self.btn_mute = QPushButton("🔊")
        self.btn_mute.setStyleSheet("""
            QPushButton {
                background-color:#1E293B;
                color:white;
                border-radius:10px;
                font-size:20pt;
            }
        """)
        self.btn_mute.clicked.connect(self.toggle_mute)
        layout.addWidget(self.btn_mute)

        # --------------------- 임계값 설정 버튼 ---------------------
        self.btn_setting = QPushButton("Threshold Setting")
        self.btn_setting.setStyleSheet("""
            QPushButton {
                background-color:#2563EB;
                color:white;
                padding:15px 25px;
                border-radius:10px;
                font-size:14pt;
                font-weight:bold;
            }
            QPushButton:hover { background-color:#1E40AF; }
        """)
        self.btn_setting.clicked.connect(self.open_threshold_dialog)
        layout.addWidget(self.btn_setting)

        # --------------------- 클릭 이벤트 연결 ---------------------
        self.card_upper.card_red.mousePressEvent = lambda e: self.show_list("상한 경고", self.upper_errors)
        self.card_upper.card_yellow.mousePressEvent = lambda e: self.show_list("상한 주의", self.upper_warnings)
        self.card_lower.card_red.mousePressEvent = lambda e: self.show_list("하한 경고", self.lower_errors)
        self.card_lower.card_yellow.mousePressEvent = lambda e: self.show_list("하한 주의", self.lower_warnings)

    # --------------------------------------------------
    def show_list(self, title: str, dataset: list):
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.resize(450, 550)

        lst = QListWidget()

        # ★ 선택 색 제거 (클릭해도 색 변화 없음)
        lst.setStyleSheet("""
            QListWidget {
                background-color: #0F172A;
                color: white;
                font-size: 13pt;
                padding: 10px;
            }
            QListWidget::item {
                padding: 12px 8px;
            }
            QListWidget::item:selected {
                background-color: transparent;
                color: white;
                border: none;
            }
        """)

        for x in dataset:
            lst.addItem(x)

        lst.itemClicked.connect(lambda item: self.jump_to_device(item.text()))

        layout = QVBoxLayout(dlg)
        layout.addWidget(lst)

        dlg.exec()

    def jump_to_device(self, text: str):
        """
        예: '22GHz Receiver - RF_LO: -97.0'
        → 장비명 = '22GHz Receiver'
        """

        # -----------------------
        # 1. 텍스트 파싱
        # -----------------------
        try:
            device_name = text.split(" - ")[0].strip()
        except:
            return

        # -----------------------
        # 2. Left 패널 객체 가져오기
        # -----------------------
        win: "MonitoringWindow" = self.window()
        if not hasattr(win, "frame_left"):
            return

        fl = win.frame_left

        # -----------------------
        # 3. 해당 장비 패널 펼치기
        # -----------------------
        if device_name in fl.device_widgets:
            info = fl.device_widgets[device_name]
            btn = info["button"]
            panel = info["panel"]

            # 패널이 닫혀 있다면 열기
            if not panel.isVisible():
                btn.setChecked(True)
                fl._reload_panel(device_name)
                panel.setVisible(True)

            # -----------------------
            # 4. 자동 스크롤
            # -----------------------
            fl.ensureWidgetVisible(panel)

        # -----------------------
        # 팝업 닫기
        # -----------------------
        # (필요하면 close() 추가)

    # --------------------------------------------------
    def update_alerts(self,
                      upper_warnings: list, upper_errors: list,
                      lower_warnings: list, lower_errors: list):

        self.upper_warnings = upper_warnings
        self.upper_errors = upper_errors
        self.lower_warnings = lower_warnings
        self.lower_errors = lower_errors

        self.card_upper.update(len(upper_errors), len(upper_warnings))
        self.card_lower.update(len(lower_errors), len(lower_warnings))

    # --------------------------------------------------
    def toggle_mute(self):
        win: "MonitoringWindow" = self.window()

        if not hasattr(win, "frame_left"):
            return

        fl = win.frame_left
        fl.sound_enabled = not fl.sound_enabled

        if fl.sound_enabled:
            self.btn_mute.setText("🔊")
            fl.last_alarm = 0
            fl.update_all_thresholds()

            # Summary UI도 새로 반영
            self.update_alerts(
                self.upper_warnings, self.upper_errors,
                self.lower_warnings, self.lower_errors
            )
        else:
            self.btn_mute.setText("🔇")
            fl.alarm.stop()

    # --------------------------------------------------
    def open_threshold_dialog(self):
        dlg = ThresholdDialog(parent=self.window())
        dlg.exec()

        win: "MonitoringWindow" = self.window()

        if hasattr(win, "frame_left"):
            win.frame_left.thresholds.load()
            win.frame_left.refresh_expanded()
