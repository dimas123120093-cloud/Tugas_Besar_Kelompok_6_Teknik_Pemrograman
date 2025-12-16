"""
================================================================================
DATABASE MODULE - SQLite Database Handler
================================================================================
Modul ini menangani semua operasi database SQLite untuk aplikasi Logbook.
Menggunakan context manager untuk koneksi yang aman dan parameterized
queries untuk mencegah SQL injection.
================================================================================
Mata Kuliah: Teknik Pemrograman
Program Studi: Teknik Geofisika - Semester 5
================================================================================
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from constants import DATABASE_FILE, DEFAULT_SETTINGS, ERROR_MESSAGES


# ==================== DATABASE CONNECTION ====================

@contextmanager
def get_connection():
    """
    Context manager untuk koneksi database yang aman.
    
    Fungsi ini memastikan:
    - Koneksi ditutup dengan benar setelah selesai
    - Transaction di-commit jika sukses
    - Transaction di-rollback jika terjadi error
    
    Yields:
        sqlite3.Connection: Objek koneksi database
    
    Raises:
        Exception: Meneruskan exception apapun yang terjadi
    
    Examples:
        >>> with get_connection() as conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT * FROM projects")
        ...     results = cursor.fetchall()
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
    
    Tabel yang dibuat:
    - projects: Menyimpan data proyek
    - activities: Menyimpan catatan aktivitas/waktu kerja
    - settings: Menyimpan pengaturan aplikasi
    
    Index yang dibuat untuk optimasi query:
    - idx_activities_project: Index pada project_id di tabel activities
    - idx_activities_start: Index pada start_time di tabel activities
    - idx_projects_status: Index pada status di tabel projects
    
    Note:
        Fungsi ini aman dipanggil berkali-kali (idempotent).
        Tabel hanya dibuat jika belum ada.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # ==================== TABEL PROJECTS ====================
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
        
        # ==================== TABEL ACTIVITIES ====================
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
        
        # ==================== TABEL SETTINGS ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        # Insert default settings jika belum ada
        cursor.execute("""
            INSERT OR IGNORE INTO settings (key, value) VALUES 
            ('target_hours_per_day', ?),
            ('efficiency_threshold', ?)
        """, (
            str(DEFAULT_SETTINGS['target_hours_per_day']),
            str(DEFAULT_SETTINGS['efficiency_threshold'])
        ))
        
        # ==================== INDEXES ====================
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_activities_project ON activities(project_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_activities_start ON activities(start_time)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)"
        )


# ==================== PROJECT OPERATIONS ====================

