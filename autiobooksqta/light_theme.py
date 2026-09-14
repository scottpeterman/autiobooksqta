LIGHT_THEME = """
QMainWindow, QWidget {
    background-color: #f5f5f0;
    color: #333333;
}

QFrame {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
}

QLabel {
    color: #3a3a3a;
}

QPushButton {
    background-color: #6b8e23;  /* Olive green */
    color: white;
    padding: 8px 15px;
    border-radius: 4px;
    border: none;
}

QPushButton:hover {
    background-color: #7aa329;
}

QPushButton:pressed {
    background-color: #5a7d1e;
}

QPushButton:disabled {
    background-color: #c0c0b8;
    color: #8a8a8a;
}

QComboBox {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 5px;
    color: #3a3a3a;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #3a3a3a;
    selection-background-color: #d8c8a0;
}

QLineEdit {
    background-color: #ffffff;
    color: #3a3a3a;
    padding: 5px;
    border-radius: 4px;
    border: 1px solid #d0d0d0;
}

QCheckBox {
    color: #3a3a3a;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
}

QCheckBox::indicator:unchecked {
    background-color: #ffffff;
    border: 1px solid #c0c0b8;
    border-radius: 2px;
}

QCheckBox::indicator:checked {
    background-color: #6b8e23;
    border: 1px solid #6b8e23;
    border-radius: 2px;
}

QProgressBar {
    border: none;
    background-color: #f0f0e8;
    border-radius: 4px;
    text-align: center;
    color: #3a3a3a;
}

QProgressBar::chunk {
    background-color: #6b8e23;
    border-radius: 4px;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: #f0f0e8;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #c0c0b8;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #6b8e23;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QStatusBar {
    background-color: #e8e0d0;
    color: #5a5a5a;
}

QSlider::groove:horizontal {
    border: 1px solid #d0d0d0;
    height: 4px;
    background: #f0f0e8;
    margin: 0 12px;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #6b8e23;
    border: none;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #7aa329;
}

QSplitter::handle {
    background-color: #e0e0d6;
}

QSplitter::handle:horizontal {
    width: 2px;
}

.HeaderLabel {
    font-weight: bold;
    font-size: 16px;
    margin-bottom: 5px;
    padding-bottom: 5px;
    border-bottom: 1px solid #e0e0d6;
}

.SectionPanel {
    background-color: #f9f9f4;
    border: 1px solid #e0e0d6;
    border-radius: 4px;
    padding: 10px;
    margin: 5px;
}
"""
