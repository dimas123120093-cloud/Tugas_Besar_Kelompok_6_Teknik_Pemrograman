"""
================================================================================
APLIKASI LOGBOOK PENCATAT WAKTU PROYEK & ANALISIS EFISIENSI
================================================================================
Aplikasi ini membantu mahasiswa Teknik Geofisika untuk:
- Mencatat waktu kerja pada berbagai proyek
- Melacak progress dan efisiensi proyek
- Menganalisis pola kerja dengan statistik deskriptif
- Memvisualisasikan data dengan grafik interaktif

Teknologi yang digunakan:
- Streamlit: Framework web UI
- SQLite: Database lokal
- Pandas & NumPy: Pengolahan data
- SciPy: Analisis statistik
- Plotly: Visualisasi interaktif
================================================================================
Mata Kuliah: Teknik Pemrograman
Program Studi: Teknik Geofisika - Semester 5
================================================================================
"""

import streamlit as st

# Import database module untuk statistik sidebar
import database as db

# Import halaman-halaman aplikasi
from views import dashboard, projects, activities, analysis, settings

# Import utility functions
from utils import format_duration

# Import konstanta
from constants import ERROR_MESSAGES


# ==================== KONFIGURASI HALAMAN ====================
st.set_page_config(
    page_title="Logbook Proyek - Teknik Geofisika",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================== FUNGSI UTAMA ====================

def main():
    """
    Fungsi utama aplikasi.
    
    Menangani:
    1. Navigasi sidebar
    2. Routing ke halaman yang dipilih
    3. Menampilkan statistik ringkas di sidebar
    """
    # Render sidebar
    selected_page = _render_sidebar()
    
    # Routing ke halaman yang dipilih
    _route_to_page(selected_page)

def _render_sidebar() -> str:
    """
    Merender sidebar navigasi.
    
    Returns:
        str: Nama halaman yang dipilih
    """
    with st.sidebar:
        # Header
        st.title("📋 Logbook")
        st.caption("Teknik Geofisika - Semester 5")
        
        st.divider()
        
        # Menu navigasi
        page = st.radio(
            "Menu Navigasi",
            options=[
                "Dashboard",
                "Proyek",
                "Aktivitas",
                "Analisis",
                "Pengaturan"
            ],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Quick stats
        _render_sidebar_stats()
        
        st.divider()
        
        # Info aplikasi
        _render_app_info()
    
    return page


def _render_sidebar_stats():
    """
    Merender statistik ringkas di sidebar.
    """
    try:
        stats = db.get_overall_statistics()
        
        st.caption("📊 **Ringkasan**")
        st.caption(f"📁 {stats['total_projects']} Proyek")
        st.caption(f"⏱️ {format_duration(stats['total_hours'])} Total Jam")
        st.caption(f"📅 {stats['active_days']} Hari Aktif")
        
        # Tampilkan aktivitas ongoing jika ada
        if stats['ongoing_activities'] > 0:
            st.caption(f"🔴 {stats['ongoing_activities']} Aktivitas Berjalan")
    
    except Exception as e:
        st.caption("⚠️ Gagal memuat statistik")


def _render_app_info():
    """
    Merender informasi aplikasi di sidebar.
    """
    st.caption("ℹ️ **Tentang Aplikasi**")
    st.caption(
        "Aplikasi Logbook untuk mencatat "
        "waktu kerja dan menganalisis efisiensi proyek."
    )


def _route_to_page(page_name: str):
    """
    Melakukan routing ke halaman yang dipilih.
    
    Args:
        page_name: Nama halaman tujuan
    """
    # Dictionary mapping nama halaman ke fungsi render
    page_routes = {
        "Dashboard": dashboard.render,
        "Proyek": projects.render,
        "Aktivitas": activities.render,
        "Analisis": analysis.render,
        "Pengaturan": settings.render
    }
    
    # Panggil fungsi render untuk halaman yang dipilih
    render_function = page_routes.get(page_name)
    
    if render_function:
        try:
            render_function()
        except Exception as e:
            st.error(
                f"Terjadi kesalahan saat memuat halaman {page_name}. "
                f"Detail: {str(e)}"
            )
    else:
        st.error(f"Halaman '{page_name}' tidak ditemukan.")


# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    main()