def create_project(name: str, description: str, estimated_hours: float, 
                   category: str) -> int:
    """
    Membuat proyek baru di database.
    
    Args:
        name: Nama proyek (wajib, tidak boleh kosong)
        description: Deskripsi proyek (opsional)
        estimated_hours: Estimasi jam yang dibutuhkan (wajib, > 0)
        category: Kategori proyek (wajib, harus dari daftar CATEGORIES)
    
    Returns:
        int: ID proyek yang baru dibuat
    
    Raises:
        ValueError: Jika validasi input gagal
        sqlite3.Error: Jika terjadi error database
    
    Examples:
        >>> project_id = create_project(
        ...     "Pengolahan Seismik",
        ...     "Analisis data seismik 2D",
        ...     20.0,
        ...     "Pengolahan Data Seismik"
        ... )
        >>> print(project_id)
        1
    """
    # Validasi input
    if not name or not name.strip():
        raise ValueError(ERROR_MESSAGES["project_name_required"])
    
    if estimated_hours <= 0:
        raise ValueError(ERROR_MESSAGES["estimated_hours_invalid"])
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO projects (name, description, estimated_hours, category)
            VALUES (?, ?, ?, ?)
        """, (name.strip(), description, estimated_hours, category))
        return cursor.lastrowid


def get_all_projects() -> List[Dict]:
    """
    Mendapatkan semua proyek beserta total jam yang tercatat.
    
    Returns:
        List[Dict]: List dictionary proyek dengan field:
            - id, name, description, estimated_hours, category
            - status, created_at, updated_at
            - total_logged_hours: Total jam yang sudah dicatat
    
    Note:
        Proyek diurutkan berdasarkan tanggal pembuatan (terbaru dulu).
    """
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
    """
    Mendapatkan proyek yang berstatus aktif saja.
    
    Returns:
        List[Dict]: List dictionary proyek aktif
    
    Note:
        Hanya proyek dengan status='active' yang dikembalikan.
    """
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
    """
    Mendapatkan detail proyek berdasarkan ID.
    
    Args:
        project_id: ID proyek yang dicari
    
    Returns:
        Optional[Dict]: Dictionary proyek jika ditemukan, None jika tidak ada
    """
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
    """
    Memperbarui data proyek.
    
    Args:
        project_id: ID proyek yang akan diupdate
        name: Nama proyek baru
        description: Deskripsi baru
        estimated_hours: Estimasi jam baru
        category: Kategori baru
        status: Status baru ('active', 'completed', atau 'paused')
    
    Returns:
        bool: True jika berhasil, False jika proyek tidak ditemukan
    
    Raises:
        ValueError: Jika validasi input gagal
    """
    if not name or not name.strip():
        raise ValueError(ERROR_MESSAGES["project_name_required"])
    
    if estimated_hours <= 0:
        raise ValueError(ERROR_MESSAGES["estimated_hours_invalid"])
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE projects 
            SET name = ?, description = ?, estimated_hours = ?, 
                category = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (name.strip(), description, estimated_hours, category, status, project_id))
        return cursor.rowcount > 0


def update_project_status(project_id: int, status: str) -> bool:
    """
    Memperbarui status proyek saja.
    
    Args:
        project_id: ID proyek
        status: Status baru ('active', 'completed', atau 'paused')
    
    Returns:
        bool: True jika berhasil, False jika proyek tidak ditemukan
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE projects 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, project_id))
        return cursor.rowcount > 0


def delete_project(project_id: int) -> bool:
    """
    Menghapus proyek dan semua aktivitas terkait.
    
    Args:
        project_id: ID proyek yang akan dihapus
    
    Returns:
        bool: True jika berhasil, False jika proyek tidak ditemukan
    
    Warning:
        Operasi ini juga menghapus semua aktivitas yang terkait
        dengan proyek (cascade delete).
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        # Hapus activities dulu (karena foreign key)
        cursor.execute("DELETE FROM activities WHERE project_id = ?", (project_id,))
        # Hapus project
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        return cursor.rowcount > 0


# ==================== ACTIVITY OPERATIONS ====================

def create_activity(project_id: int, start_time: datetime, 
                    end_time: Optional[datetime] = None,
                    notes: str = "") -> int:
    """
    Membuat catatan aktivitas baru.
    
    Aktivitas bisa dibuat dalam dua mode:
    1. Ongoing (end_time=None): Aktivitas sedang berjalan
    2. Completed (end_time diisi): Aktivitas dengan durasi tertentu
    
    Args:
        project_id: ID proyek terkait
        start_time: Waktu mulai aktivitas
        end_time: Waktu selesai (opsional, None untuk aktivitas ongoing)
        notes: Catatan aktivitas (opsional)
    
    Returns:
        int: ID aktivitas yang baru dibuat
    
    Raises:
        ValueError: Jika end_time <= start_time (durasi tidak valid)
    
    Examples:
        >>> # Aktivitas ongoing
        >>> activity_id = create_activity(1, datetime.now())
        >>> 
        >>> # Aktivitas completed
        >>> start = datetime(2024, 12, 15, 9, 0)
        >>> end = datetime(2024, 12, 15, 12, 0)
        >>> activity_id = create_activity(1, start, end, "QC data seismik")
    """
    duration = None
    
    if end_time is not None:
        # VALIDASI: end_time harus setelah start_time
        if end_time <= start_time:
            raise ValueError(ERROR_MESSAGES["end_time_before_start"])
        
        # Hitung durasi dalam jam
        duration = (end_time - start_time).total_seconds() / 3600
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO activities (project_id, start_time, end_time, duration_hours, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (project_id, start_time, end_time, duration, notes))
        return cursor.lastrowid


def get_all_activities() -> List[Dict]:
    """
    Mendapatkan semua aktivitas beserta info proyek terkait.
    
    Returns:
        List[Dict]: List dictionary aktivitas dengan field tambahan:
            - project_name: Nama proyek terkait
            - project_category: Kategori proyek terkait
    
    Note:
        Aktivitas diurutkan berdasarkan waktu mulai (terbaru dulu).
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, p.name as project_name, p.category as project_category
            FROM activities a
            JOIN projects p ON a.project_id = p.id
            ORDER BY a.start_time DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def get_activities_by_project(project_id: int) -> List[Dict]:
    """
    Mendapatkan aktivitas berdasarkan proyek tertentu.
    
    Args:
        project_id: ID proyek
    
    Returns:
        List[Dict]: List aktivitas untuk proyek tersebut
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, p.name as project_name, p.category as project_category
            FROM activities a
            JOIN projects p ON a.project_id = p.id
            WHERE a.project_id = ?
            ORDER BY a.start_time DESC
        """, (project_id,))
        return [dict(row) for row in cursor.fetchall()]


