from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox
)


class ThresholdDialog(QDialog):
    def __init__(self, parent=None, menu_lists=None, current_thresholds=None):
        super().__init__(parent)
        self.setWindowTitle("장비별 임계값 설정")
        self.setMinimumWidth(350)

        self.menu_lists = menu_lists
        self.current_thresholds = current_thresholds or {}

        layout = QVBoxLayout(self)

        # ----------------------------
        # Parent 선택
        # ----------------------------
        layout.addWidget(QLabel("장비 선택"))
        self.parent_combo = QComboBox()
        self.parent_combo.addItems(menu_lists.keys())
        layout.addWidget(self.parent_combo)

        # ----------------------------
        # Child 선택
        # ----------------------------
        layout.addWidget(QLabel("항목 선택"))
        self.child_combo = QComboBox()
        layout.addWidget(self.child_combo)

        # ----------------------------
        # 임계값 입력
        # ----------------------------
        layout.addWidget(QLabel("임계값 주의 (노란색):"))
        self.caution_edit = QLineEdit()
        layout.addWidget(self.caution_edit)

        layout.addWidget(QLabel("임계값 경고 (빨간색):"))
        self.warning_edit = QLineEdit()
        layout.addWidget(self.warning_edit)

        # ----------------------------
        # 버튼
        # ----------------------------
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("저장")
        btn_cancel = QPushButton("취소")
        btn_ok.clicked.connect(self.save_thresholds)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        # ----------------------------
        # Signal 연결
        # ----------------------------
        self.parent_combo.currentTextChanged.connect(self.update_child_combo)
        self.child_combo.currentTextChanged.connect(self.load_existing_threshold)

        # ----------------------------
        # 초기 child 세팅 + 기존값 로드
        # ----------------------------
        self.update_child_combo(self.parent_combo.currentText())
        self.load_existing_threshold()

        self.result = None

    # -----------------------------------------------------
    # 부모 선택 변경 시
    # -----------------------------------------------------
    def update_child_combo(self, parent_name):
        """부모 선택 시 자식 목록 변경 + 기존값 로드"""
        self.child_combo.clear()

        # ★ 부모 임계값용 "선택 안 함" 옵션 추가
        self.child_combo.addItem("(선택 안 함)")

        # 실제 자식 장비 리스트 추가
        self.child_combo.addItems(self.menu_lists[parent_name])

        # 새 목록 기준으로 기존 값 로드
        self.load_existing_threshold()

    # -----------------------------------------------------
    # 기존 임계값 로드
    # -----------------------------------------------------
    def load_existing_threshold(self):
        """현재 parent + child 기준으로 기존 임계값 자동 로드"""
        parent = self.parent_combo.currentText()
        child = self.child_combo.currentText()

        if not parent or not child:
            return

        # ★ 부모 임계값(__parent__) 처리
        if child == "(선택 안 함)":
            key = "__parent__"
        else:
            key = child

        existing = self.current_thresholds.get(parent, {}).get(key, {})

        caution = existing.get("caution")
        warning = existing.get("warning")

        self.caution_edit.setText("" if caution is None else str(caution))
        self.warning_edit.setText("" if warning is None else str(warning))

    # -----------------------------------------------------
    # 저장 버튼 클릭
    # -----------------------------------------------------
    def save_thresholds(self):
        parent = self.parent_combo.currentText()
        child = self.child_combo.currentText()

        # ★ 부모 임계값이면 __parent__로 저장
        if child == "(선택 안 함)":
            child = "__parent__"

        try:
            caution = float(self.caution_edit.text()) if self.caution_edit.text() else None
            warning = float(self.warning_edit.text()) if self.warning_edit.text() else None
        except ValueError:
            print("숫자를 입력해야 합니다.")
            return

        self.result = (parent, child, caution, warning)
        self.accept()
