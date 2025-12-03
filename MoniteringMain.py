import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import QTimer
from datetime import datetime, UTC

from Monitering_Ui.Mframe_top import FrameTop
from Monitering_Ui.Mframe_summary import FrameSummary
from Monitering_Ui.Mframe_left import MFrameLeft

from db_manager import get_connection


class MonitoringWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VLBI Real-Time Monitoring")
        self.setStyleSheet("background-color:#0F172A;")

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # ---------------------------
        # TOP BAR
        # ---------------------------
        self.frame_top = FrameTop(parent=self)
        main_layout.addWidget(self.frame_top, stretch=1)

        # ---------------------------
        # SUMMARY BAR
        # ---------------------------
        self.frame_summary = FrameSummary(parent=self)
        main_layout.addWidget(self.frame_summary, stretch=1)

        # ---------------------------
        # CENTER (LEFT ONLY)
        # ---------------------------
        center_layout = QHBoxLayout()
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(5)
        main_layout.addLayout(center_layout, stretch=8)

        self.frame_left = MFrameLeft()
        center_layout.addWidget(self.frame_left, stretch=1)

        # Summary 연결
        QTimer.singleShot(0, lambda: setattr(self.frame_left, "summary", self.frame_summary))
        QTimer.singleShot(10, lambda: self.frame_left.update_all_thresholds())

        # ---------------------------
        # TIMER
        # ---------------------------
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer_tick)
        self.timer.start(30_000)

        # Initial tick
        self.on_timer_tick()

    # ==================================================================
    # 통신 상태 체크 - (UTC DeprecationWarning 제거)
    # ==================================================================
    def check_connection_status(self):
        try:
            conn = get_connection(readonly=True)
            cur = conn.cursor()

            cur.execute("""
                SELECT Parsed_at
                FROM _Parsing_history_
                ORDER BY Parsed_at DESC
                LIMIT 1
            """)
            row = cur.fetchone()
            conn.close()

            if not row:
                return False

            last_time_str = row[0]

            # DB 값은 timezone 정보 없이 저장되어 있으므로 UTC timezone 부여
            last_dt = datetime.fromisoformat(last_time_str).replace(tzinfo=UTC)

            # 현재 시간 (UTC timezone-aware)
            now_utc = datetime.now(UTC)

            diff = now_utc - last_dt

            # 최근 60초 안에 데이터 있으면 정상
            return diff.total_seconds() < 60

        except Exception:
            return False

    # ==================================================================
    # 주기 갱신
    # ==================================================================
    def on_timer_tick(self):
        self.frame_left.update_all_thresholds()
        self.frame_left.refresh_expanded()

        # ---------------------------
        # 통신 상태 아이콘 갱신
        # ---------------------------
        ok = self.check_connection_status()
        self.frame_top.set_comm_status(ok)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MonitoringWindow()
    QTimer.singleShot(0, win.showMaximized)
    sys.exit(app.exec())