def get_ongoing_activities() -> List[Dict]:
    """
    Mendapatkan aktivitas yang sedang berjalan (belum selesai).
    
    Returns:
        List[Dict]: List aktivitas dengan end_time = NULL
    
    Note:
        Aktivitas ongoing adalah aktivitas yang sudah dimulai
        tetapi belum ditandai selesai.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, p.name as project_name, p.category as project_category
            FROM activities a
            JOIN projects p ON a.project_id = p.id
            WHERE a.end_time IS NULL
            ORDER BY a.start_time DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def get_activity_by_id(activity_id: int) -> Optional[Dict]:
    """
    Mendapatkan detail aktivitas berdasarkan ID.
    
    Args:
        activity_id: ID aktivitas yang dicari
    
    Returns:
        Optional[Dict]: Dictionary aktivitas jika ditemukan, None jika tidak ada
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, p.name as project_name, p.category as project_category
            FROM activities a
            JOIN projects p ON a.project_id = p.id
            WHERE a.id = ?
        """, (activity_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def end_activity(activity_id: int, end_time: datetime) -> bool:
    """
    Menyelesaikan aktivitas yang sedang berjalan.
    
    Fungsi ini:
    1. Memvalidasi aktivitas masih ongoing
    2. Memvalidasi end_time > start_time
    3. Menghitung durasi dan menyimpannya
    
    Args:
        activity_id: ID aktivitas yang akan diselesaikan
        end_time: Waktu selesai
    
    Returns:
        bool: True jika berhasil, False jika aktivitas tidak ditemukan
    
    Raises:
        ValueError: Jika aktivitas sudah selesai atau waktu tidak valid
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Ambil data aktivitas untuk validasi
        cursor.execute(
            "SELECT start_time, end_time FROM activities WHERE id = ?", 
            (activity_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            raise ValueError(ERROR_MESSAGES["activity_not_found"])
        
        # Cek apakah sudah selesai (race condition prevention)
        if row['end_time'] is not None:
            raise ValueError(ERROR_MESSAGES["activity_already_ended"])
        
        # Validasi waktu
        start_time = datetime.fromisoformat(row['start_time'])
        if end_time <= start_time:
            raise ValueError(ERROR_MESSAGES["end_time_before_start"])
        
        # Hitung durasi
        duration = (end_time - start_time).total_seconds() / 3600
        
        # Update aktivitas
        cursor.execute("""
            UPDATE activities 
            SET end_time = ?, duration_hours = ?
            WHERE id = ? AND end_time IS NULL
        """, (end_time, duration, activity_id))
        
        return cursor.rowcount > 0


def update_activity(activity_id: int, project_id: int, start_time: datetime,
                    end_time: Optional[datetime], notes: str) -> bool:
    """
    Memperbarui data aktivitas.
    
    Args:
        activity_id: ID aktivitas yang akan diupdate
        project_id: ID proyek baru
        start_time: Waktu mulai baru
        end_time: Waktu selesai baru (bisa None untuk ongoing)
        notes: Catatan baru
    
    Returns:
        bool: True jika berhasil, False jika aktivitas tidak ditemukan
    
    Raises:
        ValueError: Jika end_time <= start_time
    """
    duration = None
    
    if end_time is not None:
        if end_time <= start_time:
            raise ValueError(ERROR_MESSAGES["end_time_before_start"])
        duration = (end_time - start_time).total_seconds() / 3600
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE activities 
            SET project_id = ?, start_time = ?, end_time = ?, 
                duration_hours = ?, notes = ?
            WHERE id = ?
        """, (project_id, start_time, end_time, duration, notes, activity_id))
        return cursor.rowcount > 0


def delete_activity(activity_id: int) -> bool:
    """
    Menghapus aktivitas.
    
    Args:
        activity_id: ID aktivitas yang akan dihapus
    
    Returns:
        bool: True jika berhasil, False jika aktivitas tidak ditemukan
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
        return cursor.rowcount > 0


# ==================== STATISTICS OPERATIONS ====================

def get_daily_hours(days: int = 30) -> List[Dict]:
    """
    Mendapatkan total jam kerja per hari untuk n hari terakhir.
    
    Fungsi ini berguna untuk membuat grafik tren waktu kerja harian.
    
    Args:
        days: Jumlah hari ke belakang (default: 30)
    
    Returns:
        List[Dict]: List dengan field:
            - date: Tanggal (format YYYY-MM-DD)
            - total_hours: Total jam pada tanggal tersebut
            - activity_count: Jumlah aktivitas pada tanggal tersebut
    
    Note:
        Hanya aktivitas dengan durasi (bukan ongoing) yang dihitung.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DATE(start_time) as date, 
                   SUM(duration_hours) as total_hours,
                   COUNT(*) as activity_count
            FROM activities
            WHERE duration_hours IS NOT NULL
              AND start_time >= DATE('now', ?)
            GROUP BY DATE(start_time)
            ORDER BY date
        """, (f'-{days} days',))
        return [dict(row) for row in cursor.fetchall()]


def get_category_distribution() -> List[Dict]:
    """
    Mendapatkan distribusi waktu kerja per kategori proyek.
    
    Fungsi ini berguna untuk membuat pie chart atau bar chart
    perbandingan waktu antar kategori.
    
    Returns:
        List[Dict]: List dengan field:
            - category: Nama kategori
            - total_hours: Total jam untuk kategori tersebut
            - activity_count: Jumlah aktivitas untuk kategori tersebut
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.category, 
                   SUM(a.duration_hours) as total_hours,
                   COUNT(a.id) as activity_count
            FROM activities a
            JOIN projects p ON a.project_id = p.id
            WHERE a.duration_hours IS NOT NULL
            GROUP BY p.category
            ORDER BY total_hours DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def get_project_statistics() -> List[Dict]:
    """
    Mendapatkan statistik detail untuk setiap proyek.
    
    Returns:
        List[Dict]: List dengan field:
            - id, name, category, estimated_hours, status
            - total_logged_hours: Total jam tercatat
            - activity_count: Jumlah aktivitas
            - avg_duration: Rata-rata durasi per aktivitas
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.name, p.category, p.estimated_hours, p.status,
                   COALESCE(SUM(a.duration_hours), 0) as total_logged_hours,
                   COUNT(a.id) as activity_count,
                   COALESCE(AVG(a.duration_hours), 0) as avg_duration
            FROM projects p
            LEFT JOIN activities a ON p.id = a.project_id
            GROUP BY p.id
            ORDER BY total_logged_hours DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def get_overall_statistics() -> Dict:
    """
    Mendapatkan statistik keseluruhan aplikasi.
    
    Returns:
        Dict: Dictionary dengan field:
            - total_projects: Total jumlah proyek
            - active_projects: Jumlah proyek aktif
            - total_activities: Total jumlah aktivitas
            - total_hours: Total jam kerja
            - avg_duration: Rata-rata durasi per aktivitas
            - ongoing_activities: Jumlah aktivitas yang sedang berjalan
            - active_days: Jumlah hari dengan aktivitas
            - avg_hours_per_day: Rata-rata jam kerja per hari aktif
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Total projects
        cursor.execute("SELECT COUNT(*) as count FROM projects")
        total_projects = cursor.fetchone()['count']
        
        # Active projects
        cursor.execute("SELECT COUNT(*) as count FROM projects WHERE status = 'active'")
        active_projects = cursor.fetchone()['count']
        
        # Total activities
        cursor.execute("SELECT COUNT(*) as count FROM activities")
        total_activities = cursor.fetchone()['count']
        
        # Total hours
        cursor.execute("SELECT COALESCE(SUM(duration_hours), 0) as total FROM activities")
        total_hours = cursor.fetchone()['total']
        
        # Average duration
        cursor.execute(
            "SELECT COALESCE(AVG(duration_hours), 0) as avg FROM activities "
            "WHERE duration_hours IS NOT NULL"
        )
        avg_duration = cursor.fetchone()['avg']
        
        # Ongoing activities
        cursor.execute("SELECT COUNT(*) as count FROM activities WHERE end_time IS NULL")
        ongoing = cursor.fetchone()['count']
        
        # Days with activity
        cursor.execute("SELECT COUNT(DISTINCT DATE(start_time)) as days FROM activities")
        active_days = cursor.fetchone()['days']
        
        # Calculate average hours per day
        avg_hours_per_day = total_hours / active_days if active_days > 0 else 0
        
        return {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'total_activities': total_activities,
            'total_hours': total_hours,
            'avg_duration': avg_duration,
            'ongoing_activities': ongoing,
            'active_days': active_days,
            'avg_hours_per_day': avg_hours_per_day
        }


def get_duration_array() -> List[float]:
    """
    Mendapatkan array durasi aktivitas untuk analisis statistik.
    
    Fungsi ini mengembalikan list semua durasi aktivitas yang sudah
    selesai, berguna untuk perhitungan statistik dengan NumPy/SciPy.
    
    Returns:
        List[float]: List nilai durasi dalam jam, diurutkan ascending
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT duration_hours FROM activities 
            WHERE duration_hours IS NOT NULL AND duration_hours > 0
            ORDER BY duration_hours
        """)
        return [row['duration_hours'] for row in cursor.fetchall()]


# ==================== SETTINGS OPERATIONS ====================

def get_setting(key: str) -> Optional[str]:
    """
    Mendapatkan nilai pengaturan berdasarkan key.
    
    Args:
        key: Nama pengaturan
    
    Returns:
        Optional[str]: Nilai pengaturan, atau None jika tidak ada
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row['value'] if row else None


def set_setting(key: str, value: str) -> bool:
    """
    Menyimpan atau memperbarui nilai pengaturan.
    
    Args:
        key: Nama pengaturan
        value: Nilai yang akan disimpan
    
    Returns:
        bool: True jika berhasil
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        """, (key, value))
        return cursor.rowcount > 0


def get_all_settings() -> Dict[str, str]:
    """
    Mendapatkan semua pengaturan.
    
    Returns:
        Dict[str, str]: Dictionary key-value semua pengaturan
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        return {row['key']: row['value'] for row in cursor.fetchall()}


# ==================== DATABASE INITIALIZATION ====================
# Initialize database when module is imported
init_database()
