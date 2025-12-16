"""
================================================================================
CALCULATIONS MODULE - Fungsi Perhitungan dan Analisis
================================================================================
Modul ini berisi fungsi-fungsi untuk melakukan perhitungan statistik
dan analisis data yang digunakan dalam aplikasi Logbook.
================================================================================
Mata Kuliah: Teknik Pemrograman
Program Studi: Teknik Geofisika - Semester 5
================================================================================
"""

import math
from typing import Optional, List, Tuple
import numpy as np
from scipy import stats

from constants import (
    EFFICIENCY_THRESHOLDS, 
    EFFICIENCY_COLORS, 
    EFFICIENCY_LABELS
)


def calculate_efficiency(logged_hours: Optional[float], 
                         estimated_hours: Optional[float]) -> float:
    """
    Menghitung persentase efisiensi proyek.
    
    Efisiensi dihitung sebagai rasio antara jam yang tercatat (logged)
    dengan jam yang diestimasi, dikalikan 100 untuk mendapatkan persentase.
    
    Formula: efficiency = (logged_hours / estimated_hours) * 100
    
    Args:
        logged_hours: Total jam yang sudah dicatat/dikerjakan.
                     Bisa None atau NaN.
        estimated_hours: Estimasi total jam yang dibutuhkan.
                        Bisa None, NaN, atau 0.
    
    Returns:
        float: Persentase efisiensi (0-100+).
               Mengembalikan 0 jika input tidak valid.
    
    Examples:
        >>> calculate_efficiency(8, 10)
        80.0
        >>> calculate_efficiency(12, 10)
        120.0
        >>> calculate_efficiency(None, 10)
        0.0
        >>> calculate_efficiency(5, 0)
        0.0
    
    Note:
        - Efisiensi > 100% berarti waktu yang digunakan melebihi estimasi
        - Efisiensi = 100% berarti tepat sesuai estimasi
        - Efisiensi < 100% berarti masih ada sisa waktu dari estimasi
    """
    # Validasi logged_hours
    if logged_hours is None:
        return 0.0
    if isinstance(logged_hours, float) and math.isnan(logged_hours):
        return 0.0
    if logged_hours < 0:
        return 0.0
    
    # Validasi estimated_hours
    if estimated_hours is None:
        return 0.0
    if isinstance(estimated_hours, float) and math.isnan(estimated_hours):
        return 0.0
    if estimated_hours <= 0:
        return 0.0
    
    # Hitung efisiensi
    return (logged_hours / estimated_hours) * 100


def get_efficiency_level(efficiency: float) -> str:
    """
    Menentukan level efisiensi berdasarkan persentase.
    
    Level efisiensi dikategorikan menjadi:
    - critical: efisiensi < 50%
    - warning: efisiensi 50-80%
    - good: efisiensi 80-100%
    - excellent: efisiensi > 100%
    
    Args:
        efficiency: Nilai persentase efisiensi
    
    Returns:
        str: Level efisiensi ("critical", "warning", "good", atau "excellent")
    
    Examples:
        >>> get_efficiency_level(30)
        "critical"
        >>> get_efficiency_level(65)
        "warning"
        >>> get_efficiency_level(90)
        "good"
        >>> get_efficiency_level(120)
        "excellent"
    """
    if efficiency < EFFICIENCY_THRESHOLDS["critical"]:
        return "critical"
    elif efficiency < EFFICIENCY_THRESHOLDS["warning"]:
        return "warning"
    elif efficiency <= EFFICIENCY_THRESHOLDS["good"]:
        return "good"
    else:
        return "excellent"


def get_efficiency_color(efficiency: float) -> str:
    """
    Mendapatkan kode warna hex berdasarkan persentase efisiensi.
    
    Warna digunakan untuk visualisasi yang intuitif:
    - Merah: efisiensi rendah, perlu perhatian
    - Kuning: efisiensi cukup, bisa ditingkatkan
    - Hijau: efisiensi baik, sesuai target
    - Biru: efisiensi tinggi, melebihi target
    
    Args:
        efficiency: Nilai persentase efisiensi
    
    Returns:
        str: Kode warna hex (contoh: "#28a745")
    
    Examples:
        >>> get_efficiency_color(30)
        "#dc3545"  # Merah
        >>> get_efficiency_color(90)
        "#28a745"  # Hijau
    """
    level = get_efficiency_level(efficiency)
    return EFFICIENCY_COLORS[level]


def get_efficiency_label(efficiency: float) -> str:
    """
    Mendapatkan label tampilan berdasarkan persentase efisiensi.
    
    Label berisi emoji dan teks deskriptif untuk feedback visual
    yang mudah dipahami pengguna.
    
    Args:
        efficiency: Nilai persentase efisiensi
    
    Returns:
        str: Label dengan emoji (contoh: "🟢 Baik")
    
    Examples:
        >>> get_efficiency_label(30)
        "🔴 Kritis"
        >>> get_efficiency_label(90)
        "🟢 Baik"
    """
    level = get_efficiency_level(efficiency)
    return EFFICIENCY_LABELS[level]


