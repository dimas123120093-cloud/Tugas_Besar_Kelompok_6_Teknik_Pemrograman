"""
================================================================================
CONSTANTS MODULE - Konstanta Aplikasi Logbook
================================================================================
Modul ini menyimpan semua konstanta yang digunakan dalam aplikasi.
Memudahkan maintenance dan menghindari magic numbers.
================================================================================
Mata Kuliah: Teknik Pemrograman
Program Studi: Teknik Geofisika - Semester 5
================================================================================
"""

# ==================== KONFIGURASI DATABASE ====================
DATABASE_FILE = "logbook.db"
"""Nama file database SQLite."""

# ==================== KATEGORI PROYEK GEOFISIKA ====================
CATEGORIES = [
    "Pengolahan Data Seismik",
    "Interpretasi Data Gravity",
    "Pemodelan Resistivitas",
    "Analisis Well Log",
    "Pengukuran Lapangan",
    "Penulisan Laporan",
    "Meeting/Diskusi",
    "Lainnya"
]
"""
Daftar kategori proyek yang relevan dengan Teknik Geofisika.
Kategori ini mencakup berbagai kegiatan yang umum dilakukan
oleh mahasiswa dan profesional geofisika.
"""

# ==================== STATUS PROYEK ====================
STATUS_OPTIONS = ["active", "completed", "paused"]
"""Opsi status proyek dalam database."""

STATUS_LABELS = {
    "active": "🟢 Aktif",
    "completed": "🔵 Selesai",
    "paused": "🟡 Ditunda"
}
"""Label tampilan untuk setiap status proyek dengan emoji indikator."""

STATUS_COLORS = {
    "active": "#28a745",      # Hijau
    "completed": "#007bff",   # Biru
    "paused": "#ffc107"       # Kuning
}
"""Kode warna hex untuk setiap status proyek."""

# ==================== KONFIGURASI EFISIENSI ====================
EFFICIENCY_THRESHOLDS = {
    "critical": 50,    # Di bawah 50% = kritis (merah)
    "warning": 80,     # 50-80% = perlu perhatian (kuning)
    "good": 100,       # 80-100% = baik (hijau)
    "excellent": 100   # Di atas 100% = melebihi target (biru)
}
"""
Batas nilai efisiensi untuk kategorisasi:
- critical: Efisiensi sangat rendah, perlu evaluasi
- warning: Efisiensi cukup, masih perlu peningkatan
- good: Efisiensi baik, sesuai target
- excellent: Melebihi estimasi waktu
"""

EFFICIENCY_COLORS = {
    "critical": "#dc3545",    # Merah - efisiensi < 50%
    "warning": "#ffc107",     # Kuning - efisiensi 50-80%
    "good": "#28a745",        # Hijau - efisiensi 80-100%
    "excellent": "#17a2b8"    # Biru - efisiensi > 100%
}
"""Kode warna hex untuk setiap level efisiensi."""

EFFICIENCY_LABELS = {
    "critical": "🔴 Kritis",
    "warning": "🟡 Perlu Perhatian",
    "good": "🟢 Baik",
    "excellent": "🔵 Melebihi Target"
}
"""Label tampilan untuk setiap level efisiensi."""

# ==================== KONFIGURASI GRAFIK ====================
CHART_CONFIG = {
    "height_small": 250,
    "height_medium": 300,
    "height_large": 400,
    "margin": {"l": 0, "r": 0, "t": 10, "b": 0},
    "margin_with_labels": {"l": 0, "r": 50, "t": 10, "b": 0}
}
"""Konfigurasi ukuran dan margin untuk grafik Plotly."""

CHART_COLORS = {
    "primary": "rgb(99, 110, 250)",       # Warna utama grafik
    "primary_fill": "rgba(99, 110, 250, 0.4)",  # Warna fill area chart
    "secondary": "rgb(239, 85, 59)",      # Warna sekunder
    "success": "rgb(40, 167, 69)",        # Hijau untuk sukses
    "warning": "rgb(255, 193, 7)",        # Kuning untuk warning
    "danger": "rgb(220, 53, 69)",         # Merah untuk bahaya
    "info": "rgb(23, 162, 184)"           # Biru untuk info
}
"""Palet warna untuk visualisasi grafik."""

# ==================== KONFIGURASI VALIDASI ====================
VALIDATION_RULES = {
    "project_name_min_length": 3,
    "project_name_max_length": 100,
    "description_max_length": 500,
    "estimated_hours_min": 0.5,
    "estimated_hours_max": 1000,
    "notes_max_length": 500
}
"""
Aturan validasi input:
- project_name: Panjang nama proyek (3-100 karakter)
- description: Maksimal 500 karakter
- estimated_hours: Estimasi jam kerja (0.5-1000 jam)
- notes: Catatan aktivitas maksimal 500 karakter
"""

# ==================== KONFIGURASI TAMPILAN ====================
DISPLAY_CONFIG = {
    "items_per_page": 10,
    "date_format": "%d/%m/%Y",
    "datetime_format": "%d/%m/%Y %H:%M",
    "time_format": "%H:%M",
    "default_days_filter": 30
}
"""Konfigurasi format tampilan tanggal dan pagination."""

# ==================== KONFIGURASI DEFAULT ====================
DEFAULT_SETTINGS = {
    "target_hours_per_day": 8.0,
    "efficiency_threshold": 0.7,
    "default_work_start_hour": 9,
    "default_work_end_hour": 17
}
"""Nilai default untuk pengaturan aplikasi."""

# ==================== PESAN ERROR ====================
ERROR_MESSAGES = {
    "project_name_required": "Nama proyek wajib diisi!",
    "project_name_too_short": f"Nama proyek minimal {VALIDATION_RULES['project_name_min_length']} karakter!",
    "project_name_too_long": f"Nama proyek maksimal {VALIDATION_RULES['project_name_max_length']} karakter!",
    "estimated_hours_invalid": f"Estimasi jam harus antara {VALIDATION_RULES['estimated_hours_min']} - {VALIDATION_RULES['estimated_hours_max']} jam!",
    "end_time_before_start": "Waktu selesai harus setelah waktu mulai!",
    "activity_already_ended": "Aktivitas sudah selesai sebelumnya!",
    "activity_not_found": "Aktivitas tidak ditemukan!",
    "project_not_found": "Proyek tidak ditemukan!",
    "database_error": "Terjadi kesalahan pada database. Silakan coba lagi.",
    "invalid_duration": "Durasi tidak valid!"
}
"""Pesan error standar untuk validasi dan exception handling."""

# ==================== PESAN SUKSES ====================
SUCCESS_MESSAGES = {
    "project_created": "✅ Proyek berhasil ditambahkan!",
    "project_updated": "✅ Proyek berhasil diperbarui!",
    "project_deleted": "✅ Proyek berhasil dihapus!",
    "activity_started": "✅ Aktivitas dimulai!",
    "activity_ended": "✅ Aktivitas selesai!",
    "activity_updated": "✅ Aktivitas berhasil diperbarui!",
    "activity_deleted": "✅ Aktivitas berhasil dihapus!",
    "settings_saved": "✅ Pengaturan tersimpan!",
    "database_reset": "✅ Database berhasil direset!"
}
"""Pesan sukses standar untuk feedback ke user."""
