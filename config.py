# -*- coding: utf-8 -*-
from PySide6.QtGui import QColor

APP_NAME = "Time Tracker"
DEFAULT_CATEGORIES = ["Work", "Study", "Meal", "Fun", "Commute", "Exercise", "Rest", "Other"]
DEFAULT_TASK_PLACEHOLDER = "(No details)"

CATEGORY_ALIASES = {
    "工作": "Work", "学习": "Study", "吃饭": "Meal", "娱乐": "Fun",
    "通勤": "Commute", "运动": "Exercise", "休息": "Rest", "其他": "Other",
    "Work": "Work", "Study": "Study", "Meal": "Meal", "Fun": "Fun",
    "Commute": "Commute", "Exercise": "Exercise", "Rest": "Rest", "Other": "Other",
}

DEFAULT_MINT = QColor(134, 231, 220)
DEFAULT_PURPLE = QColor(107, 113, 217)
TEXT = QColor(33, 42, 60)
SUBTEXT = QColor(90, 100, 120)
WEEKEND = QColor(191, 132, 139)

DEFAULT_GLASS_OPACITY_SCALE = 1.18