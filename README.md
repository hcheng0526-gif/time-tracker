[Plaintext.txt](https://github.com/user-attachments/files/32224763/Plaintext.txt)
# time-trackerTimeTracker/
│
├── main.py                    # 主入口文件（应用初始化、单例控制、托盘等）
├── config.py                  # 全局常量、默认参数、主题色彩定义
├── utils.py                   # 通用工具函数（时间格式化、系统特性判定等）
│
├── database/                  # 数据库管理层
│   ├── __init__.py
│   └── db_manager.py          # TrackerDB 类（SQLite 基础操作及 CRUD）
│
├── components/                # 抽象公共UI组件与样式
│   ├── __init__.py
│   ├── background.py          # LightWallpaperBackground 毛玻璃渐变背景
│   ├── glass_card.py          # LightGlassCard 基础玻璃卡片基类
│   ├── dialogs.py             # GlassDialog, SettingsDialog, TaskDialog 等对话框
│   └── styles.py              # 共享 QSS 样式函数与 helper 函数 (glass_button_style 等)
│
└── widgets/                   # 核心业务功能部件
    ├── __init__.py
    ├── timer_widget.py        # 计时器部件 (TimerWidget)
    ├── stats_widget.py        # 饼图/环形统计图部件 (StatsWidget)
    └── range_stats_card.py    # 范围统计卡片部件 (RangeStatsCard)
