"""
================================================================================
VALIDATORS MODULE - Fungsi Validasi Input
================================================================================
Modul ini berisi fungsi-fungsi untuk memvalidasi input pengguna
sebelum data disimpan ke database.
================================================================================
Mata Kuliah: Teknik Pemrograman
Program Studi: Teknik Geofisika - Semester 5
================================================================================
"""

from datetime import datetime
from typing import Tuple, List, Optional

from constants import VALIDATION_RULES, ERROR_MESSAGES, CATEGORIES, STATUS_OPTIONS


def validate_project_name(name: str) -> Tuple[bool, str]:
    """
    Memvalidasi nama proyek.
    
    Aturan validasi:
    - Tidak boleh kosong atau hanya whitespace
    - Minimal 3 karakter
    - Maksimal 100 karakter
    
    Args:
        name: Nama proyek yang akan divalidasi
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
            - is_valid: True jika valid, False jika tidak
            - error_message: Pesan error jika tidak valid, string kosong jika valid
    
    Examples:
        >>> validate_project_name("Pengolahan Seismik")
        (True, "")
        >>> validate_project_name("")
        (False, "Nama proyek wajib diisi!")
        >>> validate_project_name("AB")
        (False, "Nama proyek minimal 3 karakter!")
    """
    # Cek kosong
    if not name or not name.strip():
        return False, ERROR_MESSAGES["project_name_required"]
    
    name = name.strip()
    
    # Cek panjang minimal
    if len(name) < VALIDATION_RULES["project_name_min_length"]:
        return False, ERROR_MESSAGES["project_name_too_short"]
    
    # Cek panjang maksimal
    if len(name) > VALIDATION_RULES["project_name_max_length"]:
        return False, ERROR_MESSAGES["project_name_too_long"]
    
    return True, ""


def validate_estimated_hours(hours: float) -> Tuple[bool, str]:
    """
    Memvalidasi estimasi jam proyek.
    
    Aturan validasi:
    - Minimal 0.5 jam (30 menit)
    - Maksimal 1000 jam
    
    Args:
        hours: Estimasi jam yang akan divalidasi
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    
    Examples:
        >>> validate_estimated_hours(10)
        (True, "")
        >>> validate_estimated_hours(0.1)
        (False, "Estimasi jam harus antara 0.5 - 1000 jam!")
    """
    min_hours = VALIDATION_RULES["estimated_hours_min"]
    max_hours = VALIDATION_RULES["estimated_hours_max"]
    
    if hours < min_hours or hours > max_hours:
        return False, ERROR_MESSAGES["estimated_hours_invalid"]
    
    return True, ""


def validate_category(category: str) -> Tuple[bool, str]:
    """
    Memvalidasi kategori proyek.
    
    Kategori harus salah satu dari daftar yang tersedia
    di constants.CATEGORIES.
    
    Args:
        category: Kategori yang akan divalidasi
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    
    Examples:
        >>> validate_category("Pengolahan Data Seismik")
        (True, "")
        >>> validate_category("Kategori Tidak Ada")
        (False, "Kategori tidak valid!")
    """
    if category not in CATEGORIES:
        return False, "Kategori tidak valid!"
    
    return True, ""


def validate_status(status: str) -> Tuple[bool, str]:
    """
    Memvalidasi status proyek.
    
    Status harus salah satu dari: "active", "completed", "paused"
    
    Args:
        status: Status yang akan divalidasi
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    
    Examples:
        >>> validate_status("active")
        (True, "")
        >>> validate_status("invalid")
        (False, "Status tidak valid!")
    """
    if status not in STATUS_OPTIONS:
        return False, "Status tidak valid!"
    
    return True, ""


def validate_time_range(start_time: datetime, 
                        end_time: Optional[datetime]) -> Tuple[bool, str]:
    """
    Memvalidasi rentang waktu aktivitas.
    
    Aturan validasi:
    - end_time harus setelah start_time
    - Durasi tidak boleh negatif
    
    Args:
        start_time: Waktu mulai aktivitas
        end_time: Waktu selesai aktivitas (opsional, bisa None untuk ongoing)
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    
    Examples:
        >>> from datetime import datetime
        >>> start = datetime(2024, 12, 15, 9, 0)
        >>> end = datetime(2024, 12, 15, 12, 0)
        >>> validate_time_range(start, end)
        (True, "")
        >>> 
        >>> end_before = datetime(2024, 12, 15, 8, 0)
        >>> validate_time_range(start, end_before)
        (False, "Waktu selesai harus setelah waktu mulai!")
    """
    # Jika end_time None (aktivitas ongoing), valid
    if end_time is None:
        return True, ""
    
    # Cek end_time > start_time
    if end_time <= start_time:
        return False, ERROR_MESSAGES["end_time_before_start"]
    
    return True, ""


