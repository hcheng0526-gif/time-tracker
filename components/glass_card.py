# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient
from PySide6.QtWidgets import QWidget, QGraphicsDropShadowEffect

from config import DEFAULT_GLASS_OPACITY_SCALE
from utils import sp
from components.styles import scaled_alpha


class LightGlassCard(QWidget):
    """毛玻璃半透明卡片容器基类"""

    def __init__(
        self,
        parent=None,
        radius_px: float = 16.0,
        bg_alpha: int = 150,
        border_alpha: int = 60,
        enable_shadow: bool = True
    ):
        super().__init__(parent)
        self.radius_px = radius_px
        self.bg_alpha = bg_alpha
        self.border_alpha = border_alpha

        # 开启透明绘图属性
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 添加柔和卡片阴影
        if enable_shadow:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(sp(20, self))
            shadow.setColor(QColor(30, 40, 70, 20))
            shadow.setOffset(0, sp(4, self))
            self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        r = sp(self.radius_px, self)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)

        # 1. 填充半透明白色背景
        bg_color = QColor(255, 255, 255, scaled_alpha(self.bg_alpha))
        painter.setBrush(bg_color)

        # 2. 绘制顶部到底部的渐变高光边框 (Glass Highlight)
        border_grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        border_grad.setColorAt(0.0, QColor(255, 255, 255, scaled_alpha(min(255, self.border_alpha + 80))))
        border_grad.setColorAt(1.0, QColor(255, 255, 255, scaled_alpha(max(10, self.border_alpha - 30))))
        
        pen = QPen(border_grad, 1.0)
        painter.setPen(pen)

        # 绘制圆角卡片
        painter.drawRoundedRect(rect, r, r)
        painter.end()
