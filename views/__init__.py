"""
================================================================================
PAGES PACKAGE - Halaman-halaman Aplikasi Logbook
================================================================================
Package ini berisi modul-modul untuk setiap halaman aplikasi:
- dashboard: Halaman utama dengan ringkasan dan visualisasi
- projects: Manajemen proyek (CRUD)
- activities: Pencatatan waktu kerja
- analysis: Analisis statistik
- settings: Pengaturan aplikasi
================================================================================
"""

from views import dashboard
from views import projects
from views import activities
from views import analysis
from views import settings

__all__ = [
    'dashboard',
    'projects',
    'activities',
    'analysis',
    'settings'
]
