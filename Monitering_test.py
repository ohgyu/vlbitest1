import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame,
    QPushButton, QProgressBar, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QFont, QColor, QPainter, QPixmap


# 🔹 상태 LED
class StatusIndicator(QFrame):
    def __init__(self, color=QColor("#22c55e"), size=14, parent=None):
        super().__init__(parent)
        self.color = color
        self.size = size
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self.color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, self.size, self.size)


# 🔹 상단 헤더
class HeaderBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #0F172A; color: white;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)

        # 로고 + 타이틀
        logo = QLabel()
        pixmap = QPixmap("C:/Work/VLBI/VLBIGUI/image/antenna.png")
        logo.setPixmap(
            pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        title_box = QVBoxLayout()
        title_box.setContentsMargins(0, 0, 0, 0)
        title_box.setSpacing(0)
        title_kr = QLabel("우주측지 관측센터 VLBI 모니터링 시스템")
        title_kr.setFont(QFont("맑은 고딕", 23, QFont.Weight.Bold))
        title_kr.setStyleSheet("color: #38bdf8;")
        title_en = QLabel("SPACE GEODETIC OBSERVATION CENTER VLBI MONITORING SYSTEM")
        title_en.setStyleSheet("color: #94a3b8; font-size:16pt;")
        title_box.addWidget(title_kr)
        title_box.addWidget(title_en)

        # QHBoxLayout 대신 QFrame으로 묶기
        left_frame = QFrame()
        left_layout = QHBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        left_layout.addWidget(logo)
        left_layout.addLayout(title_box)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # 중앙: 시간
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont("Consolas", 12))
        self.time_label.setStyleSheet("color: #e0e0e0;")

        # 우측: 상태 카운트
        self.error_label = self._make_status("에러", "#ef4444")
        self.warn_label = self._make_status("경고", "#facc15")
        self.normal_label = self._make_status("정상", "#22c55e")
        right_box = QHBoxLayout()
        right_box.addWidget(self.error_label)
        right_box.addWidget(self.warn_label)
        right_box.addWidget(self.normal_label)
        right_box.setSpacing(10)

        # 레이아웃 순서 재조정
        layout.addWidget(left_frame)
        layout.addStretch()
        layout.addLayout(right_box)
        layout.addSpacing(140)  # ← 여기서 간격 추가
        layout.addWidget(self.time_label)

        # 타이머
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.update_time()

    def _make_status(self, label, color):
        box = QFrame()
        layout = QHBoxLayout(box)
        indicator = StatusIndicator(QColor(color), 14)
        text = QLabel(str(random.randint(0, 99)))
        text.setStyleSheet(f"color: {color}; font: bold 15pt 'Consolas'; margin-left:5px;")
        layout.addWidget(indicator)
        layout.addWidget(text)
        return box

    def update_time(self):
        now_utc = QDateTime.currentDateTimeUtc()
        now_kst = now_utc.addSecs(9 * 3600)  # UTC+9 = 한국 시간
        self.time_label.setText(
            f"{now_utc.toString('hh:mm:ss')} UTC\n"
            f"{now_kst.toString('hh:mm:ss')} KST (UTC+9)\n"
            f"{now_utc.toString('yyyy-MM-dd')}"
        )


