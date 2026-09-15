# -*- coding: utf-8 -*-
from typing import Dict
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar

from config import TEXT, SUBTEXT, DEFAULT_PURPLE
from utils import sp, ui_font, fmt_hms
from components.glass_card import LightGlassCard


class RangeStatsCard(LightGlassCard):
    """范围（日/周/月）统计进度汇总卡片"""

    def __init__(self, title: str = "Weekly Overview", parent=None):
        super().__init__(parent, radius_px=16, bg_alpha=150, border_alpha=60)
        self.title_text = title
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # 卡片标题
        self.lbl_title = QLabel(self.title_text)
        self.lbl_title.setFont(ui_font(12, QFont.Weight.Bold, widget=self))
        self.lbl_title.setStyleSheet(f"color: {TEXT.name()}; background: transparent;")
        layout.addWidget(self.lbl_title)

        # 数据分类列表容器
        self.list_widget = QWidget(self)
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(6)
        layout.addWidget(self.list_widget)

    def update_data(self, category_durations: Dict[str, int], targets: Dict[str, int] = None):
        """更新汇总列表项"""
        # 清除旧的 Layout 项
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not category_durations:
            lbl_empty = QLabel("No records available")
            lbl_empty.setFont(ui_font(11, widget=self))
            lbl_empty.setStyleSheet(f"color: {SUBTEXT.name()}; background: transparent;")
            self.list_layout.addWidget(lbl_empty)
            return

        targets = targets or {}
        max_duration = max(category_durations.values()) if category_durations else 1

        for cat, sec in category_durations.items():
            item_row = QWidget()
            row_layout = QVBoxLayout(item_row)
            row_layout.setContentsMargins(0, 2, 0, 2)
            row_layout.setSpacing(2)

            # 文本描述 (分类 + 时间)
            top_layout = QHBoxLayout()
            lbl_cat = QLabel(cat)
            lbl_cat.setFont(ui_font(11, widget=self))
            lbl_cat.setStyleSheet(f"color: {TEXT.name()}; background: transparent;")

            target_sec = targets.get(cat, 0)
            time_str = fmt_hms(sec)
            if target_sec > 0:
                time_str += f" / {fmt_hms(target_sec)}"

            lbl_val = QLabel(time_str)
            lbl_val.setFont(ui_font(11, widget=self))
            lbl_val.setStyleSheet(f"color: {SUBTEXT.name()}; background: transparent;")

            top_layout.addWidget(lbl_cat)
            top_layout.addStretch()
            top_layout.addWidget(lbl_val)
            row_layout.addLayout(top_layout)

            # 进度条展示
            progress = QProgressBar()
            progress.setFixedHeight(sp(4, self))
            progress.setTextVisible(False)
            
            p_val = int((sec / (target_sec if target_sec > 0 else max_duration)) * 100)
            progress.setValue(min(100, p_val))
            progress.setStyleSheet("""
                QProgressBar {
                    background-color: rgba(200, 205, 215, 0.3);
                    border: none;
                    border-radius: 2px;
                }
                QProgressBar::chunk {
                    background-color: rgba(107, 113, 217, 0.8);
                    border-radius: 2px;
                }
            """)
            row_layout.addWidget(progress)

            self.list_layout.addWidget(item_row)
