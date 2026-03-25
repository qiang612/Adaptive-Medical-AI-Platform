"""
数据库迁移脚本：为 teaching_cases 表添加新字段
运行方式：python backend/scripts/migrate_teaching_cases.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine


def migrate():
    new_columns = [
        ("images", "JSON"),
        ("diagnosis", "TEXT"),
        ("treatment", "TEXT"),
        ("tags", "JSON"),
        ("update_time", "DATETIME"),
    ]

    with engine.connect() as conn:
        for column_name, column_type in new_columns:
            try:
                sql = f"ALTER TABLE teaching_cases ADD COLUMN {column_name} {column_type}"
                conn.execute(text(sql))
                conn.commit()
                print(f"Added column: {column_name}")
            except Exception as e:
                if "Duplicate column" in str(e) or "already exists" in str(e).lower():
                    print(f"Column already exists: {column_name}")
                else:
                    print(f"Error adding column {column_name}: {e}")

    print("Migration completed!")


if __name__ == "__main__":
    migrate()
