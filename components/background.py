# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QLinearGradient, QRadialGradient, QBrush, QColor
from PySide6.QtWidgets import QWidget

from config import DEFAULT_MINT, DEFAULT_PURPLE
from utils import get_noise_pixmap, blend


class LightWallpaperBackground(QWidget):
    """自绘柔和渐变与动态磨砂颗粒的背景部件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        
        # 预先生成 Noise 贴图以提高绘制性能
        self._noise_pixmap = get_noise_pixmap(128, 128, opacity=0.035)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        w, h = rect.width(), rect.height()

        # 1. 绘制底层线性光晕渐变
        linear_grad = QLinearGradient(0, 0, w, h)
        linear_grad.setColorAt(0.0, QColor(245, 247, 250))
        linear_grad.setColorAt(0.5, QColor(238, 242, 248))
        linear_grad.setColorAt(1.0, QColor(230, 235, 245))
        painter.fillRect(rect, linear_grad)

        # 2. 绘制左上角 Mint 柔光斑
        mint_grad = QRadialGradient(w * 0.15, h * 0.15, max(w, h) * 0.55)
        mint_color = blend(DEFAULT_MINT, QColor(255, 255, 255), 0.4)
        mint_color.setAlpha(100)
        mint_grad.setColorAt(0.0, mint_color)
        mint_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(rect, QBrush(mint_grad))

        # 3. 绘制右下角 Purple 柔光斑
        purple_grad = QRadialGradient(w * 0.85, h * 0.85, max(w, h) * 0.6)
        purple_color = blend(DEFAULT_PURPLE, QColor(255, 255, 255), 0.45)
        purple_color.setAlpha(85)
        purple_grad.setColorAt(0.0, purple_color)
        purple_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(rect, QBrush(purple_grad))

        # 4. 平铺噪声纹理覆盖，增强质感
        if not self._noise_pixmap.isNull():
            painter.drawTiledPixmap(rect, self._noise_pixmap)

        painter.end()