def calculate_duration(start_time, end_time) -> float:
    """
    Menghitung durasi antara dua waktu dalam jam.
    
    Args:
        start_time: Waktu mulai (datetime)
        end_time: Waktu selesai (datetime)
    
    Returns:
        float: Durasi dalam jam
    
    Raises:
        ValueError: Jika end_time <= start_time (durasi negatif atau nol)
    
    Examples:
        >>> from datetime import datetime
        >>> start = datetime(2024, 12, 15, 9, 0)
        >>> end = datetime(2024, 12, 15, 12, 30)
        >>> calculate_duration(start, end)
        3.5
    """
    if end_time <= start_time:
        raise ValueError("Waktu selesai harus setelah waktu mulai!")
    
    duration_seconds = (end_time - start_time).total_seconds()
    duration_hours = duration_seconds / 3600
    
    return duration_hours


def calculate_progress(logged_hours: float, estimated_hours: float) -> float:
    """
    Menghitung progress proyek sebagai nilai antara 0 dan 1.
    
    Nilai progress dibatasi maksimal 1.0 untuk keperluan tampilan
    progress bar yang tidak melebihi 100%.
    
    Args:
        logged_hours: Jam yang sudah dikerjakan
        estimated_hours: Estimasi total jam
    
    Returns:
        float: Nilai progress antara 0.0 dan 1.0
    
    Examples:
        >>> calculate_progress(5, 10)
        0.5
        >>> calculate_progress(12, 10)
        1.0  # Dibatasi maksimal 1.0
    """
    if estimated_hours <= 0:
        return 0.0
    
    if logged_hours < 0:
        return 0.0
    
    progress = logged_hours / estimated_hours
    
    # Batasi antara 0 dan 1
    return min(max(progress, 0.0), 1.0)


def calculate_statistics(data: List[float]) -> dict:
    """
    Menghitung statistik deskriptif dari array data.
    
    Fungsi ini menggunakan NumPy dan SciPy untuk menghitung
    berbagai ukuran statistik yang relevan untuk analisis data.
    
    Args:
        data: List atau array nilai numerik
    
    Returns:
        dict: Dictionary berisi statistik deskriptif:
            - count: Jumlah data
            - mean: Rata-rata
            - median: Nilai tengah
            - std: Standar deviasi
            - min: Nilai minimum
            - max: Nilai maksimum
            - range: Rentang (max - min)
            - q1: Kuartil pertama (25%)
            - q3: Kuartil ketiga (75%)
            - iqr: Interquartile range (Q3 - Q1)
            - skewness: Kemiringan distribusi
            - kurtosis: Keruncingan distribusi
    
    Examples:
        >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> stats = calculate_statistics(data)
        >>> stats['mean']
        5.5
        >>> stats['median']
        5.5
    
    Note:
        Skewness dan kurtosis membutuhkan minimal 3 data point.
        Jika data kurang dari 3, nilai akan diset ke 0.
    """
    if not data or len(data) == 0:
        return {
            'count': 0,
            'mean': 0,
            'median': 0,
            'std': 0,
            'min': 0,
            'max': 0,
            'range': 0,
            'q1': 0,
            'q3': 0,
            'iqr': 0,
            'skewness': 0,
            'kurtosis': 0
        }
    
    arr = np.array(data)
    
    # Hitung kuartil
    q1 = np.percentile(arr, 25)
    q3 = np.percentile(arr, 75)
    
    # Hitung skewness dan kurtosis (butuh minimal 3 data)
    if len(arr) >= 3:
        skewness = stats.skew(arr)
        kurtosis = stats.kurtosis(arr)
    else:
        skewness = 0
        kurtosis = 0
    
    return {
        'count': len(arr),
        'mean': np.mean(arr),
        'median': np.median(arr),
        'std': np.std(arr),
        'min': np.min(arr),
        'max': np.max(arr),
        'range': np.ptp(arr),  # peak-to-peak (max - min)
        'q1': q1,
        'q3': q3,
        'iqr': q3 - q1,
        'skewness': skewness,
        'kurtosis': kurtosis
    }


def calculate_trend(dates: List, values: List[float]) -> Tuple[float, float]:
    """
    Menghitung tren linear dari data time series.
    
    Menggunakan regresi linear sederhana untuk menentukan
    slope (kemiringan) dan intercept dari data.
    
    Args:
        dates: List tanggal atau indeks waktu
        values: List nilai yang akan dianalisis
    
    Returns:
        Tuple[float, float]: (slope, intercept)
            - slope positif = tren naik
            - slope negatif = tren turun
            - slope ~0 = stabil
    
    Examples:
        >>> dates = [1, 2, 3, 4, 5]
        >>> values = [10, 12, 15, 18, 20]
        >>> slope, intercept = calculate_trend(dates, values)
        >>> slope > 0
        True  # Tren naik
    """
    if len(dates) < 2 or len(values) < 2:
        return 0.0, 0.0
    
    # Konversi ke array numerik
    x = np.arange(len(values))
    y = np.array(values)
    
    # Regresi linear
    slope, intercept, _, _, _ = stats.linregress(x, y)
    
    return slope, intercept


def calculate_average_per_day(total_hours: float, active_days: int) -> float:
    """
    Menghitung rata-rata jam kerja per hari.
    
    Args:
        total_hours: Total jam yang dikerjakan
        active_days: Jumlah hari aktif bekerja
    
    Returns:
        float: Rata-rata jam per hari, atau 0 jika tidak ada hari aktif
    
    Examples:
        >>> calculate_average_per_day(40, 5)
        8.0
        >>> calculate_average_per_day(10, 0)
        0.0
    """
    if active_days <= 0:
        return 0.0
    
    return total_hours / active_days
