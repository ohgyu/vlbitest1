# DashBoard_Ui/frame_center.py
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QDateTimeEdit, QDialog
from PyQt6.QtCore import Qt, QDateTime, QUrl, QTimer
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib import rc
from db_manager import get_connection
from datetime import datetime, timedelta
import random
import numpy as np


rc("font", family="Malgun Gothic")


class CustomRangeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("기간 설정")
        self.setFixedSize(300, 120)
        layout = QVBoxLayout(self)

        # 시작일
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(QLabel("시작:"))
        self.start_edit = QDateTimeEdit(QDateTime.currentDateTime().addDays(-1))
        self.start_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.start_edit.setCalendarPopup(True)
        h_layout1.addWidget(self.start_edit)
        layout.addLayout(h_layout1)

        # 종료일
        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(QLabel("끝:"))
        self.end_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.end_edit.setCalendarPopup(True)
        h_layout2.addWidget(self.end_edit)
        layout.addLayout(h_layout2)

        # 확인/취소 버튼
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("확인")
        cancel_btn = QPushButton("취소")
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def get_range(self):
        return (
            self.start_edit.dateTime().toPyDateTime(),
            self.end_edit.dateTime().toPyDateTime(),
        )


class FrameCenter(QFrame):
    def __init__(self, frame_right=None, parent=None):
        super().__init__(parent)
        self.frame_right = frame_right
        self.setStyleSheet("background-color:#0F172A;")
        self.selected_parents = []
        self.time_range = "7일"
        self.initial_load = True  # ✅ 초기에만 특수 줌 로직 적용
        self.threshold_values = None
        self.lines = {}
        self.alarm_active = False
        self.alarm_cooldown = False

        self.menu_lists = {
            "2GHz 수신기 상태 모니터": [
                "Normal Temperature",
                "LNA Monitor",
                "Cryogenic Temperature",
            ],
            "8GHz 수신기 상태 모니터": [
                "Normal Temperature",
                "LNA Monitor",
                "Cryogenic Temperature",
            ],
            "22GHz 수신기 상태 모니터": [
                "Normal Temperature",
                "LNA Monitor",
                "Cryogenic Temperature",
            ],
            "43GHz 수신기 상태 모니터": [
                "Normal Temperature",
                "LNA Monitor",
                "Cryogenic Temperature",
            ],
            "S/X 다운 컨버터": ["S", "X1", "X2"],
            "K 다운 컨버터": ["K1", "K2", "K3", "K4"],
            "Q 다운 컨버터": ["Q1", "Q2", "Q3", "Q4"],
            "Video Converter 1": [
                "CH1",
                "CH2",
                "CH3",
                "CH4",
                "CH5",
                "CH6",
                "CH7",
                "CH8",
            ],
            "Video Converter 2": [
                "CH9",
                "CH10",
                "CH11",
                "CH12",
                "CH13",
                "CH14",
                "CH15",
                "CH16",
            ],
            "IF Selector": [
                "CH1",
                "CH2",
                "CH3",
                "CH4",
                "CH5",
                "CH6",
                "CH7",
                "CH8",
                "CH9",
                "CH10",
                "CH11",
                "CH12",
                "CH13",
                "CH14",
                "CH15",
                "CH16",
            ],
        }

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # 상단 영역
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(12)


        layout.addWidget(top_widget)

        # 그래프 영역
        self.figure = Figure(facecolor="#1E293B")
        self.canvas = FigureCanvas(self.figure)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet(
            """
            QToolBar { background-color: #1E293B; border: none; }
            QToolButton { color: white; }
        """
        )
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, stretch=1)

        self.canvas.mpl_connect("button_press_event", self.on_graph_click)

        # 상단 버튼
        top_layout.addStretch()

        button_names = ["6시간", "24시간", "7일", "기간설정", "보고서"]
        self.time_buttons = {}

        for name in button_names:
            btn = QPushButton(name)
            btn.setStyleSheet(
                """
                QPushButton {
                    background-color:#2563EB;
                    color:white;
                    border-radius:6px;
                    padding:4px 10px;
                    font-size:10pt;
                }
                QPushButton:hover {
                    background-color:#1D4ED8;
                }
            """
            )
            btn.setFixedHeight(28)
            btn.setFixedWidth(70)
            top_layout.addWidget(btn)
            self.time_buttons[name] = btn

            if name == "보고서":
                btn.clicked.connect(self.generate_report)
            else:
                btn.clicked.connect(lambda checked, n=name: self.change_time_range(n))

        # 초기 그래프
        self.update_graph()

        # ----------------------------------------
        # 실시간 전체 데이터 로딩 타이머 (30초마다 1회 SELECT)
        # ----------------------------------------
        self.realtime_data = None  # 메모리 캐싱용 변수

        self.realtime_timer = QTimer()
        self.realtime_timer.setInterval(30000)  # 30초
        self.realtime_timer.timeout.connect(self.fetch_realtime_data)
        self.realtime_timer.start()

        # 시작할 때 1회 로드
        self.realtime_data = []  # 그래프에 빈 데이터
        self.update_graph()

    # -----------------------------------------------------
    # 보고서 생성
    # -----------------------------------------------------
    def generate_report(self):
        if not self.selected_parents:
            print("선택된 항목이 없습니다.")
            return

        from PyQt6.QtWidgets import QFileDialog
        from matplotlib.backends.backend_pdf import PdfPages
        import matplotlib.pyplot as plt

        file_path, _ = QFileDialog.getSaveFileName(
            self, "보고서 저장", "", "PDF 파일 (*.pdf)"
        )
        if not file_path:
            return

        with PdfPages(file_path) as pdf:
            fig = plt.figure(figsize=(10, 6), facecolor="#1E293B")

            n = len(self.selected_parents)
            if n == 1:
                ax_list = [fig.add_subplot(111)]
            elif n == 2:
                ax_list = [fig.add_subplot(2, 1, i + 1) for i in range(2)]
            else:
                ax_list = [fig.add_subplot(2, 2, i + 1) for i in range(n)]

            colors = [
                "skyblue",
                "orange",
                "lime",
                "violet",
                "red",
                "yellow",
                "cyan",
                "magenta",
            ]

            now = datetime.now()
            x = [now - timedelta(hours=i) for i in reversed(range(7 * 24))]

            for idx, parent in enumerate(self.selected_parents):
                ax = ax_list[idx]
                children = self.menu_lists.get(parent, [])
                y_all = []

                for cidx, child in enumerate(children):
                    y = [random.uniform(5, 20) for _ in x]
                    y_all.extend(y)
                    ax.plot(x, y, label=child, color=colors[cidx % len(colors)])

                if y_all:
                    avg = float(np.mean(y_all))
                    max_v = float(np.max(y_all))
                    min_v = float(np.min(y_all))
                    stats_text = f"평균: {avg:.2f}, 최대: {max_v:.2f}, 최소: {min_v:.2f}"
                    ax.text(
                        0.95,
                        0.95,
                        stats_text,
                        transform=ax.transAxes,
                        color="white",
                        fontsize=9,
                        verticalalignment="top",
                        horizontalalignment="right",
                        bbox=dict(facecolor="black", alpha=0.3, pad=4),
                    )

                ax.set_facecolor("#1E293B")
                ax.tick_params(colors="white")
                ax.spines["bottom"].set_color("white")
                ax.spines["left"].set_color("white")
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
                ax.legend(facecolor="#1E293B", labelcolor="white")

                if n >= 3:
                    for label in ax.get_xticklabels():
                        label.set_rotation(45)
                        label.set_horizontalalignment("right")

            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        print(f"보고서 저장 완료: {file_path}")

    def fetch_realtime_data(self):
        """
        30초마다 1번 전체 데이터를 SELECT해서
        self.realtime_data 에 저장.
        update_graph()는 이 메모리 데이터만 사용하여 DB를 안 건드림.
        """
        try:
            conn = get_connection(readonly=True)  # 🔥 여기만 바뀜
            cur = conn.cursor()

            cur.execute("""
                SELECT datetime, NormalTemp_RF
                FROM frontend_2ghz
                WHERE datetime >= DATETIME('now', '-24 hours')
                ORDER BY datetime ASC
            """)

            self.realtime_data = cur.fetchall()

            conn.close()


        except Exception as e:

            print("[DB ERROR] fetch_realtime_data 실패:", e)

            # realtime_data가 None이면 그래프 자체가 안 보이므로 빈 데이터라도 넣어줌

            self.realtime_data = []

        # 데이터 로딩 성공 → 그래프 갱신
        self.update_graph()

        # 이벤트 로그 갱신
        if self.frame_right:
            self.frame_right.update_event_logs(self.realtime_data)

    # -----------------------------------------------------
    # 선택/그래프
    # -----------------------------------------------------
    def toggle_parent(self, parent_name):
        if parent_name in self.selected_parents:
            self.selected_parents.remove(parent_name)
        else:
            if len(self.selected_parents) < 4:
                self.selected_parents.append(parent_name)

        QTimer.singleShot(300, self.update_graph)

    def show_child_graph(self, parent, child):
        ax = self.figure.add_subplot(111)

        if self.realtime_data is None:
            print("실시간 데이터가 없습니다.")
            return

        # X축
        x = []
        for row in self.realtime_data:
            try:
                x.append(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"))
            except:
                continue

        # Y축
        child_column_map = {
            "Normal Temperature": 1
        }

        if child in child_column_map:
            col_idx = child_column_map[child]
            y = [float(row[col_idx]) if row[col_idx] is not None else np.nan
                 for row in self.realtime_data]
        else:
            # DB 없는 child → 랜덤 데이터
            y = [random.uniform(5, 20) for _ in x]

        # 그래프 그리기
        ax.plot(x, y, label=child, color="skyblue")

        # 제목
        ax.set_title(
            f"{parent} : {child}",
            color="cyan",
            fontsize=14,
            pad=10,
            fontweight="bold",
        )

        # 임계값
        # 임계값
        if (
                self.threshold_values
                and parent in self.threshold_values
                and child in self.threshold_values[parent]
        ):
            th = self.threshold_values[parent][child]
            caution = th.get("caution")
            warning = th.get("warning")

            if caution is not None:
                ax.axhline(y=caution, color="yellow", linestyle="--", linewidth=1.5, alpha=0.8)

            if warning is not None:
                ax.axhline(y=warning, color="red", linestyle="--", linewidth=1.5, alpha=0.8)

        # 오른쪽 통계
        if self.frame_right:
            self.frame_right.update_stats(y)

        # 스타일
        ax.set_facecolor("#1E293B")
        ax.tick_params(colors="white")
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
        ax.legend(facecolor="#1E293B", labelcolor="white")

        self.canvas.draw()

    def update_graph(self):
        n = len(self.selected_parents)

        # 데이터가 없는 경우 → 그래프 초기화
        if n == 0 or not hasattr(self, "realtime_data") or self.realtime_data is None:
            self.figure.clear()
            if self.frame_right:
                self.frame_right.update_stats([])
            self.canvas.draw()
            return

        # 서브플롯 개수 결정
        if n == 1:
            axs = [self.figure.add_subplot(111)]
        elif n == 2:
            axs = [self.figure.add_subplot(2, 1, i + 1) for i in range(2)]
        else:
            axs = [self.figure.add_subplot(2, 2, i + 1) for i in range(n)]

        colors = ["skyblue", "orange", "lime", "violet", "red", "yellow", "cyan", "magenta"]
        all_y_values = []
        self.ax_titles = {}
        self.lines = {}

        # realtime_data 구조 예:
        # row = (datetime_str, NormalTemp_RF, LNA, Cryo)
        # index 0 = datetime, index1~3 = child 값

        # 1) X축(time) 준비
        x = []
        for row in self.realtime_data:
            try:
                x.append(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"))
            except:
                continue

        # 2GHz 수신기용 child 순서
        # (다른 parent는 아직 미구현이므로 너 상황에 맞게 확장 가능)
        child_column_map = {
            "Normal Temperature": 1
        }

        for idx, parent in enumerate(self.selected_parents):
            ax = axs[idx]

            # 제목
            ax.set_title(parent, color="white", fontsize=14, pad=10, fontweight="bold")
            self.ax_titles[ax] = parent

            children = self.menu_lists.get(parent, [])

            # 자식별 그래프
            for cidx, child in enumerate(children):

                # 2) DB 접근 제거 → 메모리(self.realtime_data)에서 값 가져오기
                if child in child_column_map:
                    col_idx = child_column_map[child]
                    y = [float(row[col_idx]) if row[col_idx] is not None else np.nan
                         for row in self.realtime_data]
                else:
                    # 미구현 child → 랜덤 표시
                    y = [random.uniform(5, 20) for _ in x]

                # 통계용 전체 저장
                all_y_values.extend(y)

                # 그래프 그리기
                line, = ax.plot(x, y, label=child, color=colors[cidx % len(colors)])
                self.lines[(parent, child)] = line

                # Warning 임계값 체크 (알람 호출 완전 비활성화)
                if (
                        self.threshold_values
                        and parent in self.threshold_values
                        and child in self.threshold_values[parent]
                ):
                    th = self.threshold_values[parent][child]
                    warning = th.get("warning")

            # 임계값 표시
            if (
                    self.threshold_values
                    and parent in self.threshold_values
                    and "__parent__" in self.threshold_values[parent]
            ):
                th = self.threshold_values[parent]["__parent__"]
                caution = th.get("caution")
                warning = th.get("warning")

                if caution is not None:
                    ax.axhline(y=caution, color="yellow", linestyle="--", linewidth=2)
                if warning is not None:
                    ax.axhline(y=warning, color="red", linestyle="--", linewidth=2)

            # 스타일
            ax.set_facecolor("#1E293B")
            ax.tick_params(colors="white")
            ax.spines['bottom'].set_color("white")
            ax.spines['left'].set_color("white")
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
            ax.legend(facecolor="#1E293B", labelcolor="white")

        # 오른쪽 패널 통계
        if self.frame_right:
            self.frame_right.update_stats(all_y_values)

        self.ax_list = axs
        self.apply_time_zoom(redraw=False)
        self.canvas.draw()

    def play_alarm(self):
        # 🔴 임시: 알람 완전 비활성화 (소리/타이머 모두 OFF)
        #       → Crash 원인 범위 좁히기 위해 사용
        print("[ALARM] (disabled) Warning threshold exceeded!")

    def stop_alarm(self):
        # 🔴 더 이상 아무 것도 하지 않음
        print("[ALARM] (disabled) stop_alarm called")

    def reset_alarm_cooldown(self):
        # 🔴 더 이상 아무 것도 하지 않음
        print("[ALARM] (disabled) cooldown reset")

    # -----------------------------------------------------
    # 시간 범위 줌
    # -----------------------------------------------------
    def change_time_range(self, range_name):
        if range_name == "기간설정":
            self.realtime_timer.stop()

            dlg = CustomRangeDialog(self)
            if dlg.exec():
                self.custom_start, self.custom_end = dlg.get_range()
            else:
                return
        else:
            # 🔥 기간설정 종료 → 실시간 재시작
            self.realtime_timer.start()
        self.time_range = range_name
        self.apply_time_zoom(redraw=True)

    def apply_time_zoom(self, redraw=True):
        axes = self.figure.get_axes()
        if not axes:
            return

        now = datetime.now()

        if self.initial_load:
            start = now - timedelta(days=7)
            major = mdates.DayLocator(interval=1)  # 1일 단위로 라벨 표시

            for ax in axes:
                ax.set_xlim(start, now)
                ax.xaxis.set_major_locator(major)
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
                for lbl in ax.get_xticklabels():
                    lbl.set_rotation(45)
                    lbl.set_horizontalalignment("right")

            self.initial_load = False
            if redraw:
                self.canvas.draw()
            return

        if self.time_range == "6시간":
            start = now - timedelta(hours=6)
            major = mdates.HourLocator(interval=1)
        elif self.time_range == "24시간":
            start = now - timedelta(hours=24)
            major = mdates.HourLocator(interval=1)
        elif self.time_range == "7일":
            start = now - timedelta(days=7)
            major = mdates.DayLocator(interval=1)
        elif self.time_range == "기간설정" and hasattr(self, "custom_start"):
            start = self.custom_start
            now = self.custom_end
            diff = now - start
            if diff.days >= 7:
                major = mdates.DayLocator(interval=1)
            elif diff.days >= 1:
                major = mdates.HourLocator(interval=6)
            else:
                major = mdates.HourLocator(interval=1)
        else:
            start = now - timedelta(days=7)
            major = mdates.HourLocator(interval=1)

        for ax in axes:
            ax.set_xlim(start, now)
            ax.xaxis.set_major_locator(major)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
            for lbl in ax.get_xticklabels():
                lbl.set_rotation(45)
                lbl.set_horizontalalignment("right")

        if redraw:
            self.canvas.draw()

    def set_thresholds(self, threshold_values):
        self.threshold_values = threshold_values
        self.update_graph()

    def on_graph_click(self, event):
        if event.inaxes is None:
            return
        if not hasattr(self, "ax_list"):
            return

        clicked_ax = event.inaxes

        # 어떤 그래프인지 찾기
        try:
            clicked_index = self.ax_list.index(clicked_ax)
        except ValueError:
            return

        # 1) 클릭되면 → 모든 그래프 테두리 리셋
        for ax in self.ax_list:
            for spine in ax.spines.values():
                spine.set_color("white")
                spine.set_linewidth(1)

        # 2) 클릭된 그래프만 강조
        for spine in clicked_ax.spines.values():
            spine.set_color("cyan")
            spine.set_linewidth(3)

        # 3) 제목은 절대로 변경하지 않음
        # (아무 것도 안 함)

        # 4) 오른쪽 통계 업데이트 (child 전체 합산)
        all_y = []
        for line in clicked_ax.get_lines():
            all_y.extend(list(line.get_ydata()))

        if self.frame_right:
            self.frame_right.update_stats(all_y)

        self.canvas.draw()
