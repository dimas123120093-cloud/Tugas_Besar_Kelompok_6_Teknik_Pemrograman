def get_all_activities() -> List[Dict]:
    """Mendapatkan semua aktivitas dengan info proyek."""
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
    """Mendapatkan aktivitas berdasarkan proyek."""
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
    """Mendapatkan aktivitas yang sedang berjalan (belum selesai)."""
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


def end_activity(activity_id: int, end_time: datetime) -> bool:
    """Menyelesaikan aktivitas yang sedang berjalan."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Ambil start_time untuk hitung durasi
        cursor.execute("SELECT start_time FROM activities WHERE id = ?", (activity_id,))
        row = cursor.fetchone()
        if not row:
            return False
        
        start_time = datetime.fromisoformat(row['start_time'])
        duration = (end_time - start_time).total_seconds() / 3600
        
        cursor.execute("""
            UPDATE activities 
            SET end_time = ?, duration_hours = ?
            WHERE id = ?
        """, (end_time, duration, activity_id))
        return cursor.rowcount > 0


def update_activity(activity_id: int, project_id: int, start_time: datetime,
                    end_time: Optional[datetime], notes: str) -> bool:
    """Update data aktivitas."""
    duration = None
    if end_time:
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
    """Hapus aktivitas."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
        return cursor.rowcount > 0


# ==================== STATISTICS OPERATIONS ====================

def get_daily_hours(days: int = 30) -> List[Dict]:
    """Mendapatkan total jam per hari untuk n hari terakhir."""
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
    """Mendapatkan distribusi waktu per kategori."""
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
    """Mendapatkan statistik per proyek."""
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
    """Mendapatkan statistik keseluruhan."""
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
        cursor.execute("SELECT COALESCE(AVG(duration_hours), 0) as avg FROM activities WHERE duration_hours IS NOT NULL")
        avg_duration = cursor.fetchone()['avg']
        
        # Ongoing activities
        cursor.execute("SELECT COUNT(*) as count FROM activities WHERE end_time IS NULL")
        ongoing = cursor.fetchone()['count']
        
        # Days with activity
        cursor.execute("SELECT COUNT(DISTINCT DATE(start_time)) as days FROM activities")
        active_days = cursor.fetchone()['days']
        
        return {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'total_activities': total_activities,
            'total_hours': total_hours,
            'avg_duration': avg_duration,
            'ongoing_activities': ongoing,
            'active_days': active_days,
            'avg_hours_per_day': total_hours / active_days if active_days > 0 else 0
        }


def get_duration_array() -> List[float]:
    """Mendapatkan array durasi untuk analisis statistik."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT duration_hours FROM activities 
            WHERE duration_hours IS NOT NULL
            ORDER BY duration_hours
        """)
        return [row['duration_hours'] for row in cursor.fetchall()]


# ==================== SETTINGS OPERATIONS ====================

def get_setting(key: str) -> Optional[str]:
    """Mendapatkan nilai setting."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row['value'] if row else None


def set_setting(key: str, value: str) -> bool:
    """Menyimpan nilai setting."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        """, (key, value))
        return cursor.rowcount > 0


def get_all_settings() -> Dict[str, str]:
    """Mendapatkan semua settings."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        return {row['key']: row['value'] for row in cursor.fetchall()}


# Initialize database when module is imported
init_database()
