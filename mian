# -*- coding: utf-8 -*-
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QTabWidget
)

from config import TEXT, DEFAULT_PURPLE
from utils import ui_font, sp, try_enable_native_blur
from database.db_manager import TrackerDB

# 导入原有与新增的部件
from widgets.timer_widget import TimerWidget
from widgets.stats_widget import StatsWidget
from widgets.range_stats_card import RangeStatsCard
from widgets.calendar_widget import CalendarWidget  # <-- 1. 新增导入

from components.dialogs import SettingsDialog, TaskDialog, PlanDialog
from components.styles import glass_tab_style


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Focus & Time Tracker")
        self.resize(sp(1000, self), sp(680, self))

        # 初始化数据库
        self.db = TrackerDB()

        # 开启 Windows 毛玻璃效果
        try_enable_native_blur(int(self.winId()))

        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # 选项卡容器 (TabWidget)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(glass_tab_style())

        # --------------------------------------------------------------
        # Tab 1: 计时与实时统计 (Focus & Stats)
        # --------------------------------------------------------------
        tab_focus = QWidget()
        focus_layout = QHBoxLayout(tab_focus)
        focus_layout.setContentsMargins(0, 12, 0, 0)
        focus_layout.setSpacing(12)

        self.timer_widget = TimerWidget(self)
        self.timer_widget.session_completed.connect(self._on_session_completed)

        self.stats_widget = StatsWidget(self)

        focus_layout.addWidget(self.timer_widget, 3)
        focus_layout.addWidget(self.stats_widget, 2)

        # --------------------------------------------------------------
        # Tab 2: 日历与循环计划 (Calendar & Schedule) -- 2. 新增页面
        # --------------------------------------------------------------
        self.calendar_widget = CalendarWidget(self.db, self)  # <-- 实例化并传入 db

        # --------------------------------------------------------------
        # Tab 3: 数据汇总 (Overview)
        # --------------------------------------------------------------
        tab_overview = QWidget()
        overview_layout = QVBoxLayout(tab_overview)
        overview_layout.setContentsMargins(0, 12, 0, 0)

        self.range_stats = RangeStatsCard("Weekly Summary", self)
        overview_layout.addWidget(self.range_stats)

        # 3. 将各页面添加到 TabWidget 中
        self.tabs.addTab(tab_focus, "Focus Timer")
        self.tabs.addTab(self.calendar_widget, "Calendar Schedule")  # <-- 新增 Tab
        self.tabs.addTab(tab_overview, "Overview")

        main_layout.addWidget(self.tabs)

    def _on_session_completed(self, category, task_name, start_time, end_time):
        """计时结束回调处理"""
        # 保存到专注会话表中 (已有逻辑)
        duration = int((end_time - start_time).total_seconds())
        # ... 刷新统计等操作 ...


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
