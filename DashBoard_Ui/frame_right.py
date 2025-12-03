# FrameRight.py
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QWidget
)
from PyQt6.QtCore import QSize
import numpy as np


class FrameRight(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgb(15,23,42); border-radius:15px; border:1px solid #000081;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # ------------------------------
        # 통계 프레임
        # ------------------------------
        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet(
            "background-color:#0F172A; border-radius:10px; border:1px solid rgba(110,227,247,0.3);")
        self.stats_layout = QVBoxLayout(self.stats_frame)
        self.stats_layout.setContentsMargins(15, 15, 15, 15)
        self.stats_layout.setSpacing(8)
        self.stats_labels = {}

        stats_names = ["평균값", "최솟값", "최댓값", "표준편차", "안정도"]
        for name in stats_names:
            lbl = QLabel(f"{name}: -")
            lbl.setStyleSheet("color:white; font-size:12pt; font-weight:bold;")
            self.stats_layout.addWidget(lbl)
            self.stats_labels[name] = lbl

        # ------------------------------
        # Event Log 프레임
        # ------------------------------
        eventlog_frame = QFrame()
        eventlog_frame.setStyleSheet(
            "background-color:#0F172A; border-radius:10px; border:1px solid rgba(110,227,247,0.3);")
        eventlog_layout = QVBoxLayout(eventlog_frame)
        eventlog_layout.setContentsMargins(15, 15, 15, 15)
        eventlog_layout.setSpacing(8)

        log_title = QLabel("최근 경보 이력 (Event Log)")
        log_title.setStyleSheet("color:rgb(110,227,247); font-size:15pt; font-weight:bold;")
        eventlog_layout.addWidget(log_title)

        self.log_list = QListWidget()
        self.log_list.setStyleSheet("""
            QListWidget {background-color:#1E293B; color:white; border:1px solid rgba(110,227,247,0.3); 
                         border-radius:8px; font-size:11pt;}
            QListWidget::item {border-bottom:1px solid rgba(255,255,255,0.1); padding:8px;}
        """)
        eventlog_layout.addWidget(self.log_list)

        layout.addWidget(self.stats_frame, stretch=3)
        layout.addWidget(eventlog_frame, stretch=7)

    # ------------------------------
    # FrameCenter에서 호출하는 이벤트 로그 갱신 함수
    # ------------------------------
    def update_event_logs(self, realtime_data):
        """
        realtime_data = [
            ("2025-01-01 10:00:00", 10.5, 12.3, 5.5),
            ("2025-01-01 10:00:30", 10.8, 12.1, 5.7),
            ...
        ]
        """
        self.log_list.clear()

        if not realtime_data:
            self.log_list.addItem("데이터 없음")
            return

        # 최신 10개만 표시
        for row in realtime_data[-10:]:
            dt, normal, lna, cryo = row

            item_widget = QWidget()
            v_layout = QVBoxLayout(item_widget)
            v_layout.setContentsMargins(10, 8, 10, 8)

            lbl_time = QLabel(str(dt))
            lbl_time.setStyleSheet("color:skyblue; font-size:10pt; font-weight:bold;")

            msg = f"Normal={normal}, LNA={lna}, Cryo={cryo}"
            lbl_msg = QLabel(msg)
            lbl_msg.setStyleSheet("color:white; font-size:11pt; font-weight:bold;")

            v_layout.addWidget(lbl_time)
            v_layout.addWidget(lbl_msg)

            item = QListWidgetItem(self.log_list)
            item.setSizeHint(QSize(0, 75))
            self.log_list.addItem(item)
            self.log_list.setItemWidget(item, item_widget)

    # ------------------------------
    # 통계 패널 업데이트
    # ------------------------------
    def update_stats(self, data):
        if data is None or len(data) == 0:
            for key in self.stats_labels:
                self.stats_labels[key].setText(f"{key}: -")
            return

        mean_val = np.mean(data)
        min_val = np.min(data)
        max_val = np.max(data)
        std_val = np.std(data)
        stability = max_val - min_val

        self.stats_labels["평균값"].setText(f"평균값: {mean_val:.2f}")
        self.stats_labels["최솟값"].setText(f"최솟값: {min_val:.2f}")
        self.stats_labels["최댓값"].setText(f"최댓값: {max_val:.2f}")
        self.stats_labels["표준편차"].setText(f"표준편차: {std_val:.2f}")
        self.stats_labels["안정도"].setText(f"안정도: {stability:.2f}")
