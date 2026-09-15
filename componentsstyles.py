# -*- coding: utf-8 -*-
from PySide6.QtGui import QColor
from config import DEFAULT_GLASS_OPACITY_SCALE, TEXT, SUBTEXT
from utils import sp


# ----------------------------------------------------------------------
# 1. 色彩与透明度转换 Helper 函数
# ----------------------------------------------------------------------

def scaled_alpha(alpha: int, scale: float = DEFAULT_GLASS_OPACITY_SCALE) -> int:
    """根据全局玻璃透明度缩放系数调整 Alpha 值 (0-255)"""
    return max(0, min(255, int(alpha * scale)))


def css_rgba(color: QColor, alpha_override: int = None) -> str:
    """将 QColor 对象转换为 CSS rgba(...) 格式字符串"""
    a = color.alpha() if alpha_override is None else alpha_override
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {a / 255.0:.3f})"


# ----------------------------------------------------------------------
# 2. QSS 样式生成器
# ----------------------------------------------------------------------

def glass_button_style(
    base_color: QColor = QColor(255, 255, 255),
    text_color: QColor = TEXT,
    border_alpha: int = 40,
    bg_alpha: int = 120,
    radius_px: float = 12.0,
    widget=None,
) -> str:
    """生成具备毛玻璃极简质感的主按钮 QSS 样式"""
    r = sp(radius_px, widget)
    bg_normal = css_rgba(base_color, scaled_alpha(bg_alpha))
    bg_hover = css_rgba(base_color, scaled_alpha(min(255, bg_alpha + 40)))
    bg_pressed = css_rgba(base_color, scaled_alpha(max(0, bg_alpha - 30)))
    border_color = css_rgba(QColor(255, 255, 255), scaled_alpha(border_alpha))
    text_rgba = css_rgba(text_color)

    return f"""
        QPushButton {{
            background-color: {bg_normal};
            color: {text_rgba};
            border: 1px solid {border_color};
            border-radius: {r}px;
            padding: 6px 14px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {bg_hover};
            border: 1px solid rgba(255, 255, 255, 0.6);
        }}
        QPushButton:pressed {{
            background-color: {bg_pressed};
        }}
        QPushButton:disabled {{
            background-color: rgba(200, 200, 200, 0.2);
            color: rgba(150, 150, 150, 0.5);
            border: 1px solid rgba(200, 200, 200, 0.1);
        }}
    """


def glass_tiny_button_style(widget=None) -> str:
    """生成适用于小图标/轻量操作的微型按钮样式"""
    r = sp(8, widget)
    return f"""
        QPushButton {{
            background-color: rgba(255, 255, 255, 0.35);
            color: {css_rgba(TEXT)};
            border: 1px solid rgba(255, 255, 255, 0.4);
            border-radius: {r}px;
            padding: 2px 8px;
            font-size: 11px;
        }}
        QPushButton:hover {{
            background-color: rgba(255, 255, 255, 0.65);
        }}
        QPushButton:pressed {{
            background-color: rgba(255, 255, 255, 0.2);
        }}
    """


def glass_input_style(widget=None) -> str:
    """生成输入框 (QLineEdit, QComboBox, QSpinBox) 的通用 QSS 样式"""
    r = sp(8, widget)
    return f"""
        QLineEdit, QComboBox, QSpinBox {{
            background-color: rgba(255, 255, 255, 0.45);
            color: {css_rgba(TEXT)};
            border: 1px solid rgba(255, 255, 255, 0.5);
            border-radius: {r}px;
            padding: 4px 8px;
            selection-background-color: rgba(107, 113, 217, 0.4);
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
            background-color: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(107, 113, 217, 0.6);
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
    """


def glass_scrollbar_style() -> str:
    """生成极简半透明滚动条样式"""
    return """
        QScrollBar:vertical {
            border: none;
            background: transparent;
            width: 6px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: rgba(0, 0, 0, 0.15);
            min-height: 20px;
            border-radius: 3px;
        }
        QScrollBar::handle:vertical:hover {
            background: rgba(0, 0, 0, 0.3);
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
    """