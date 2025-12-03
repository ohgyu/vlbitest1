from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QDateTimeEdit, QDialog, QSizePolicy, QFileDialog
)
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from PyQt6.QtCore import Qt, QDateTime
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        # Navigation Toolbar
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib import rc
from db_manager import get_connection
from datetime import datetime, timedelta
import numpy as np
import matplotlib as mpl
import os

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('MalgunGothic', 'C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MalgunGothic-Bold', 'C:/Windows/Fonts/malgunbd.ttf'))

# 한글 폰트
rc("font", family="Malgun Gothic")
mpl.rcParams['axes.unicode_minus'] = False

# ----------------------------------------------------------------------
#  DB 매핑: 좌측 메뉴 텍스트  →  테이블 / 컬럼명
# ----------------------------------------------------------------------
TABLE_MAP = {
    "2GHz 수신기 상태 모니터": {
        "table": "frontend_2ghz",
        "columns": {
            "Normal Temperature RF":           "NormalTemp_RF",
            "Normal Temperature Load":         "NormalTemp_Load",
            "LNA Monitor LHCP Vd":             "LNA_LHCP_Vd1",
            "LNA Monitor LHCP Id":             "LNA_LHCP_Id1",
            "LNA Monitor RHCP Vd":             "LNA_RHCP_Vd1",
            "LNA Monitor RHCP Id":             "LNA_RHCP_Id1",
            "Cryogenic Temperature Cold":      "Cryo_ColdPla",
            "Cryogenic Temperature Shild Box": "Cryo_ShieldBox",
            "Pressure Sensor CH1":             "Pressure",
            "RF out Power RHCP":               "RF_RHCP",
            "RF out Power LHCP":               "RF_LHCP",
        }
    },
    "8GHz 수신기 상태 모니터": {
        "table": "frontend_8ghz",
        "columns": {
            "Normal Temperature RF":           "NormalTemp_RF",
            "Normal Temperature Load":         "NormalTemp_Load",
            "LNA Monitor LHCP Vg1":            "LNA_LHCP_Vg1",
            "LNA Monitor LHCP Vg2":            "LNA_LHCP_Vg2",
            "LNA Monitor RHCP Vd":             "LNA_RHCP_Vd1",
            "LNA Monitor RHCP Id":             "LNA_RHCP_Id1",
            # ★ 오타 수정: NA_RHCP_Vg1/Vg2 → LNA_RHCP_Vg1/Vg2
            "LNA Monitor RHCP Vg1":            "LNA_RHCP_Vg1",
            "LNA Monitor RHCP Vg2":            "LNA_RHCP_Vg2",
            "LNA Monitor LHCP Vd":             "LNA_LHCP_Vd1",
            "LNA Monitor LHCP Id":             "LNA_LHCP_Id1",
            "Cryogenic Temperature Cold":      "Cryo_ColdPla",
            "Cryogenic Temperature Shild Box": "Cryo_ShieldBox",
            "Pressure Sensor CH1":             "Pressure",
            "RF out Power RHCP":               "RF_RHCP",
            "RF out Power LHCP":               "RF_LHCP",
        }
    },
    "22GHz 수신기 상태 모니터": {
        "table": "frontend_22ghz",
        "columns": {
            "Normal Temperature RF":           "NormalTemp_RF",
            "Normal Temperature LO":           "NormalTemp_Load",
            "LNA Monitor LHCP Vg1":            "LNA_LHCP_Vg1",
            "LNA Monitor LHCP Vg2":            "LNA_LHCP_Vg2",
            "LNA Monitor RHCP Vd":             "LNA_RHCP_Vd1",
            "LNA Monitor RHCP Id":             "LNA_RHCP_Id1",
            # ★ 오타 수정
            "LNA Monitor RHCP Vg1":            "LNA_RHCP_Vg1",
            "LNA Monitor RHCP Vg2":            "LNA_RHCP_Vg2",
            "LNA Monitor LHCP Vd":             "LNA_LHCP_Vd1",
            "LNA Monitor LHCP Id":             "LNA_LHCP_Id1",
            "Cryogenic Temperature Cold":      "Cryo_ColdPla",
            "Cryogenic Temperature Shild Box": "Cryo_ShieldBox",
            "Pressure Sensor CH1":             "Pressure",
            "RF out Power RF":                 "RF_RHCP",
            "RF out Power LO":                 "RF_Low",
        }
    },
    "43GHz 수신기 상태 모니터": {
        "table": "frontend_43ghz",
        "columns": {
            "Normal Temperature RF":           "NormalTemp_RF",
            "Normal Temperature LO":           "NormalTemp_Load",
            "LNA Monitor LHCP Vg1":            "LNA_LHCP_Vg1",
            "LNA Monitor LHCP Vg2":            "LNA_LHCP_Vg2",
            "LNA Monitor RHCP Vd":             "LNA_RHCP_Vd1",
            "LNA Monitor RHCP Id":             "LNA_RHCP_Id1",
            # ★ 오타 수정
            "LNA Monitor RHCP Vg1":            "LNA_RHCP_Vg1",
            "LNA Monitor RHCP Vg2":            "LNA_RHCP_Vg2",
            "LNA Monitor LHCP Vd":             "LNA_LHCP_Vd1",
            "LNA Monitor LHCP Id":             "LNA_LHCP_Id1",
            "Cryogenic Temperature Cold":      "Cryo_ColdPla",
            "Cryogenic Temperature Shild Box": "Cryo_ShieldBox",
            "Pressure Sensor CH1":             "Pressure",
            "RF out Power RHCP":               "RF_RHCP",
            "RF out Power LHCP":               "RF_LHCP",
            "RF out Power LO":                 "RF_Low",
        }
    },
    "S/X 다운 컨버터": {
        "table": "SXDown",
        "columns": {
            "S":  "SLEVEL",
            "X1": "X1LEVEL",
            "X2": "X2LEVEL",
        }
    },
    "K 다운 컨버터": {
        "table": "KDown",
        "columns": {
            "K1": "K1LEVEL",
            "K2": "K2LEVEL",
            "K3": "K3LEVEL",
            "K4": "K4LEVEL",
        }
    },
    "Q 다운 컨버터": {
        "table": "QDown",
        "columns": {
            "Q1": "Q1LEVEL",
            "Q2": "Q2LEVEL",
            "Q3": "Q3LEVEL",
            "Q4": "Q4LEVEL",
        }
    },
    # Video Converter 1: 실제 테이블 없음 → 그래프 없음 처리용
    "Video Converter 1": {
        "table": None,
        "columns": {}
    },
    # Video Converter 2: FrameLeft에서 CH9~CH16 사용
    "Video Converter 2": {
        "table": "VideoConverter2",
        "columns": {
            "CH9":  "CH9LEVEL",
            "CH10": "CH10LEVEL",
            "CH11": "CH11LEVEL",
            "CH12": "CH12LEVEL",
            "CH13": "CH13LEVEL",
            "CH14": "CH14LEVEL",
            "CH15": "CH15LEVEL",
            "CH16": "CH16LEVEL",
        }
    },
    # IF Selector: CH1~CH16
    "IF Selector": {
        "table": "IFselector",
        "columns": {
            **{f"CH{i}": f"CH{i}LEVEL" for i in range(1, 17)}
        }
    },
}


