import os
from PyQt6.QtWidgets import QLabel, QFrame, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QPixmap


class FrameTop(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgb(15,23,42); border-radius: 10px;")

        top_layout = QHBoxLayout(self)
        top_layout.setContentsMargins(10, 5, 10, 5)
        top_layout.setSpacing(10)

        # ------------------------------------
        # Left Image (VLBI antenna logo etc)
        # ------------------------------------
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

        top_layout.addWidget(
            label_image,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        # ------------------------------------
        # Titles
        # ------------------------------------
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        label_title = QLabel("측지 VLBI 시스템 모니터링")
        label_title.setStyleSheet("color:#38bdf8; font-weight:bold; font-size:23pt;")

        label_subtitle = QLabel("Geodetic VLBI System Monitoring")
        label_subtitle.setStyleSheet("color:#94a3b8; font-size:16pt;")

        title_layout.addWidget(label_title)
        title_layout.addWidget(label_subtitle)

        top_layout.addLayout(title_layout, stretch=1)

        # ------------------------------------
        # TIME LABEL (KST / UTC)
        # ------------------------------------
        self.time_label = QLabel()
        self.time_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.time_label.setStyleSheet(
            "color:white; font-size:12pt; font-weight:bold;"
        )

        time_layout = QVBoxLayout()
        time_layout.addWidget(
            self.time_label,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        top_layout.addLayout(time_layout)

        # ------------------------------------
        # COMMUNICATION STATUS ICON (On/Off)
        # ------------------------------------
        self.icon_comm = QLabel()
        self.icon_comm.setFixedSize(36, 36)

        pix = QPixmap("image/antenna_on.png").scaled(
            36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.icon_comm.setPixmap(pix)

        top_layout.addWidget(
            self.icon_comm,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        # Timer for clock tick
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    # ==================================================================
    # TIME UPDATE
    # ==================================================================
    def update_time(self):
        now_utc = QDateTime.currentDateTimeUtc()
        now_kst = now_utc.addSecs(9 * 3600)

        kst_str = now_kst.toString("yyyy-MM-dd hh:mm:ss")
        utc_str = now_utc.toString("yyyy-MM-dd hh:mm:ss")

        # 글자 크기 16pt, 줄 간격 추가(line-height)
        self.time_label.setStyleSheet("""
            color: white;
            font-size: 16pt;
            font-weight: bold;
            line-height: 140%;
        """)

        # KST / UTC 사이 한 줄 간격 추가
        self.time_label.setText(
            f"(KST) {kst_str}\n\n"
            f"(UTC) {utc_str}"
        )
    # ==================================================================
    # COMMUNICATION ICON CHANGE
    # ==================================================================
    def set_comm_status(self, ok: bool):
        img = "image/antenna_on.png" if ok else "image/antenna_off.png"

        pix = QPixmap(img).scaled(
            36, 36,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.icon_comm.setPixmap(pix)
