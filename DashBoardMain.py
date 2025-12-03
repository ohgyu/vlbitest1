# main.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt

from DashBoard_Ui.frame_top import FrameTop
from DashBoard_Ui.frame_left import FrameLeft
from DashBoard_Ui.frame_center import FrameCenter


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VLBI Dashboard")

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Top
        self.frame_top = FrameTop(parent=self)
        main_layout.addWidget(self.frame_top, stretch=1)

        # Left & Center
        self.frame_left = FrameLeft()
        self.frame_center = FrameCenter()

        self.frame_left.set_frame_center(self.frame_center)
        self.frame_center.frame_left = self.frame_left

        # ★ PyQt6 전용 QSplitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.frame_left)
        splitter.addWidget(self.frame_center)

        # 초기 폭 비율
        splitter.setSizes([260, 1200])

        main_layout.addWidget(splitter, stretch=9)

        self.frame_top.frame_center = self.frame_center
        self.frame_left.item_selected.connect(self.on_item_selected)

    def on_item_selected(self, group_name, item_name, is_parent):
        if is_parent:
            self.frame_center.toggle_parent(group_name)
        else:
            self.frame_center.show_child_graph(group_name, item_name)

        self.frame_left.refresh_child_selection()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
