# -*- coding: utf-8 -*-
import sys
import ctypes
from datetime import datetime, timezone
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QFont, QColor, QPixmap, QPainter, QRadialGradient, QBrush
from PySide6.QtWidgets import QApplication

# ----------------------------------------------------------------------
# 1. 时间与字符串处理工具
# ----------------------------------------------------------------------

def now_local() -> datetime:
    """获取当前本地时间（带有本地时区信息）"""
    return datetime.now().astimezone()


def dt_to_str(dt: datetime) -> str:
    """将 datetime 对象转换为标准的 ISO 格式字符串"""
    if dt is None:
        return ""
    return dt.isoformat()


def str_to_dt(s: str) -> datetime:
    """将 ISO 格式字符串解析为 datetime 对象"""
    if not s:
        return now_local()
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.astimezone()
        return dt
    except Exception:
        return now_local()


def fmt_hms(seconds: int) -> str:
    """将总秒数格式化为 HH:MM:SS 或 MM:SS 字符串"""
    sec = max(0, int(seconds))
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


# ----------------------------------------------------------------------
# 2. Windows 系统底层与原生 API 操作
# ----------------------------------------------------------------------

def hide_windows_console():
    """在 Windows 系统下隐藏控制台黑框"""
    if sys.platform == "win32":
        try:
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 0
            )
        except Exception:
            pass


def ensure_single_instance(mutex_name: str = "TimeTracker_SingleInstance_Mutex") -> bool:
    """通过 Windows Mutex 确保程序只运行单实例"""
    if sys.platform == "win32":
        try:
            kernel32 = ctypes.windll.kernel32
            mutex = kernel32.CreateMutexW(None, False, mutex_name)
            last_error = kernel32.GetLastError()
            ERROR_ALREADY_EXISTS = 183
            if last_error == ERROR_ALREADY_EXISTS:
                return False
        except Exception:
            pass
    return True


def ensure_windows_autostart(app_name: str = "TimeTracker"):
    """注册/检查 Windows 开机自启（通过注册表 Run 键）"""
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            executable_path = f'"{sys.executable}" "{sys.argv[0]}"'
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, executable_path)
            winreg.CloseKey(key)
        except Exception:
            pass


def try_enable_native_blur(hwnd: int):
    """为 Windows 窗口启用原生的 Accent/Acrylic 毛玻璃效果"""
    if sys.platform != "win32" or not hwnd:
        return
    try:
        user32 = ctypes.windll.user32
        
        # ACCENT_POLICY 结构定义
        class ACCENT_POLICY(ctypes.Structure):
            _fields_ = [
                ("AccentState", ctypes.c_int),
                ("AccentFlags", ctypes.c_int),
                ("GradientColor", ctypes.c_uint),
                ("AnimationId", ctypes.c_int),
            ]

        class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
            _fields_ = [
                ("Attribute", ctypes.c_int),
                ("Data", ctypes.c_void_p),
                ("SizeOfData", ctypes.c_size_t),
            ]

        # ACCENT_ENABLE_BLURBEHIND = 3, ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
        accent = ACCENT_POLICY()
        accent.AccentState = 3  # BlurBehind
        accent.AccentFlags = 2
        accent.GradientColor = 0x00FFFFFF

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = 19  # WCA_ACCENT_POLICY
        data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p)
        data.SizeOfData = ctypes.sizeof(accent)

        user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
    except Exception:
        pass


def apply_windows_toolwindow_style(hwnd: int):
    """为窗口添加 WS_EX_TOOLWINDOW 属性，使其不在任务栏显示图标"""
    if sys.platform != "win32" or not hwnd:
        return
    try:
        user32 = ctypes.windll.user32
        GWL_EXSTYLE = -20
        WS_EX_TOOLWINDOW = 0x00000080
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_TOOLWINDOW)
    except Exception:
        pass


# ----------------------------------------------------------------------
# 3. UI 缩放与字体适配
# ----------------------------------------------------------------------

def ui_scale_for(widget) -> float:
    """根据 widget 当前所在的屏幕 DPI 动态计算 UI 缩放比例系数"""
    try:
        screen = widget.screen() if widget else None
        if not screen:
            screen = QApplication.primaryScreen()
        if screen:
            dpi = screen.logicalDotsPerInch()
            return max(0.8, dpi / 96.0)
    except Exception:
        pass
    return 1.0


def sp(size_px: float, widget=None) -> int:
    """根据 DPI 缩放像素尺寸，返回适合当前设备的整型 px"""
    scale = ui_scale_for(widget)
    return max(1, int(round(size_px * scale)))


def ui_font(size_px: float, weight=QFont.Weight.Normal, bold=False, widget=None) -> QFont:
    """生成具备 DPI 适应能力的标准的系统 UI 字体对象"""
    font = QFont("Segoe UI", sp(size_px, widget))
    if bold:
        font.setBold(True)
    else:
        font.setWeight(weight)
    return font


# ----------------------------------------------------------------------
# 4. QPainter 绘图与色彩辅助函数
# ----------------------------------------------------------------------

def blend(c1: QColor, c2: QColor, factor: float) -> QColor:
    """在两个颜色之间进行线性插值混合 (factor 范围 0.0 ~ 1.0)"""
    f = max(0.0, min(1.0, factor))
    r = int(c1.red() * (1 - f) + c2.red() * f)
    g = int(c1.green() * (1 - f) + c2.green() * f)
    b = int(c1.blue() * (1 - f) + c2.blue() * f)
    a = int(c1.alpha() * (1 - f) + c2.alpha() * f)
    return QColor(r, g, b, a)


def get_noise_pixmap(width: int = 128, height: int = 128, opacity: float = 0.03) -> QPixmap:
    """生成软磨砂颗粒（Noise/Grain）纹理贴图，增强玻璃质感"""
    import random
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    alpha = int(255 * opacity)
    
    for x in range(width):
        for y in range(height):
            if random.random() > 0.5:
                val = random.randint(200, 255)
                painter.setPen(QColor(val, val, val, alpha))
                painter.drawPoint(x, y)
                
    painter.end()
    return pixmap