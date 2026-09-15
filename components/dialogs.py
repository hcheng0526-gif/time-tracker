# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt, QPoint, QSize, QDateTime
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QComboBox, QSpinBox, QFormLayout,
    QGraphicsDropShadowEffect, QDateTimeEdit
)

from config import DEFAULT_CATEGORIES, TEXT, SUBTEXT, DEFAULT_MINT, DEFAULT_PURPLE
from utils import sp, ui_font, try_enable_native_blur
from components.glass_card import LightGlassCard
from components.styles import glass_button_style, glass_input_style


# ----------------------------------------------------------------------
# 1. 窗口拖拽标题栏组件
# ----------------------------------------------------------------------

class DialogTitleBar(QWidget):
    """自定义玻璃风格对话框标题栏（支持鼠标按压拖拽与关闭按钮）"""

    def __init__(self, title: str, parent_dialog: QDialog):
        super().__init__(parent_dialog)
        self.dialog = parent_dialog
        self._drag_pos = QPoint()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 12, 8)
        layout.setSpacing(8)

        # 标题文本
        self.lbl_title = QLabel(title)
        self.lbl_title.setFont(ui_font(13, QFont.Weight.Bold, widget=self))
        self.lbl_title.setStyleSheet(f"color: {TEXT.name()}; background: transparent;")
        layout.addWidget(self.lbl_title)

        layout.addStretch()

        # 关闭按钮
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(sp(24, self), sp(24, self))
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #888888;
                border: none;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(235, 87, 87, 0.2);
                color: #eb5757;
            }
        """)
        self.btn_close.clicked.connect(self.dialog.reject)
        layout.addWidget(self.btn_close)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.dialog.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            self.dialog.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()


# ----------------------------------------------------------------------
# 2. 通用玻璃无边框对话框基类
# ----------------------------------------------------------------------

class GlassDialog(QDialog):
    """具有原生毛玻璃背景与无边框阴影的对话框基类"""

    def __init__(self, title: str = "", parent=None, width_px: float = 380, height_px: float = 260):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(sp(width_px, self), sp(height_px, self))

        # 尝试开启 Windows 原生 Accent 毛玻璃效果
        try_enable_native_blur(int(self.winId()))

        # 主外层布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 玻璃卡片主体容器
        self.card = LightGlassCard(self, radius_px=18, bg_alpha=200, border_alpha=80)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(0, 0, 0, 12)
        card_layout.setSpacing(8)

        # 标题栏
        self.title_bar = DialogTitleBar(title, self)
        card_layout.addWidget(self.title_bar)

        # 内容区域容器
        self.content_widget = QWidget(self.card)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(16, 4, 16, 8)
        card_layout.addWidget(self.content_widget)

        main_layout.addWidget(self.card)


# ----------------------------------------------------------------------
# 3. 设置对话框 (SettingsDialog)
# ----------------------------------------------------------------------

class SettingsDialog(GlassDialog):
    """系统与偏好设置弹窗"""

    def __init__(self, parent=None):
        super().__init__("Settings & Preferences", parent, width_px=360, height_px=280)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # 示例选项：自动启动
        self.lbl_autostart = QLabel("Start with Windows")
        self.lbl_autostart.setFont(ui_font(12, widget=self))
        self.chk_autostart = QComboBox()
        self.chk_autostart.addItems(["Enabled", "Disabled"])
        self.chk_autostart.setStyleSheet(glass_input_style(self))

        # 示例选项：全局透明度
        self.lbl_opacity = QLabel("Glass Opacity Scale")
        self.lbl_opacity.setFont(ui_font(12, widget=self))
        self.spn_opacity = QSpinBox()
        self.spn_opacity.setRange(80, 150)
        self.spn_opacity.setValue(118)
        self.spn_opacity.setSuffix("%")
        self.spn_opacity.setStyleSheet(glass_input_style(self))

        form_layout.addRow(self.lbl_autostart, self.chk_autostart)
        form_layout.addRow(self.lbl_opacity, self.spn_opacity)

        self.content_layout.addLayout(form_layout)
        self.content_layout.addStretch()

        # 确认保存按钮
        self.btn_save = QPushButton("Save Settings")
        self.btn_save.setFont(ui_font(12, QFont.Weight.Bold, widget=self))
        self.btn_save.setStyleSheet(glass_button_style(DEFAULT_PURPLE, QColor(255, 255, 255), widget=self))
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.clicked.connect(self.accept)
        self.content_layout.addWidget(self.btn_save)


# ----------------------------------------------------------------------
# 4. 任务手动录入对话框 (TaskDialog)
# ----------------------------------------------------------------------

class TaskDialog(GlassDialog):
    """手动添加或补录时间记录弹窗"""

    def __init__(self, parent=None, categories=None):
        super().__init__("Log Task Session", parent, width_px=380, height_px=320)
        cats = categories or DEFAULT_CATEGORIES

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # 分类选择
        self.cmb_category = QComboBox()
        self.cmb_category.addItems(cats)
        self.cmb_category.setStyleSheet(glass_input_style(self))

        # 任务名称/明细
        self.txt_task = QLineEdit()
        self.txt_task.setPlaceholderText("What were you working on?")
        self.txt_task.setStyleSheet(glass_input_style(self))

        # 时长输入 (分钟)
        self.spn_duration = QSpinBox()
        self.spn_duration.setRange(1, 1440)
        self.spn_duration.setValue(30)
        self.spn_duration.setSuffix(" mins")
        self.spn_duration.setStyleSheet(glass_input_style(self))

        form_layout.addRow("Category:", self.cmb_category)
        form_layout.addRow("Task Name:", self.txt_task)
        form_layout.addRow("Duration:", self.spn_duration)

        self.content_layout.addLayout(form_layout)
        self.content_layout.addStretch()

        # 提交按钮
        self.btn_submit = QPushButton("Log Session")
        self.btn_submit.setFont(ui_font(12, QFont.Weight.Bold, widget=self))
        self.btn_submit.setStyleSheet(glass_button_style(DEFAULT_MINT, TEXT, widget=self))
        self.btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_submit.clicked.connect(self.accept)
        self.content_layout.addWidget(self.btn_submit)

    def get_data(self):
        """获取提交的数据"""
        return {
            "category": self.cmb_category.currentText(),
            "task_name": self.txt_task.text().strip() or "(No details)",
            "duration_minutes": self.spn_duration.value()
        }


# ----------------------------------------------------------------------
# 5. 计划与目标设定对话框 (PlanDialog)
# ----------------------------------------------------------------------

class PlanDialog(GlassDialog):
    """设置分类目标时长弹窗"""

    def __init__(self, parent=None, categories=None):
        super().__init__("Set Daily Target", parent, width_px=360, height_px=280)
        cats = categories or DEFAULT_CATEGORIES

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.cmb_category = QComboBox()
        self.cmb_category.addItems(cats)
        self.cmb_category.setStyleSheet(glass_input_style(self))

        self.spn_target_hours = QSpinBox()
        self.spn_target_hours.setRange(1, 24)
        self.spn_target_hours.setValue(2)
        self.spn_target_hours.setSuffix(" hours/day")
        self.spn_target_hours.setStyleSheet(glass_input_style(self))

        form_layout.addRow("Category:", self.cmb_category)
        form_layout.addRow("Target:", self.spn_target_hours)

        self.content_layout.addLayout(form_layout)
        self.content_layout.addStretch()

        self.btn_save = QPushButton("Set Target")
        self.btn_save.setFont(ui_font(12, QFont.Weight.Bold, widget=self))
        self.btn_save.setStyleSheet(glass_button_style(DEFAULT_PURPLE, QColor(255, 255, 255), widget=self))
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.clicked.connect(self.accept)
        self.content_layout.addWidget(self.btn_save)

    def get_data(self):
        """获取设置的目标数据 (转化为秒)"""
        return {
            "category": self.cmb_category.currentText(),
            "target_seconds": self.spn_target_hours.value() * 3600
        }
# ----------------------------------------------------------------------
# 6. 新增支持设置开始时间和循环周期的弹窗组件
# ----------------------------------------------------------------------
class CalendarTaskDialog(GlassDialog):
    """提前预约/循环任务添加弹窗"""

    def __init__(self, parent=None, categories=None, default_date: date = None):
        super().__init__("Schedule Task", parent, width_px=400, height_px=360)
        cats = categories or DEFAULT_CATEGORIES

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # 任务名称
        self.txt_task = QLineEdit()
        self.txt_task.setPlaceholderText("Task description...")
        self.txt_task.setStyleSheet(glass_input_style(self))

        # 分类
        self.cmb_category = QComboBox()
        self.cmb_category.addItems(cats)
        self.cmb_category.setStyleSheet(glass_input_style(self))

        # 开始时间（日期 + 时间）
        self.dt_edit = QDateTimeEdit()
        init_dt = QDateTime.currentDateTime()
        if default_date:
            init_dt.setDate(default_date)
        self.dt_edit.setDateTime(init_dt)
        self.dt_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.dt_edit.setStyleSheet(glass_input_style(self))

        # 循环规则
        self.cmb_recurrence = QComboBox()
        self.cmb_recurrence.addItem("One-time (Once)", "none")
        self.cmb_recurrence.addItem("Every Day", "daily")
        self.cmb_recurrence.addItem("Every Week", "weekly")
        self.cmb_recurrence.addItem("Every Month", "monthly")
        self.cmb_recurrence.setStyleSheet(glass_input_style(self))

        form_layout.addRow("Task:", self.txt_task)
        form_layout.addRow("Category:", self.cmb_category)
        form_layout.addRow("Start Time:", self.dt_edit)
        form_layout.addRow("Repeat:", self.cmb_recurrence)

        self.content_layout.addLayout(form_layout)
        self.content_layout.addStretch()

        # 提交按钮
        self.btn_submit = QPushButton("Add to Schedule")
        self.btn_submit.setFont(ui_font(12, QFont.Weight.Bold, widget=self))
        self.btn_submit.setStyleSheet(glass_button_style(DEFAULT_PURPLE, QColor(255, 255, 255), widget=self))
        self.btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_submit.clicked.connect(self.accept)
        self.content_layout.addWidget(self.btn_submit)

    def get_data(self):
        """获取任务数据"""
        q_dt = self.dt_edit.dateTime()
        py_dt = datetime(
            q_dt.date().year(), q_dt.date().month(), q_dt.date().day(),
            q_dt.time().hour(), q_dt.time().minute()
        )
        return {
            "task_name": self.txt_task.text().strip() or "(No Details)",
            "category": self.cmb_category.currentText(),
            "start_time": py_dt,
            "recurrence_rule": self.cmb_recurrence.currentData()
        }
