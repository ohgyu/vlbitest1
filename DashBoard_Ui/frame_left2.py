# DashBoard_Ui/frame_left.py
from PyQt6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
from functools import partial


class FrameLeft(QScrollArea):
    item_selected = pyqtSignal(str, str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.setMinimumWidth(220)
        self.setMaximumWidth(330)

        # 스크롤 설정
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.setStyleSheet("background-color: rgb(15,23,42); border-radius:15px;")

        # 콘텐츠 프레임
        content = QWidget()
        content.setStyleSheet("background-color: rgb(15,23,42);")
        self.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        self.active_child = None

        # 제목
        title_label = QLabel("매개변수 선택")
        title_label.setStyleSheet(
            "color: rgb(110,227,247); font-weight:bold; font-size:20pt;"
        )
        layout.addWidget(title_label)

        # 메뉴 항목
        self.menu_lists = {
            "2GHz 수신기 상태 모니터": [
                "Normal Temperature RF", "Normal Temperature Load",
                "LNA Monitor LHCP Vd", "LNA Monitor LHCP Id",
                "LNA Monitor RHCP Vd", "LNA Monitor RHCP Id",
                "Cryogenic Temperature Cold", "Cryogenic Temperature Shild Box",
                "Pressure Sensor CH1",
                "RF out Power RHCP", "RF out Power LHCP"
            ],
            "8GHz 수신기 상태 모니터": [
                "Normal Temperature RF", "Normal Temperature Load",
                "LNA Monitor LHCP Vg1", "LNA Monitor LHCP Vg2",
                "LNA Monitor LHCP Vd", "LNA Monitor LHCP Id",
                "LNA Monitor RHCP Vg1", "LNA Monitor RHCP Vg2",
                "LNA Monitor RHCP Vd", "LNA Monitor RHCP Id",
                "Cryogenic Temperature Cold", "Cryogenic Temperature Shild Box",
                "Pressure Sensor CH1",
                "RF out Power RHCP", "RF out Power LHCP"
            ],
            "22GHz 수신기 상태 모니터": [
                "Normal Temperature RF", "Normal Temperature LO",
                "LNA Monitor LHCP Vg1", "LNA Monitor LHCP Vg2",
                "LNA Monitor LHCP Vd", "LNA Monitor LHCP Id",
                "LNA Monitor RHCP Vg1", "LNA Monitor RHCP Vg2",
                "LNA Monitor RHCP Vd", "LNA Monitor RHCP Id",
                "Cryogenic Temperature Cold", "Cryogenic Temperature Shild Box",
                "Pressure Sensor CH1",
                "RF out Power RF", "RF out Power LO"
            ],
            "43GHz 수신기 상태 모니터": [
                "Normal Temperature RF", "Normal Temperature LO",
                "LNA Monitor LHCP Vg1", "LNA Monitor LHCP Vg2",
                "LNA Monitor LHCP Vd", "LNA Monitor LHCP Id",
                "LNA Monitor RHCP Vg1", "LNA Monitor RHCP Vg2",
                "LNA Monitor RHCP Vd", "LNA Monitor RHCP Id",
                "Cryogenic Temperature Cold", "Cryogenic Temperature Shild Box",
                "Pressure Sensor CH1",
                "RF out Power RHCP", "RF out Power LHCP", "RF out Power LO"
            ],
            "S/X 다운 컨버터": ["S", "X1", "X2"],
            "K 다운 컨버터": ["K1", "K2", "K3", "K4"],
            "Q 다운 컨버터": ["Q1", "Q2", "Q3", "Q4"],
            "Video Converter 1": ["CH1", "CH2", "CH3", "CH4", "CH5", "CH6", "CH7", "CH8"],
            "Video Converter 2": ["CH9", "CH10", "CH11", "CH12", "CH13", "CH14", "CH15", "CH16"],
            "IF Selector": [
                "CH1", "CH2", "CH3", "CH4", "CH5", "CH6", "CH7", "CH8",
                "CH9", "CH10", "CH11", "CH12", "CH13", "CH14", "CH15", "CH16"
            ],
        }

        self.lists = {}
        self.buttons = {}

        for title, items in self.menu_lists.items():
            btn = QPushButton(title)
            btn.setStyleSheet(self.default_btn_style())
            self.buttons[title] = btn
            layout.addWidget(btn)

            lst = QListWidget()
            lst.addItems(items)
            lst.setVisible(False)
            lst.setStyleSheet(self.list_style())
            layout.addWidget(lst)
            self.lists[title] = lst

            btn.clicked.connect(partial(self.toggle_parent_item, title))
            lst.itemClicked.connect(partial(self.select_child_item, group_name=title))

        layout.addStretch()

    def default_btn_style(self):
        return """
        QPushButton {
            text-align:left;
            background-color:#1E293B;
            color:white;
            padding:8px;
            border-radius:5px;
            font-size:16pt;
        }
        QPushButton:hover { background-color:#334155; }
        """

    def active_btn_style(self):
        return """
        QPushButton {
            text-align:left;
            background-color:#2563EB;
            color:white;
            padding:8px;
            border-radius:5px;
            font-size:16pt;
            font-weight:bold;
        }
        """

    def list_style(self):
        return """
        QListWidget {
            background-color:#1E293B;
            color:white;
            border:1px solid rgb(80,160,200);
            border-radius:5px;
            font-size:12pt;
        }
        QListWidget::item:selected {
            background-color:#2563EB;
            color:white;
            font-weight:bold;
        }
        QListWidget::item:hover {
            background-color:#334155;
        }
        """

    def toggle_parent_item(self, group_name):
        lst = self.lists[group_name]
        lst.setVisible(not lst.isVisible())

        active_parents = [name for name, l in self.lists.items() if l.isVisible()]
        self.update_button_highlight(active_parents)

        self.item_selected.emit(group_name, "", True)

    def update_button_highlight(self, active_names):
        for name, btn in self.buttons.items():
            if name in active_names:
                btn.setStyleSheet(self.active_btn_style())
            else:
                btn.setStyleSheet(self.default_btn_style())

    def select_child_item(self, item, group_name):
        self.active_child = item
        self.item_selected.emit(group_name, item.text(), False)

    def refresh_child_selection(self, parent_name=None):
        if not hasattr(self, "frame_center") or self.frame_center is None:
            return
        for parent, widget in self.lists.items():
            selected_list = self.frame_center.selected_children.get(parent, [])
            for i in range(widget.count()):
                widget.item(i).setSelected(widget.item(i).text() in selected_list)

    def set_frame_center(self, frame_center):
        self.frame_center = frame_center