# 🔹 GHz 카드
class GHzCard(QFrame):
    def __init__(self, ghz_label, status_color="#22c55e"):
        super().__init__()
        self.setStyleSheet("background-color: #1E293B; border-radius: 10px;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # 타이틀
        title_layout = QHBoxLayout()
        title = QLabel(f"{ghz_label} GHz 수신기 상태 모니터")
        title.setFont(QFont("맑은 고딕", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #38bdf8;")
        icon = QLabel("✅" if status_color == "#22c55e" else ("⚠️" if status_color == "#facc15" else "❌"))
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(icon)
        main_layout.addLayout(title_layout)

        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setStyleSheet("border:none;")
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(15, 10, 15, 10)
        scroll_layout.setSpacing(8)

        items = self._make_items(ghz_label)
        for label_text, sub_label, value in items:
            row = QHBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet("color:#9CA3AF; font:14pt '맑은 고딕';")
            sub_label_widget = QLabel(sub_label)
            sub_label_widget.setStyleSheet("color:#9CA3AF; font:12pt '맑은 고딕';")
            value_widget = QLabel(f"{value:.2f}")
            value_widget.setStyleSheet("color:white; font: bold 14pt 'Consolas';")
            row.addWidget(label, 2)
            row.addWidget(sub_label_widget, 1)
            row.addWidget(value_widget, 1)
            scroll_layout.addLayout(row)

        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def _make_items(self, ghz_label):
        import random
        if ghz_label == "2":
            return [
                ("Normal Temperature (C)", "RF", random.uniform(20, 40)),
                ("Load", "", random.uniform(0, 100)),
                ("LNA Monitor (V,A)", "LHCP Vd", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "LHCP Id", random.uniform(0, 1)),
                ("LNA Monitor (V,A)", "RHCP Vd", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "RHCP Id", random.uniform(0, 1)),
                ("Cryogenic Temperature (K)", "Cold", random.uniform(15, 300)),
                ("Cryogenic Temperature (K)", "Shield Box", random.uniform(15, 300)),
                ("Pressure Sensor (torr)", "CH1", random.uniform(0, 5)),
                ("RF out Power (dBm)", "RHCP", random.uniform(-30, 30)),
                ("RF out Power (dBm)", "LHCP", random.uniform(-30, 30)),
            ]
        elif ghz_label == "8":
            return [
                ("Normal Temperature (C)", "RF", random.uniform(20, 40)),
                ("Load", "", random.uniform(0, 100)),
                ("LNA Monitor (V,A)", "LHCP Vg1", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "LHCP Vg2", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "LHCP Vd", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "LHCP Id", random.uniform(0, 1)),
                ("LNA Monitor (V,A)", "RHCP Vg1", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "RHCP Vg2", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "RHCP Vd", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "RHCP Id", random.uniform(0, 1)),
                ("Cryogenic Temperature (K)", "Cold", random.uniform(15, 300)),
                ("Cryogenic Temperature (K)", "Shield Box", random.uniform(15, 300)),
                ("Pressure Sensor (torr)", "CH1", random.uniform(0, 5)),
                ("RF out Power (dBm)", "RHCP", random.uniform(-30, 30)),
                ("RF out Power (dBm)", "LHCP", random.uniform(-30, 30)),
            ]
        elif ghz_label == "22":
            return [
                ("Normal Temperature (C)", "RF", random.uniform(20, 40)),
                ("Normal Temperature (C)", "LO", random.uniform(20, 40)),
                ("LNA Monitor (V,A)", "LHCP Vg1", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "LHCP Vg2", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "LHCP Vd", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "LHCP Id", random.uniform(0, 1)),
                ("LNA Monitor (V,A)", "RHCP Vg1", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "RHCP Vg2", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "RHCP Vd", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "RHCP Id", random.uniform(0, 1)),
                ("Cryogenic Temperature (K)", "Cold", random.uniform(15, 300)),
                ("Cryogenic Temperature (K)", "Shield Box", random.uniform(15, 300)),
                ("Pressure Sensor (torr)", "CH1", random.uniform(0, 5)),
                ("RF out Power (dBm)", "RF", random.uniform(-30, 30)),
                ("RF out Power (dBm)", "LO", random.uniform(-30, 30)),
            ]
        else:  # 43GHz
            return [
                ("Normal Temperature (C)", "RF", random.uniform(20, 40)),
                ("Normal Temperature (C)", "LO", random.uniform(20, 40)),
                ("LNA Monitor (V,A)", "LHCP Vg1", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "LHCP Vg2", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "LHCP Vd", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "LHCP Id", random.uniform(0, 1)),
                ("LNA Monitor (V,A)", "RHCP Vg1", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "RHCP Vg2", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "RHCP Vd", random.uniform(0, 2)),
                ("LNA Monitor (V,A)", "RHCP Id", random.uniform(0, 1)),
                ("Cryogenic Temperature (K)", "Cold", random.uniform(15, 300)),
                ("Cryogenic Temperature (K)", "Shield Box", random.uniform(15, 300)),
                ("Pressure Sensor (torr)", "CH1", random.uniform(0, 5)),
                ("RF out Power (dBm)", "RHCP", random.uniform(-30, 30)),
                ("RF out Power (dBm)", "LHCP", random.uniform(-30, 30)),
                ("RF out Power (dBm)", "LO", random.uniform(-30, 30)),
            ]


# 🔹 시스템 신호 흐름도
class SystemFlow(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            """
            background-color: #0F172A; color: white; border: none; border-radius: 0;
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 10)
        layout.setSpacing(0)

        # 🔹 1️⃣ 제목 + 구분선을 하나의 고정 상단 프레임으로 묶기
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        title = QLabel("시스템 신호 흐름도")
        title.setFont(QFont("맑은 고딕", 16, QFont.Weight.Bold))
        title.setStyleSheet("color:#38bdf8; background:transparent; border:none;")
        title.setFixedHeight(title.fontMetrics().height() + 4)
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        line.setFixedHeight(1)
        line.setStyleSheet("background-color:#38bdf8; margin:0;")
        header_layout.addWidget(title)
        header_layout.addWidget(line)
        layout.addWidget(header_frame, 0)  # ← stretch 0으로 고정

        # 🔹 2️⃣ 장비 아이템 그리드
        grid = QGridLayout()
        grid.setSpacing(12)
        items = [
            ["안테나", "Flat Mirror", "", ""],
            ["2/8GHz", "RHCP", "LNA", "CAL"],
            ["22GHz", "RHCP", "LNA", "CAL"],
            ["43GHz", "RHCP", "LNA", "CAL"],
            ["다운컨버터", "S/X", "K-Band", "Q-Band"],
            ["백엔드", "Video Conv 1", "Video Conv 2", ""],
            ["기록장치", "Mark 6-1", "Mark 6-2", ""],
            ["네트워크", "10G Switch", "Data Server", ""],
        ]
        standard_height = 50
        for r, row in enumerate(items):
            for c, text in enumerate(row):
                if not text:
                    continue
                btn = QLabel(text)
                btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
                if c == 0:
                    btn.setStyleSheet("""
                        background: transparent; border: none; color:white; font: bold 12pt '맑은 고딕'; padding: 8px;
                    """)
                else:
                    color = "#22c55e" if random.random() > 0.2 else "#ef4444"
                    btn.setStyleSheet(f"""
                        border:1px solid #38bdf8; border-radius:8px; background-color:{color}33; padding:12px; font: bold 12pt '맑은 고딕';
                    """)
                btn.setFixedHeight(standard_height)
                grid.addWidget(btn, r, c)

        # 🔹 아래쪽은 stretch 1로 남은 공간 다 차지하게
        grid_widget = QWidget()
        grid_widget.setLayout(grid)
        layout.addWidget(grid_widget, 1)


# 🔹 하단 상태바
class StatusBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color:#0F172A; color:white; border-top:1px solid #334155;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 5, 20, 5)
        lbl1 = QLabel("관측 대상: <b style='color:#38bdf8;'>3C273</b>")
        lbl2 = QLabel("세션: <b style='color:#38bdf8;'>R24045</b>")
        lbl3 = QLabel("남은 시간: <b style='color:#22c55e;'>02:34:15</b>")
        layout.addWidget(lbl1)
        layout.addWidget(lbl2)
        layout.addStretch()
        layout.addWidget(lbl3)
        btn1 = QPushButton("모니터링")
        btn2 = QPushButton("통계 대시보드")
        for b in (btn1, btn2):
            b.setStyleSheet(
                "background-color:#1E40AF; color:white; font-weight:bold; border-radius:8px; padding:5px 15px;")
        layout.addWidget(btn1)
        layout.addWidget(btn2)


# 🔹 메인 윈도우
class MonitoringDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("실시간 모니터링")
        self.setStyleSheet("background-color:#0F172A; color:white;")
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 8, 10, 8)

        # 상단
        header = HeaderBar()
        main_layout.addWidget(header)

        # 중앙
        center_layout = QHBoxLayout()
        left_panel = SystemFlow()
        right_panel = QGridLayout()
        cards = [
            GHzCard("2", "#22c55e"),
            GHzCard("8", "#22c55e"),
            GHzCard("22", "#facc15"),
            GHzCard("43", "#22c55e"),
        ]
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for card, pos in zip(cards, positions):
            right_panel.addWidget(card, *pos)

        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        center_layout.addWidget(left_panel, 4)
        center_layout.addWidget(right_widget, 6)
        main_layout.addLayout(center_layout, 1)

        # 하단
        status_bar = StatusBar()
        main_layout.addWidget(status_bar)


# ✅ 클래스 밖에서 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MonitoringDashboard()
    win.resize(1400, 800)
    win.show()
    sys.exit(app.exec())