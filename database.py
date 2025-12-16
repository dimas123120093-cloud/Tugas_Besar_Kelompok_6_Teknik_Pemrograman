"""
================================================================================
DATABASE MODULE - SQLite Database Handler
================================================================================
Modul ini menangani semua operasi database SQLite untuk aplikasi Logbook.
Menggunakan context manager untuk koneksi yang aman.
================================================================================
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

DATABASE_FILE = "logbook.db"


@contextmanager
def get_connection():
    """
    Context manager untuk koneksi database yang aman.
    Otomatis commit dan close connection.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Akses kolom dengan nama
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    """
    Inisialisasi database dengan membuat tabel-tabel yang diperlukan.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Tabel Projects
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                estimated_hours REAL NOT NULL,
                category TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabel Activities
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                duration_hours REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # Tabel Settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        # Insert default settings jika belum ada
        cursor.execute("""
            INSERT OR IGNORE INTO settings (key, value) VALUES 
            ('target_hours_per_day', '8'),
            ('efficiency_threshold', '0.7')
        """)
        
        # Create indexes untuk performa
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_project ON activities(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_start ON activities(start_time)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)")


# ==================== PROJECT OPERATIONS ====================

def create_project(name: str, description: str, estimated_hours: float, 
                   category: str) -> int:
    """
    Membuat proyek baru.
    
    Returns:
        int: ID proyek yang baru dibuat
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO projects (name, description, estimated_hours, category)
            VALUES (?, ?, ?, ?)
        """, (name, description, estimated_hours, category))
        return cursor.lastrowid


def get_all_projects() -> List[Dict]:
    """Mendapatkan semua proyek."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, 
                   COALESCE(SUM(a.duration_hours), 0) as total_logged_hours
            FROM projects p
            LEFT JOIN activities a ON p.id = a.project_id
            GROUP BY p.id
            ORDER BY p.created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def get_active_projects() -> List[Dict]:
    """Mendapatkan proyek yang aktif saja."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, 
                   COALESCE(SUM(a.duration_hours), 0) as total_logged_hours
            FROM projects p
            LEFT JOIN activities a ON p.id = a.project_id
            WHERE p.status = 'active'
            GROUP BY p.id
            ORDER BY p.created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def get_project_by_id(project_id: int) -> Optional[Dict]:
    """Mendapatkan proyek berdasarkan ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, 
                   COALESCE(SUM(a.duration_hours), 0) as total_logged_hours
            FROM projects p
            LEFT JOIN activities a ON p.id = a.project_id
            WHERE p.id = ?
            GROUP BY p.id
        """, (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_project(project_id: int, name: str, description: str, 
                   estimated_hours: float, category: str, status: str) -> bool:
    """Update data proyek."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE projects 
            SET name = ?, description = ?, estimated_hours = ?, 
                category = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (name, description, estimated_hours, category, status, project_id))
        return cursor.rowcount > 0


def update_project_status(project_id: int, status: str) -> bool:
    """Update status proyek."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE projects 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, project_id))
        return cursor.rowcount > 0


def delete_project(project_id: int) -> bool:
    """Hapus proyek (cascade delete activities)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        # Hapus activities dulu
        cursor.execute("DELETE FROM activities WHERE project_id = ?", (project_id,))
        # Hapus project
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        return cursor.rowcount > 0


# ==================== ACTIVITY OPERATIONS ====================

def create_activity(project_id: int, start_time: datetime, 
                    end_time: Optional[datetime] = None,
                    notes: str = "") -> int:
    """
    Membuat aktivitas baru.
    
    Returns:
        int: ID aktivitas yang baru dibuat
    """
    duration = None
    if end_time:
        duration = (end_time - start_time).total_seconds() / 3600
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO activities (project_id, start_time, end_time, duration_hours, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (project_id, start_time, end_time, duration, notes))
        return cursor.lastrowid