def validate_notes(notes: str) -> Tuple[bool, str]:
    """
    Memvalidasi catatan aktivitas.
    
    Aturan validasi:
    - Maksimal 500 karakter
    
    Args:
        notes: Catatan yang akan divalidasi
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    
    Examples:
        >>> validate_notes("Mengerjakan QC data seismik")
        (True, "")
        >>> validate_notes("x" * 600)
        (False, "Catatan maksimal 500 karakter!")
    """
    if notes and len(notes) > VALIDATION_RULES["notes_max_length"]:
        return False, f"Catatan maksimal {VALIDATION_RULES['notes_max_length']} karakter!"
    
    return True, ""


def validate_project(name: str, estimated_hours: float, 
                     category: str) -> Tuple[bool, List[str]]:
    """
    Memvalidasi semua field proyek sekaligus.
    
    Fungsi ini menggabungkan validasi nama, estimasi jam, dan kategori
    untuk kemudahan penggunaan di form.
    
    Args:
        name: Nama proyek
        estimated_hours: Estimasi jam
        category: Kategori proyek
    
    Returns:
        Tuple[bool, List[str]]: (all_valid, list_of_errors)
            - all_valid: True jika semua field valid
            - list_of_errors: List pesan error (kosong jika valid)
    
    Examples:
        >>> validate_project("Seismik Project", 20, "Pengolahan Data Seismik")
        (True, [])
        >>> validate_project("", 0, "Invalid")
        (False, ["Nama proyek wajib diisi!", "Estimasi jam harus antara 0.5 - 1000 jam!", "Kategori tidak valid!"])
    """
    errors = []
    
    # Validasi nama
    is_valid, error = validate_project_name(name)
    if not is_valid:
        errors.append(error)
    
    # Validasi estimasi jam
    is_valid, error = validate_estimated_hours(estimated_hours)
    if not is_valid:
        errors.append(error)
    
    # Validasi kategori
    is_valid, error = validate_category(category)
    if not is_valid:
        errors.append(error)
    
    return len(errors) == 0, errors


def validate_activity(project_id: int, start_time: datetime,
                      end_time: Optional[datetime], 
                      notes: str = "") -> Tuple[bool, List[str]]:
    """
    Memvalidasi semua field aktivitas sekaligus.
    
    Args:
        project_id: ID proyek
        start_time: Waktu mulai
        end_time: Waktu selesai (opsional)
        notes: Catatan (opsional)
    
    Returns:
        Tuple[bool, List[str]]: (all_valid, list_of_errors)
    
    Examples:
        >>> from datetime import datetime
        >>> validate_activity(1, datetime.now(), None, "Testing")
        (True, [])
    """
    errors = []
    
    # Validasi project_id
    if not project_id or project_id <= 0:
        errors.append("Proyek harus dipilih!")
    
    # Validasi waktu
    is_valid, error = validate_time_range(start_time, end_time)
    if not is_valid:
        errors.append(error)
    
    # Validasi notes
    is_valid, error = validate_notes(notes)
    if not is_valid:
        errors.append(error)
    
    return len(errors) == 0, errors


def sanitize_string(text: str) -> str:
    """
    Membersihkan string dari karakter yang tidak diinginkan.
    
    Fungsi ini melakukan:
    - Strip whitespace di awal dan akhir
    - Menghapus karakter kontrol
    - Normalisasi spasi ganda
    
    Args:
        text: String yang akan dibersihkan
    
    Returns:
        str: String yang sudah dibersihkan
    
    Examples:
        >>> sanitize_string("  Hello   World  ")
        "Hello World"
    """
    if not text:
        return ""
    
    # Strip whitespace
    text = text.strip()
    
    # Normalisasi spasi ganda
    import re
    text = re.sub(r'\s+', ' ', text)
    
    return text
