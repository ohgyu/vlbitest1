# MoniteringMain.py
import sys
import os

# 현재 파일 위치를 sys.path에 추가 (패키지 인식용)
sys.path.append(os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import QTimer

from Monitering_Ui.Mframe_top import FrameTop
from Monitering_Ui.Mframe_summary import FrameSummary
from Monitering_Ui.Mframe_left import MFrameLeft
from Monitering_Ui.Mframe_eventlog import FrameEventLog


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

        # 상단바 (모니터링용 타이틀)
        self.frame_top = FrameTop(parent=self)
        main_layout.addWidget(self.frame_top, stretch=1)

        # 상단 Summary 바
        self.frame_summary = FrameSummary(parent=self)
        main_layout.addWidget(self.frame_summary, stretch=1)

        # 중앙 2분할 레이아웃 (좌: 실시간 리스트뷰, 우: EVENT LOG)
        center_layout = QHBoxLayout()
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(5)
        main_layout.addLayout(center_layout, stretch=8)

        # 좌측: 장비 아코디언 + 실시간 값 리스트
        self.frame_left = MFrameLeft()
        QTimer.singleShot(0, lambda: setattr(self.frame_left, "summary", self.frame_summary))

        # 초기 Summary 즉시 반영
        QTimer.singleShot(10, lambda: self.frame_left.update_all_thresholds())
        center_layout.addWidget(self.frame_left, stretch=6)

        # 우측: 이벤트 로그
        self.frame_eventlog = FrameEventLog()
        center_layout.addWidget(self.frame_eventlog, stretch=2)

        # 주기적 갱신 타이머 (30초)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer_tick)
        self.timer.start(30_000)

        # 초기 1회 갱신
        self.on_timer_tick()

        # Summary가 연결된 뒤 update_all_thresholds 즉시 실행
        QTimer.singleShot(30, lambda: self.frame_left.update_all_thresholds())

    def on_timer_tick(self):
        print("TIMER TICK")

        self.frame_left.update_all_thresholds()

        # 좌측: 펼쳐져 있는 장비들만 최신값 갱신
        self.frame_left.refresh_expanded()

        # 우측: ERROR 이벤트 로그 다시 로드
        self.frame_eventlog.reload_logs()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MonitoringWindow()

    # 첫 프레임 그려진 뒤에 최대화
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(0, win.showMaximized)

    sys.exit(app.exec())
