# DashBoard_Ui/frame_top.py
import os
from PyQt6.QtWidgets import QLabel, QPushButton, QFrame, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QPixmap


class FrameTop(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgb(15,23,42); border-radius: 10px;")

        # 향후 필요 시 center 접근용 (지금은 직접 사용하지 않음)
        self.frame_center = None

        top_layout = QHBoxLayout(self)
        top_layout.setContentsMargins(10, 5, 10, 5)
        top_layout.setSpacing(10)

        # 안테나 사진
        pixmap = QPixmap(r"C:\Work\VLBI\VLBIGUI\image\antenna.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                120, 120,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        label_image = QLabel()
        label_image.setPixmap(pixmap)
        label_image.setFixedSize(120, 120)
        top_layout.addWidget(label_image, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # 제목 영역
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        label_title = QLabel("우주측지 관측센터 VLBI 통계 대시보드")
        label_title.setStyleSheet("color:#38bdf8; font-weight:bold; font-size:23pt;")
        label_subtitle = QLabel("SPACE GEODETIC OBSERVATION CENTER VLBI STATISTICS DASHBOARD")
        label_subtitle.setStyleSheet("color:#94a3b8; font-size:16pt;")
        title_layout.addWidget(label_title)
        title_layout.addWidget(label_subtitle)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        top_layout.addLayout(title_layout, stretch=1)

        # 시간 레이블 (KST / UTC)
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.time_label.setStyleSheet("color:white; font-size:12pt; font-weight:bold;")

        time_layout = QVBoxLayout()
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        top_layout.addLayout(time_layout)

        # 타이머
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def update_time(self):
        now_utc = QDateTime.currentDateTimeUtc()
        now_kst = now_utc.addSecs(9 * 3600)

        kst_date = now_kst.toString("yyyy-MM-dd")
        kst_time = now_kst.toString("hh:mm:ss")
        utc_date = now_utc.toString("yyyy-MM-dd")
        utc_time = now_utc.toString("hh:mm:ss")

        self.time_label.setText(
            f"{kst_date} (KST)\n"
            f"{kst_time}\n"
            f"{utc_date} (UTC)\n"
            f"{utc_time}"
        )
