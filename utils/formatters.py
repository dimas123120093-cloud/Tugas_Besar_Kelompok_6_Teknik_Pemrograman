"""
================================================================================
FORMATTERS MODULE - Fungsi Pemformatan Data
================================================================================
Modul ini berisi fungsi-fungsi untuk memformat data menjadi string
yang mudah dibaca oleh pengguna.
================================================================================
Mata Kuliah: Teknik Pemrograman
Program Studi: Teknik Geofisika - Semester 5
================================================================================
"""

import math
from datetime import datetime, timedelta
from typing import Optional, Union

from constants import DISPLAY_CONFIG


def format_duration(hours: Optional[float]) -> str:
    """
    Memformat durasi dalam jam menjadi string yang mudah dibaca.
    
    Fungsi ini mengkonversi nilai jam (float) menjadi format "Xj Ym"
    dimana X adalah jam dan Y adalah menit.
    
    Args:
        hours: Durasi dalam jam (float). Bisa None atau NaN.
    
    Returns:
        str: String format "Xj Ym" (contoh: "2j 30m" untuk 2.5 jam)
             Mengembalikan "0j 0m" jika input None, NaN, atau <= 0
    
    Examples:
        >>> format_duration(2.5)
        "2j 30m"
        >>> format_duration(0.25)
        "0j 15m"
        >>> format_duration(None)
        "0j 0m"
        >>> format_duration(-1)
        "0j 0m"
    
    Note:
        Nilai negatif dianggap tidak valid dan akan mengembalikan "0j 0m"
    """
    # Handle None
    if hours is None:
        return "0j 0m"
    
    # Handle NaN
    if isinstance(hours, float) and math.isnan(hours):
        return "0j 0m"
    
    # Handle nilai negatif atau nol
    if hours <= 0:
        return "0j 0m"
    
    # Konversi ke menit total
    total_minutes = int(hours * 60)
    
    # Hitung jam dan menit
    jam = total_minutes // 60
    menit = total_minutes % 60
    
    return f"{jam}j {menit}m"


def format_duration_long(hours: Optional[float]) -> str:
    """
    Memformat durasi dalam jam menjadi string lengkap.
    
    Mirip dengan format_duration() tetapi menggunakan kata lengkap
    "jam" dan "menit" untuk tampilan yang lebih formal.
    
    Args:
        hours: Durasi dalam jam (float). Bisa None atau NaN.
    
    Returns:
        str: String format "X jam Y menit" (contoh: "2 jam 30 menit")
    
    Examples:
        >>> format_duration_long(2.5)
        "2 jam 30 menit"
        >>> format_duration_long(1.0)
        "1 jam 0 menit"
    """
    if hours is None:
        return "0 jam 0 menit"
    
    if isinstance(hours, float) and math.isnan(hours):
        return "0 jam 0 menit"
    
    if hours <= 0:
        return "0 jam 0 menit"
    
    total_minutes = int(hours * 60)
    jam = total_minutes // 60
    menit = total_minutes % 60
    
    return f"{jam} jam {menit} menit"


def format_date(dt: Optional[Union[datetime, str]], 
                format_type: str = "date") -> str:
    """
    Memformat datetime menjadi string tanggal/waktu yang mudah dibaca.
    
    Args:
        dt: Objek datetime atau string ISO format. Bisa None.
        format_type: Tipe format yang diinginkan:
            - "date": Hanya tanggal (dd/mm/yyyy)
            - "datetime": Tanggal dan waktu (dd/mm/yyyy HH:MM)
            - "time": Hanya waktu (HH:MM)
    
    Returns:
        str: String tanggal/waktu terformat, atau "-" jika None
    
    Examples:
        >>> format_date(datetime(2024, 12, 15, 10, 30), "date")
        "15/12/2024"
        >>> format_date(datetime(2024, 12, 15, 10, 30), "datetime")
        "15/12/2024 10:30"
        >>> format_date(None)
        "-"
    """
    if dt is None:
        return "-"
    
    # Konversi string ke datetime jika perlu
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return "-"
    
    # Pilih format berdasarkan tipe
    if format_type == "date":
        return dt.strftime(DISPLAY_CONFIG["date_format"])
    elif format_type == "datetime":
        return dt.strftime(DISPLAY_CONFIG["datetime_format"])
    elif format_type == "time":
        return dt.strftime(DISPLAY_CONFIG["time_format"])
    else:
        return dt.strftime(DISPLAY_CONFIG["datetime_format"])


def format_percentage(value: Optional[float], decimals: int = 1) -> str:
    """
    Memformat nilai float menjadi string persentase.
    
    Args:
        value: Nilai persentase (float). Bisa None.
        decimals: Jumlah angka desimal (default: 1)
    
    Returns:
        str: String format "X.X%" atau "0%" jika None
    
    Examples:
        >>> format_percentage(85.567)
        "85.6%"
        >>> format_percentage(100)
        "100.0%"
        >>> format_percentage(None)
        "0%"
    """
    if value is None:
        return "0%"
    
    if isinstance(value, float) and math.isnan(value):
        return "0%"
    
    return f"{value:.{decimals}f}%"


def format_number(value: Optional[float], decimals: int = 2) -> str:
    """
    Memformat angka dengan jumlah desimal tertentu.
    
    Args:
        value: Nilai numerik (float). Bisa None.
        decimals: Jumlah angka desimal (default: 2)
    
    Returns:
        str: String angka terformat atau "0" jika None
    
    Examples:
        >>> format_number(3.14159, 2)
        "3.14"
        >>> format_number(100.0, 0)
        "100"
    """
    if value is None:
        return "0"
    
    if isinstance(value, float) and math.isnan(value):
        return "0"
    
    if decimals == 0:
        return str(int(value))
    
    return f"{value:.{decimals}f}"


def format_elapsed_time(start_time: datetime) -> str:
    """
    Menghitung dan memformat waktu yang telah berlalu dari start_time.
    
    Fungsi ini berguna untuk menampilkan durasi aktivitas yang sedang
    berjalan (ongoing).
    
    Args:
        start_time: Waktu mulai aktivitas
    
    Returns:
        str: String format "Xj Ym" menunjukkan waktu yang telah berlalu
    
    Examples:
        >>> # Jika sekarang 10:30 dan start_time adalah 08:00
        >>> format_elapsed_time(datetime(2024, 12, 15, 8, 0))
        "2j 30m"
    """
    elapsed_seconds = (datetime.now() - start_time).total_seconds()
    elapsed_hours = elapsed_seconds / 3600
    
    return format_duration(elapsed_hours)


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Memotong teks jika melebihi panjang maksimum.
    
    Args:
        text: Teks yang akan dipotong
        max_length: Panjang maksimum (default: 50)
        suffix: String yang ditambahkan jika teks dipotong (default: "...")
    
    Returns:
        str: Teks asli atau teks terpotong dengan suffix
    
    Examples:
        >>> truncate_text("Pengolahan Data Seismik Laut Jawa Utara", 20)
        "Pengolahan Data S..."
        >>> truncate_text("Short text", 50)
        "Short text"
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
