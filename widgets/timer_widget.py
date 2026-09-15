# -*- coding: utf-8 -*-
import math
from datetime import datetime
from PySide6.QtCore import Qt, QTimer, QRectF, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit

from config import DEFAULT_CATEGORIES, TEXT, SUBTEXT, DEFAULT_MINT, DEFAULT_PURPLE
from utils import sp, ui_font, fmt_hms, blend, now_local
from components.glass_card import LightGlassCard
from components.styles import glass_button_style, glass_input_style


class ArcProgressWidget(QWidget):
    """自绘圆弧进度/环形指示器"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0.0  # 0.0 ~ 1.0

    def set_progress(self, val: float):
        self.progress = max(0.0, min(1.0, val))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        size = min(w, h) - sp(16, self)
        rect = QRectF((w - size) / 2, (h - size) / 2, size, size)
        stroke_width = sp(8, self)

        # 1. 轨道背景圆环
        pen_bg = QPen(QColor(220, 225, 235, 120), stroke_width)
        pen_bg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_bg)
        painter.drawEllipse(rect)

        # 2. 动态进度弧线 (从 -90 度/顶部开始)
        if self.progress > 0:
            pen_fg = QPen(DEFAULT_MINT, stroke_width)
            pen_fg.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen_fg)
            start_angle = 90 * 16
            span_angle = -int(self.progress * 360 * 16)
            painter.drawArc(rect, start_angle, span_angle)

        painter.end()


class TimerWidget(LightGlassCard):
    """计时器核心卡片部件"""

    session_completed = Signal(str, str, datetime, datetime)  # category, task_name, start_time, end_time

    def __init__(self, parent=None, categories=None):
        super().__init__(parent, radius_px=18, bg_alpha=160, border_alpha=70)
        self.categories = categories or DEFAULT_CATEGORIES
        
        self.is_running = False
        self.elapsed_seconds = 0
        self.start_dt = None

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._on_tick)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # 顶部输入栏 (分类与任务描述)
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self.cmb_category = QComboBox()
        self.cmb_category.addItems(self.categories)
        self.cmb_category.setStyleSheet(glass_input_style(self))

        self.txt_task = QLineEdit()
        self.txt_task.setPlaceholderText("What are you focusing on?")
        self.txt_task.setStyleSheet(glass_input_style(self))

        input_layout.addWidget(self.cmb_category, 1)
        input_layout.addWidget(self.txt_task, 2)
        layout.addLayout(input_layout)

        # 中间计时器自绘与时间显示
        self.arc_widget = ArcProgressWidget(self)
        arc_layout = QVBoxLayout(self.arc_widget)
        arc_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_time = QLabel("00:00:00")
        self.lbl_time.setFont(ui_font(28, QFont.Weight.Bold, widget=self))
        self.lbl_time.setStyleSheet(f"color: {TEXT.name()}; background: transparent;")
        arc_layout.addWidget(self.lbl_time)

        layout.addWidget(self.arc_widget, 1)

        # 底部操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_toggle = QPushButton("Start Focus")
        self.btn_toggle.setFont(ui_font(13, QFont.Weight.Bold, widget=self))
        self.btn_toggle.setStyleSheet(glass_button_style(DEFAULT_MINT, TEXT, widget=self))
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_timer)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setFont(ui_font(13, widget=self))
        self.btn_reset.setStyleSheet(glass_button_style(QColor(255, 255, 255, 100), TEXT, widget=self))
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_timer)

        btn_layout.addWidget(self.btn_toggle, 2)
        btn_layout.addWidget(self.btn_reset, 1)
        layout.addLayout(btn_layout)

    def _on_tick(self):
        self.elapsed_seconds += 1
        self.lbl_time.setText(fmt_hms(self.elapsed_seconds))
        # 简单循环进度展示
        self.arc_widget.set_progress((self.elapsed_seconds % 3600) / 3600.0)

    def toggle_timer(self):
        if not self.is_running:
            # 开始计时
            self.is_running = True
            self.start_dt = now_local()
            self.timer.start()
            self.btn_toggle.setText("Pause & Save")
            self.btn_toggle.setStyleSheet(glass_button_style(DEFAULT_PURPLE, QColor(255, 255, 255), widget=self))
        else:
            # 停止并保存
            self.is_running = False
            self.timer.stop()
            end_dt = now_local()
            
            category = self.cmb_category.currentText()
            task_name = self.txt_task.text().strip() or "(No details)"
            
            if self.elapsed_seconds > 0:
                self.session_completed.emit(category, task_name, self.start_dt, end_dt)

            self.reset_timer()

    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.elapsed_seconds = 0
        self.start_dt = None
        self.lbl_time.setText("00:00:00")
        self.arc_widget.set_progress(0.0)
        self.btn_toggle.setText("Start Focus")
        self.btn_toggle.setStyleSheet(glass_button_style(DEFAULT_MINT, TEXT, widget=self))
