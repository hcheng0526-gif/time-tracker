# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional


class TrackerDB:
    """时间追踪器与日历计划 SQLite 数据库管理类"""

    def __init__(self, db_name: str = "tracker.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接并配置行记录转换为字典格式"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. 专注会话记录表 (Focus Sessions)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS focus_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    task_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    duration INTEGER NOT NULL
                )
            """)

            # 2. 预设任务列表表 (Task Preset List)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_list (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    task_name TEXT NOT NULL
                )
            """)

            # 3. 日历任务与循环计划表 (Calendar Schedule & Recurrence Tasks)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calendar_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    scheduled_time TEXT NOT NULL,
                    recurrence_type TEXT DEFAULT 'none',
                    is_completed INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)

            conn.commit()

    # =========================================================================
    # 专注会话与任务预设相关操作 (Focus Sessions & Task Presets)
    # =========================================================================

    def add_focus_session(self, category: str, task_name: str, start_time: datetime, end_time: datetime) -> int:
        """记录一次专注会话"""
        duration = int((end_time - start_time).total_seconds())
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO focus_sessions (category, task_name, start_time, end_time, duration)
                VALUES (?, ?, ?, ?, ?)
            """, (
                category,
                task_name,
                start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time.strftime("%Y-%m-%d %H:%M:%S"),
                duration
            ))
            conn.commit()
            return cursor.lastrowid

    def get_todays_sessions((self) -> List[Dict[str, Any]]:
        """获取今天的专注记录"""
        today_str = date.today().strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM focus_sessions 
                WHERE start_time LIKE ? 
                ORDER BY start_time DESC
            """, (f"{today_str}%",))
            return [dict(row) for row in cursor.fetchall()]

    def add_preset_task(self, category: str, task_name: str) -> int:
        """添加预设任务"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO task_list (category, task_name)
                VALUES (?, ?)
            """, (category, task_name))
            conn.commit()
            return cursor.lastrowid

    def get_all_preset_tasks(self) -> List[Dict[str, Any]]:
        """获取所有预设任务"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM task_list ORDER BY category, task_name")
            return [dict(row) for row in cursor.fetchall()]

    # =========================================================================
    # 日历计划与循环任务相关操作 (Calendar Tasks & Recurrence Logic)
    # =========================================================================

    def add_calendar_task(
        self, 
        title: str, 
        category: str, 
        scheduled_time: datetime, 
        recurrence_type: str = "none"
    ) -> int:
        """
        添加日历计划任务
        :param title: 任务标题
        :param category: 任务分类
        :param scheduled_time: 计划日期时间 (datetime 对象)
        :param recurrence_type: 循环类型 ('none' 单次, 'daily' 每天, 'weekly' 每周, 'monthly' 每月)
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_str = scheduled_time.strftime("%Y-%m-%d %H:%M:%S")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO calendar_tasks (title, category, scheduled_time, recurrence_type, is_completed, created_at)
                VALUES (?, ?, ?, ?, 0, ?)
            """, (title, category, time_str, recurrence_type, now_str))
            conn.commit()
            return cursor.lastrowid

    def get_calendar_tasks_for_date(self, target_date: date) -> List[Dict[str, Any]]:
        """
        根据日期获取当天的计划任务（自动算入匹配的循环任务）
        :param target_date: 目标日期 (date 对象)
        """
        target_str = target_date.strftime("%Y-%m-%d")
        matching_tasks = []

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM calendar_tasks")
            rows = [dict(r) for r in cursor.fetchall()]

            for task in rows:
                task_dt = datetime.strptime(task["scheduled_time"], "%Y-%m-%d %H:%M:%S")
                task_date = task_dt.date()
                rec = task.get("recurrence_type", "none")

                # 1. 任务创建于目标日期之后，跳过
                if task_date > target_date:
                    continue

                # 2. 单次任务匹配精确日期
                if rec == "none" and task_date == target_date:
                    matching_tasks.append(task)
                # 3. 每天循环
                elif rec == "daily":
                    matching_tasks.append(task)
                # 4. 每周循环（同星期几）
                elif rec == "weekly" and task_date.weekday() == target_date.weekday():
                    matching_tasks.append(task)
                # 5. 每月循环（同几号）
                elif rec == "monthly" and task_date.day == target_date.day:
                    matching_tasks.append(task)

        return matching_tasks

    def toggle_calendar_task_completion(self, task_id: int, is_completed: bool):
        """切换日历任务完成状态"""
        status_val = 1 if is_completed else 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE calendar_tasks 
                SET is_completed = ? 
                WHERE id = ?
            """, (status_val, task_id))
            conn.commit()

    def delete_calendar_task(self, task_id: int):
        """删除指定的日历任务"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM calendar_tasks WHERE id = ?", (task_id,))
            conn.commit()
