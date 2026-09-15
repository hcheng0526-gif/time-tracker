# -*- coding: utf-8 -*-
from datetime import date
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget, 
    QLabel, QPushButton, QListWidget, QListWidgetItem
)

from config import TEXT, SUBTEXT, DEFAULT_PURPLE
from utils import ui_font, sp
from components.glass_card import LightGlassCard
from components.styles import glass_button_style, glass_scrollbar_style
from components.dialogs import CalendarTaskDialog


class CalendarWidget(LightGlassCard):
    """日历与预定/循环任务展示视图"""

    task_added = Signal()

    def __init__(self, db_manager, parent=None):
        super().__init__(parent, radius_px=18, bg_alpha=160, border_alpha=70)
        self.db = db_manager
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 1. 左侧原生日历控件
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.refresh_task_list)
        self.calendar.setStyleSheet("""
            QCalendarWidget QAbstractItemView {
                background-color: rgba(255, 255, 255, 0.4);
                selection-background-color: rgba(107, 113, 217, 0.6);
                selection-color: white;
            }
        """)
        layout.addWidget(self.calendar, 3)

        # 2. 右侧所选日期的任务列表
        right_box = QWidget()
        right_layout = QVBoxLayout(right_box)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # 头部标题与添加按钮
        header_layout = QHBoxLayout()
        self.lbl_date = QLabel("Scheduled Tasks")
        self.lbl_date.setFont(ui_font(12, QFont.Weight.Bold, widget=self))
        self.lbl_date.setStyleSheet(f"color: {TEXT.name()}; background: transparent;")

        self.btn_add = QPushButton("+ Schedule")
        self.btn_add.setFont(ui_font(11, QFont.Weight.Bold, widget=self))
        self.btn_add.setStyleSheet(glass_button_style(DEFAULT_PURPLE, QColor(255, 255, 255), widget=self))
        self.btn_add.clicked.connect(self._open_add_dialog)

        header_layout.addWidget(self.lbl_date)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_add)
        right_layout.addLayout(header_layout)

        # 任务列表组件
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
            }}
            QListWidget::item {{
                background: rgba(255, 255, 255, 0.4);
                border-radius: 8px;
                padding: 6px;
                margin-bottom: 4px;
                color: {TEXT.name()};
            }}
            {glass_scrollbar_style()}
        """)
        right_layout.addWidget(self.list_widget, 1)

        layout.addWidget(right_box, 2)
        
        # 初始加载当天数据
        self.refresh_task_list()

    def get_selected_date(self) -> date:
        """获取当前日历选中的 Python date 对象"""
        q_date = self.calendar.selectedDate()
        return date(q_date.year(), q_date.month(), q_date.day())

    def refresh_task_list(self):
        """刷新右侧列表数据"""
        self.list_widget.clear()
        sel_date = self.get_selected_date()
        self.lbl_date.setText(f"Tasks for {sel_date.strftime('%Y-%m-%d')}")

        tasks = self.db.get_calendar_tasks_for_date(sel_date)
        if not tasks:
            item = QListWidgetItem("No tasks scheduled for this day.")
            item.setForeground(Qt.GlobalColor.gray)
            self.list_widget.addItem(item)
            return

        for task in tasks:
            time_str = task["start_time"].split(" ")[1][:5]
            rule = task["recurrence_rule"]
            rule_str = f" [{rule.upper()}]" if rule != "none" else ""
            
            text = f"⏰ {time_str} | {task['category']} - {task['task_name']}{rule_str}"
            item = QListWidgetItem(text)
            self.list_widget.addItem(item)

    def _open_add_dialog(self):
        dlg = CalendarTaskDialog(self, default_date=self.get_selected_date())
        if dlg.exec():
            data = dlg.get_data()
            self.db.add_calendar_task(
                task_name=data["task_name"],
                category=data["category"],
                start_time=data["start_time"],
                recurrence_rule=data["recurrence_rule"]
            )
            self.refresh_task_list()
            self.task_added.emit()