# ----------------------------------------------------------------------
# 기간 설정 다이얼로그
# ----------------------------------------------------------------------
class CustomRangeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("기간 설정")
        self.setFixedSize(320, 130)
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


# ----------------------------------------------------------------------
#  메인 센터 프레임
# ----------------------------------------------------------------------
class FrameCenter(QFrame):
    def __init__(self, parent=None, frame_right=None):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        self.setStyleSheet("background-color:#0F172A;")
        self.title_label = QLabel("")
        self.title_label.hide()
        self.selected_parents = []
        self.current_parent = None
        self.selected_children = {}
        self.time_range = "24시간"
        self.custom_start = None
        self.custom_end = None

        self.raw = {}

        # -----------------------------
        # 전체 레이아웃
        # -----------------------------
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # ------------------------------------------------
        # 상단 바 (제목 제거 + 아이콘 제거 + 버튼만 유지)
        # ------------------------------------------------
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(12)

        # 제목 제거 → 대신 위치용 stretch
        top_layout.addStretch(1)

        # 시간 범위 버튼들
        self.time_buttons = {}
        for name in ["6시간", "24시간", "7일", "30일", "기간설정"]:
            btn = QPushButton(name)
            btn.setFixedHeight(30)
            btn.setFixedWidth(70)
            btn.setStyleSheet(
                """
                QPushButton {
                    background-color:#1E293B;
                    color:white;
                    border-radius:8px;
                    padding:4px 10px;
                    font-size:10pt;
                }
                QPushButton:hover { background-color:#334155; }
                QPushButton:checked {
                    background-color:#2563EB;
                    font-weight:bold;
                }
                """
            )
            btn.setCheckable(True)
            self.time_buttons[name] = btn
            top_layout.addWidget(btn)
            btn.clicked.connect(self._make_time_range_handler(name))

        # 기본 체크
        self.time_buttons["24시간"].setChecked(True)

        # 새로고침 버튼
        self.refresh_btn = QPushButton("새로고침")
        self.refresh_btn.setFixedHeight(30)
        self.refresh_btn.setFixedWidth(90)
        self.refresh_btn.setStyleSheet(
            """
            QPushButton {
                background-color:#22C55E;
                color:white;
                border-radius:8px;
                padding:4px 12px;
                font-size:10pt;
                font-weight:bold;
            }
            QPushButton:hover { background-color:#16A34A; }
            """
        )
        self.refresh_btn.clicked.connect(self.refresh_all_data)
        top_layout.addWidget(self.refresh_btn)

        # 보고서 PDF 버튼
        self.report_pdf_btn = QPushButton("보고서 PDF")
        self.report_pdf_btn.setFixedHeight(30)
        self.report_pdf_btn.setFixedWidth(110)
        self.report_pdf_btn.setStyleSheet(
            """
            QPushButton {
                background-color:#6366F1;
                color:white;
                border-radius:8px;
                padding:4px 12px;
                font-size:10pt;
                font-weight:bold;
            }
            QPushButton:hover { background-color:#4F46E5; }
            """
        )
        self.report_pdf_btn.clicked.connect(self.save_pdf_report)
        top_layout.addWidget(self.report_pdf_btn)

        layout.addWidget(top_widget)

        # ------------------------------------------------
        # 그래프 영역 (툴바 삭제됨!)
        # ------------------------------------------------
        self.figure = Figure(facecolor="#0F172A")
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas, stretch=1)

        # ------------------------------------------------
        # 통계 패널
        # ------------------------------------------------
        self._init_stats_panel()
        layout.addWidget(self.stats_frame)

        # 그래프 클릭 이벤트
        self.ax_info = []
        self.canvas.mpl_connect("button_press_event", self.on_graph_click)

        # 초기 빈 그래프 표시
        self.update_graph()

    # ------------------------------------------------------------------
    #  통계 패널
    # ------------------------------------------------------------------
    def _init_stats_panel(self):
        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet(
            "background-color:#020617; border-radius:12px;"
        )
        stats_layout = QHBoxLayout(self.stats_frame)
        stats_layout.setContentsMargins(16, 10, 16, 10)
        stats_layout.setSpacing(16)

        self.stat_labels = {}

        def make_card(title_text):
            card = QFrame()
            card.setStyleSheet(
                """
                QFrame {
                    background-color:#020617;
                    border:1px solid #1E293B;
                    border-radius:10px;
                }
                """
            )
            v = QVBoxLayout(card)
            v.setContentsMargins(12, 6, 12, 6)

            title = QLabel(title_text)
            title.setStyleSheet("color:#9CA3AF; font-size:9pt;")
            value = QLabel("--")
            value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            value.setStyleSheet(
                "color:#38BDF8; font-size:16pt; font-weight:bold;"
            )

            v.addWidget(title)
            v.addStretch()
            v.addWidget(value)

            return card, value

        for name in ["평균값", "최소값", "최대값", "표준편차", "안정도"]:
            card, value_label = make_card(name)
            self.stat_labels[name] = value_label
            stats_layout.addWidget(card)

    def update_stats(self, y_values):
        # 기본값 초기화
        for lbl in self.stat_labels.values():
            lbl.setText("--")

        if not y_values:
            return

        cleaned = []
        for v in y_values:
            if v is None:
                continue
            try:
                fv = float(v)
            except Exception:
                continue
            if np.isnan(fv):
                continue
            cleaned.append(fv)

        if not cleaned:
            return

        arr = np.array(cleaned, dtype=float)
        mean_v = float(np.mean(arr))
        min_v = float(np.min(arr))
        max_v = float(np.max(arr))
        std_v = float(np.std(arr))

        # 안정도: (1 - std/|mean|) * 100 [%], 0~100 클램핑
        if mean_v == 0:
            stability = 0.0
        else:
            stability = (1.0 - std_v / abs(mean_v)) * 100.0
            stability = max(0.0, min(100.0, stability))

        self.stat_labels["평균값"].setText(f"{mean_v:,.2f}")
        self.stat_labels["최소값"].setText(f"{min_v:,.2f}")
        self.stat_labels["최대값"].setText(f"{max_v:,.2f}")
        self.stat_labels["표준편차"].setText(f"{std_v:,.2f}")
        self.stat_labels["안정도"].setText(f"{stability:,.1f}%")

    # ------------------------------------------------------------------
    #  시간 범위 / 기간 설정
    # ------------------------------------------------------------------
    def _make_time_range_handler(self, name):
        def handler():
            # 버튼 체크 상태 갱신
            for n, btn in self.time_buttons.items():
                btn.setChecked(n == name)

            if name == "기간설정":
                dlg = CustomRangeDialog(self)
                if dlg.exec():
                    self.custom_start, self.custom_end = dlg.get_range()
                    self.time_range = "기간설정"
                else:
                    # 취소 시 기존 버튼 상태로 복귀
                    self.time_buttons[self.time_range].setChecked(True)
                    return
            else:
                self.time_range = name

            # 기간만 변경 → 로컬 데이터 재사용해서 그래프만 다시 그림
            self.update_graph()

        return handler

    def _get_time_window(self):
        """현재 time_range 에 해당하는 (start, end) 반환."""
        if self.time_range == "기간설정" and self.custom_start and self.custom_end:
            return self.custom_start, self.custom_end

        now = datetime.now()
        if self.time_range == "6시간":
            return now - timedelta(hours=6), now
        elif self.time_range == "24시간":
            return now - timedelta(hours=24), now
        elif self.time_range == "7일":
            return now - timedelta(days=7), now
        elif self.time_range == "30일":
            return now - timedelta(days=30), now
        else:
            # 기본값: 24시간
            return now - timedelta(hours=24), now

    # ------------------------------------------------------------------
    #  MainWindow / FrameLeft 에서 호출되는 API
    # ------------------------------------------------------------------
    def toggle_parent(self, parent_name: str):
        if parent_name not in self.selected_children:
            self.selected_children[parent_name] = []

        if parent_name not in self.raw:
            self.reload_data(parent_name)

        self.update_graph()

        # ★ 좌측 UI 즉시 갱신 ★
        if hasattr(self, "frame_left") and self.frame_left:
            self.frame_left.refresh_child_selection()

    def show_child_graph(self, parent_name: str, child_name: str):
        if parent_name not in self.selected_children:
            self.selected_children[parent_name] = []

        if child_name in self.selected_children[parent_name]:
            self.selected_children[parent_name].remove(child_name)
        else:
            if len(self.selected_children[parent_name]) >= 4:
                self.selected_children[parent_name].pop(0)
            self.selected_children[parent_name].append(child_name)

        if parent_name not in self.raw:
            self.reload_data(parent_name)

        self.update_graph()

        # ★ 좌측 UI 즉시 갱신 ★
        if hasattr(self, "frame_left") and self.frame_left:
            self.frame_left.refresh_child_selection()

    # ------------------------------------------------------------------
    #  새로고침 버튼용: 선택된 parent 전체 재조회
    # ------------------------------------------------------------------
    def refresh_all_data(self):
        # 현재 선택된 parent들(raw에 있는 것 + selected_children 기준)을 모두 재로드
        parents = set(self.selected_children.keys())
        for parent_name in parents:
            self.reload_data(parent_name, load_only=True)
        self.update_graph()

    # ------------------------------------------------------------------
    #  DB 로부터 데이터 로드
    # ------------------------------------------------------------------
    def reload_data(self, parent_name, load_only=False):
        """parent_name 기준으로 raw[parent_name] = {times:[], data:{col:[...]}} 저장"""

        info = TABLE_MAP.get(parent_name)
        if not info:
            print(f"[FrameCenter] TABLE_MAP 에 없는 parent: {parent_name}")
            return

        table = info["table"]
        if not table:
            print(f"[FrameCenter] 테이블이 없는 parent: {parent_name}")
            return

        wanted_cols = list(dict.fromkeys(info["columns"].values()))

        conn = None  # ★ conn이 실패해도 finally에서 에러 안 나도록 초기화
        try:
            conn = get_connection(readonly=True)
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {table} ORDER BY datetime ASC")
            rows = cur.fetchall()

            col_names = [desc[0] for desc in cur.description]
            col_index = {name: idx for idx, name in enumerate(col_names)}

            if "datetime" not in col_index:
                print(f"[FrameCenter] {table} 에 datetime 컬럼이 없습니다.")
                return

        except Exception as e:
            print(f"[FrameCenter] DB 오류: {e}")
            return
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

        # raw[parent_name] 구조 생성
        times = []
        data = {col: [] for col in wanted_cols}
        dt_idx = col_index["datetime"]

        for row in rows:
            try:
                dt = row[dt_idx]
                if not isinstance(dt, datetime):
                    dt = datetime.fromisoformat(str(dt))
            except Exception:
                continue
            times.append(dt)

            for col in wanted_cols:
                idx = col_index.get(col)
                val = row[idx] if idx is not None else None
                data[col].append(val)

        # 저장
        self.raw[parent_name] = {
            "times": times,
            "data": data
        }

        if not load_only:
            self.update_graph()

    # ------------------------------------------------------------------
    #  그래프 업데이트
    # ------------------------------------------------------------------
    def update_graph(self):
        try:
            self.figure.clf()
            self.figure.set_facecolor("#0F172A")

            self.ax_info.clear()  # ★ subplot 정보 초기화
            self.update_stats([])  # 기본 통계 초기화

            start, end = self._get_time_window()
            all_plots = []

            # parent-child 조합 데이터 수집
            for parent, child_list in self.selected_children.items():
                if parent not in self.raw:
                    continue

                info = TABLE_MAP[parent]
                times = self.raw[parent]["times"]
                data = self.raw[parent]["data"]

                indices = [i for i, t in enumerate(times) if start <= t <= end]
                if not indices:
                    continue

                for child in child_list:
                    col = info["columns"].get(child)
                    if not col:
                        continue

                    xs = [times[i] for i in indices]
                    ys = [data[col][i] for i in indices]

                    # 유효값 필터
                    fx, fy = [], []
                    for x, y in zip(xs, ys):
                        try:
                            v = float(y)
                            if np.isnan(v):
                                continue
                            fx.append(x)
                            fy.append(v)
                        except Exception:
                            continue

                    if not fx:
                        continue

                    all_plots.append((f"{parent} | {child}", fx, fy))

            # 아무 그래프 없음 → 빈 화면
            if not all_plots:
                self.canvas.draw()
                return

            n = len(all_plots)

            if n == 1:
                rows, cols = 1, 1
            elif n == 2:
                rows, cols = 1, 2
            else:
                rows = (n + 1) // 2
                cols = 2

            for idx, (label, xs, ys) in enumerate(all_plots):
                ax = self.figure.add_subplot(rows, cols, idx + 1)

                ax.set_facecolor("#020617")
                for spine in ax.spines.values():
                    spine.set_color("#1E293B")

                ax.tick_params(axis="x", colors="white")
                ax.tick_params(axis="y", colors="white")
                ax.grid(True, color="#1E293B", linestyle="--", linewidth=0.5)

                ax.plot(xs, ys, linewidth=1.0)
                ax.set_title(label, color="white", fontsize=10, pad=8)

                # ★ 클릭 이벤트용 데이터 저장
                self.ax_info.append({
                    "ax": ax,
                    "label": label,
                    "ys": ys
                })

            self.figure.autofmt_xdate()
            self.figure.subplots_adjust(
                left=0.06, right=0.98, top=0.95, bottom=0.1,
                wspace=0.15, hspace=0.22
            )

            self.canvas.draw()

        except Exception as e:
            import traceback
            print("[FrameCenter] update_graph 예외:", e)
            traceback.print_exc()
            try:
                self.canvas.draw()
            except Exception:
                pass

    def on_graph_click(self, event):
        if event.inaxes is None:
            return  # 그래프 영역 밖 클릭

        clicked_ax = event.inaxes

        # 어떤 ax를 클릭했는지 검색
        for info in self.ax_info:
            if info["ax"] == clicked_ax:
                label = info["label"]
                ys = info["ys"]

                # 제목 갱신
                self.title_label.setText(f"선택된 그래프: {label}")

                # 통계 갱신
                self.update_stats(ys)

                # 그래프 하이라이트
                self._highlight_selected_ax(clicked_ax)
                break

    def save_pdf_report(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "PDF 보고서 저장",
            "VLBI_Report.pdf",
            "PDF Files (*.pdf)"
        )
        if not filename:
            return

        # 1) 그래프 이미지 저장
        graph_path = "temp_graph.png"
        self.canvas.figure.savefig(graph_path, dpi=150, facecolor=self.canvas.figure.get_facecolor())

        # 2) PDF 생성
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # 기본 스타일에 폰트 적용
        styles["Title"].fontName = "MalgunGothic-Bold"
        styles["Normal"].fontName = "MalgunGothic"

        # 오른쪽 정렬 스타일
        right_style = styles["Normal"].clone('Right')
        right_style.alignment = TA_RIGHT
        styles.add(right_style)

        # 가운데 정렬 스타일
        center_style = styles["Normal"].clone('Center')
        center_style.alignment = TA_CENTER
        styles.add(center_style)

        # 가운데 정렬 제목 스타일
        center_title_style = styles["Title"].clone('CenterTitle')
        center_title_style.alignment = TA_CENTER
        styles.add(center_title_style)

        # 보고서 제목 (중앙 정렬)
        elements.append(Paragraph("<b>VLBI 통계 보고서</b>", styles["CenterTitle"]))
        elements.append(Spacer(1, 0.5 * cm))

        # ★ 생성 날짜/시간 (오른쪽 정렬)
        now_kst = datetime.utcnow() + timedelta(hours=9)
        created_text = f"생성일시: {now_kst.strftime('%Y-%m-%d %H:%M:%S')} (KST)"
        elements.append(Paragraph(created_text, styles["Center"]))
        elements.append(Spacer(1, 0.5 * cm))

        # ★ 선택된 Parent/Child 목록 (중앙 정렬)
        elements.append(Paragraph("<b>선택된 항목</b>", styles["CenterTitle"]))
        elements.append(Spacer(1, 0.3 * cm))

        for parent, children in self.selected_children.items():
            if not children:
                continue

            elements.append(Paragraph(f"<b>{parent}</b>", styles["Center"]))
            for child in children:
                elements.append(Paragraph(f"- {child}", styles["Center"]))

            elements.append(Spacer(1, 0.2 * cm))

        elements.append(Spacer(1, 0.5 * cm))

        # 그래프 이미지 삽입
        elements.append(Image(graph_path, width=16 * cm, height=10 * cm))
        elements.append(Spacer(1, 0.5 * cm))

        # 통계 값 표
        data = [
            ["항목", "값"],
            ["평균값", self.stat_labels["평균값"].text()],
            ["최소값", self.stat_labels["최소값"].text()],
            ["최대값", self.stat_labels["최대값"].text()],
            ["표준편차", self.stat_labels["표준편차"].text()],
            ["안정도", self.stat_labels["안정도"].text()],
        ]

        table = Table(data, colWidths=[5 * cm, 5 * cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'MalgunGothic'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),

            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F3F4F6")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(table)

        # PDF 저장
        doc.build(elements)

        # 임시 그래프 삭제
        try:
            os.remove(graph_path)
        except:
            pass

        print("PDF 보고서 저장 완료:", filename)

    def _highlight_selected_ax(self, selected_ax):
        # 모든 축 초기화
        for info in self.ax_info:
            for spine in info["ax"].spines.values():
                spine.set_edgecolor("#1E293B")
                spine.set_linewidth(1.0)

        # 선택된 축 강조 표시
        for spine in selected_ax.spines.values():
            spine.set_edgecolor("#38BDF8")
            spine.set_linewidth(2.0)

        self.canvas.draw()
