# -*- coding: utf-8 -*-
import os
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta


class TrackerDB:
    """时间追踪器数据库管理类，统一处理所有 SQLite 交互"""

    def __init__(self, db_path: str = "time_tracker.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接并配置 Row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """初始化数据库表结构"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. 记录表 (sessions)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    task_name TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # 2. 计划目标表 (plans)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    target_seconds INTEGER NOT NULL,
                    period_type TEXT NOT NULL, -- 'daily', 'weekly', 'monthly'
                    created_at TEXT NOT NULL
                )
            """)

            # 3. 每日待办事项表 (daily_todos)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    todo_date TEXT NOT NULL,
                    task_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    completed INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)
           # 4. 日历与循环任务表 (calendar_tasks)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calendar_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    recurrence_rule TEXT DEFAULT 'none',
                    is_completed INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)

            conn.commit()

    # ----------------------------------------------------------------------
    # Session 关联操作 (时间记录)
    # ----------------------------------------------------------------------

    def add_session(self, category: str, task_name: str, start_time: datetime, end_time: datetime) -> int:
        """添加一条时间记录"""
        duration = int((end_time - start_time).total_seconds())
        if duration < 0:
            duration = 0

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (category, task_name, start_time, end_time, duration, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                category,
                task_name,
                start_time.isoformat(),
                end_time.isoformat(),
                duration,
                datetime.now().isoformat()
            ))
            conn.commit()
            return cursor.lastrowid

    def delete_session(self, session_id: int):
        """删除一条时间记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()

    def get_sessions_range(self, start_dt: datetime, end_dt: datetime) -> List[Dict[str, Any]]:
        """按时间范围查询记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sessions
                WHERE start_time >= ? AND start_time <= ?
                ORDER BY start_time DESC
            """, (start_dt.isoformat(), end_dt.isoformat()))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_category_durations(self, start_dt: datetime, end_dt: datetime) -> Dict[str, int]:
        """按分类统计指定时间范围内的总时长 (秒)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT category, SUM(duration) as total_duration
                FROM sessions
                WHERE start_time >= ? AND start_time <= ?
                GROUP BY category
            """, (start_dt.isoformat(), end_dt.isoformat()))
            rows = cursor.fetchall()
            return {row["category"]: row["total_duration"] for row in rows}

    # ----------------------------------------------------------------------
    # Plan 关联操作 (目标计划)
    # ----------------------------------------------------------------------

    def set_plan(self, category: str, target_seconds: int, period_type: str = "daily"):
        """设置或更新分类的目标时长"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM plans WHERE category = ? AND period_type = ?
            """, (category, period_type))
            row = cursor.fetchone()

            if row:
                cursor.execute("""
                    UPDATE plans SET target_seconds = ? WHERE id = ?
                """, (target_seconds, row["id"]))
            else:
                cursor.execute("""
                    INSERT INTO plans (category, target_seconds, period_type, created_at)
                    VALUES (?, ?, ?, ?)
                """, (category, target_seconds, period_type, datetime.now().isoformat()))
            conn.commit()

    def get_plans(self, period_type: str = "daily") -> Dict[str, int]:
        """获取指定周期类型的所有计划目标 (秒)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT category, target_seconds FROM plans WHERE period_type = ?
            """, (period_type,))
            rows = cursor.fetchall()
            return {row["category"]: row["target_seconds"] for row in rows}

    # ----------------------------------------------------------------------
    # Daily Todo 关联操作 (待办事项)
    # ----------------------------------------------------------------------

    def add_todo(self, todo_date: str, task_name: str, category: str) -> int:
        """添加一条待办事项"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO daily_todos (todo_date, task_name, category, completed, created_at)
                VALUES (?, ?, ?, 0, ?)
            """, (todo_date, task_name, category, datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid

    def update_todo_status(self, todo_id: int, completed: bool):
        """更新待办事项状态"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE daily_todos SET completed = ? WHERE id = ?
            """, (1 if completed else 0, todo_id))
            conn.commit()

    def delete_todo(self, todo_id: int):
        """删除一条待办事项"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM daily_todos WHERE id = ?", (todo_id,))
            conn.commit()

    def get_todos_for_date(self, todo_date: str) -> List[Dict[str, Any]]:
        """获取指定日期的待办列表 (格式: YYYY-MM-DD)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM daily_todos WHERE todo_date = ? ORDER BY id ASC
            """, (todo_date,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
# --- 在 TrackerDB 类中新增以下方法 ---

    def add_calendar_task(self, task_name: str, category: str, start_time: datetime, recurrence_rule: str = 'none') -> int:
        """添加日历/循环任务"""
      with self._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO calendar_tasks (task_name, category, start_time, recurrence_rule, is_completed, created_at)
            VALUES (?, ?, ?, ?, 0, ?)
        """, (
            task_name,
            category,
            start_time.strftime("%Y-%m-%d %H:%M:%S"),
            recurrence_rule,
            datetime.now().isoformat()
        ))
        conn.commit()
        return cursor.lastrowid

    def get_calendar_tasks_for_date(self, target_date: date) -> List[Dict[str, Any]]:
    """获取指定日期的所有任务（包含单次任务与匹配规则的循环任务）"""
    date_str = target_date.strftime("%Y-%m-%d")
    matched_tasks = []

    with self._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM calendar_tasks")
        rows = cursor.fetchall()

        for row in rows:
            task = dict(row)
            task_dt = datetime.strptime(task["start_time"], "%Y-%m-%d %H:%M:%S")
            task_date = task_dt.date()
            rule = task["recurrence_rule"]

            # 1. 任务日期在目标日期之后，尚未开始
            if task_date > target_date:
                continue

            # 2. 匹配逻辑
            if rule == 'none' and task_date == target_date:
                matched_tasks.append(task)
            elif rule == 'daily':
                matched_tasks.append(task)
            elif rule == 'weekly' and task_date.weekday() == target_date.weekday():
                matched_tasks.append(task)
            elif rule == 'monthly' and task_date.day == target_date.day:
                matched_tasks.append(task)

    return matched_tasks
