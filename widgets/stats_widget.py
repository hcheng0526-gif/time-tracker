# -*- coding: utf-8 -*-
import math
from typing import Dict
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from config import TEXT, SUBTEXT, DEFAULT_MINT, DEFAULT_PURPLE
from utils import sp, ui_font, fmt_hms
from components.glass_card import LightGlassCard


class DonutChartCanvas(QWidget):
    """自绘环形统计图画布"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data: Dict[str, int] = {}  # {category: duration_seconds}
        self.colors = [
            DEFAULT_MINT, DEFAULT_PURPLE, QColor(255, 179, 186), 
            QColor(255, 223, 186), QColor(186, 225, 255), QColor(186, 255, 201)
        ]

    def set_data(self, data: Dict[str, int]):
        self.data = {k: v for k, v in data.items() if v > 0}
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        total = sum(self.data.values())
        rect = QRectF(self.rect()).adjusted(12, 12, -12, -12)

        if total <= 0 or not self.data:
            # 绘制无数据空心圆圈
            pen = QPen(QColor(200, 205, 215, 100), sp(12, self))
            painter.setPen(pen)
            painter.drawEllipse(rect)
            painter.end()
            return

        # 绘制各分类环形占比弧线
        stroke_width = sp(16, self)
        start_angle = 90 * 16

        for idx, (cat, val) in enumerate(self.data.items()):
            sweep_angle = -int((val / total) * 360 * 16)
            color = self.colors[idx % len(self.colors)]

            pen = QPen(color, stroke_width)
            pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            painter.setPen(pen)
            painter.drawArc(rect, start_angle, sweep_angle)

            start_angle += sweep_angle

        painter.end()


class StatsWidget(LightGlassCard):
    """统计分析卡片部件"""

    def __init__(self, parent=None):
        super().__init__(parent, radius_px=18, bg_alpha=160, border_alpha=70)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        lbl_title = QLabel("Today's Distribution")
        lbl_title.setFont(ui_font(13, QFont.Weight.Bold, widget=self))
        lbl_title.setStyleSheet(f"color: {TEXT.name()}; background: transparent;")
        layout.addWidget(lbl_title)

        # 环形图画布
        self.chart = DonutChartCanvas(self)
        layout.addWidget(self.chart, 1)

        # 底部总时间说明
        self.lbl_total = QLabel("Total Focused: 00:00:00")
        self.lbl_total.setFont(ui_font(11, widget=self))
        self.lbl_total.setStyleSheet(f"color: {SUBTEXT.name()}; background: transparent;")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_total)

    def update_stats(self, category_durations: Dict[str, int]):
        """更新统计图表数据"""
        self.chart.set_data(category_durations)
        total_sec = sum(category_durations.values())
        self.lbl_total.setText(f"Total Focused: {fmt_hms(total_sec)}")
