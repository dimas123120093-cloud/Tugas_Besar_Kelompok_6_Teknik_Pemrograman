"""
================================================================================
SETTINGS PAGE - Halaman Pengaturan Aplikasi
================================================================================
Halaman ini menangani pengaturan aplikasi termasuk:
- Target jam kerja per hari
- Threshold efisiensi
- Export data ke CSV
- Reset database
================================================================================
Mata Kuliah: Teknik Pemrograman
Program Studi: Teknik Geofisika - Semester 5
================================================================================
"""

import streamlit as st
import pandas as pd
import os

import database as db
from constants import DATABASE_FILE, SUCCESS_MESSAGES, ERROR_MESSAGES


def render():
    """
    Merender halaman Pengaturan.
    
    Halaman ini memiliki beberapa section:
    1. Pengaturan target dan threshold
    2. Export data ke CSV
    3. Reset database (danger zone)
    """
    st.header("⚙️ Pengaturan")
    
    # Ambil settings saat ini
    try:
        settings = db.get_all_settings()
    except Exception as e:
        st.error(f"Gagal mengambil pengaturan: {str(e)}")
        settings = {}
    
    # Layout 2 kolom
    col_settings, col_export = st.columns(2)
    
    with col_settings:
        _render_settings_form(settings)
    
    with col_export:
        _render_export_section()
    
    st.divider()
    
    # Danger zone
    _render_danger_zone()


def _render_settings_form(settings: dict):
    """
    Merender form pengaturan target dan threshold.
    
    Args:
        settings: Dictionary pengaturan saat ini
    """
    st.subheader("🎯 Target & Threshold")
    
    with st.form("settings_form"):
        # Target jam per hari
        current_target = float(settings.get('target_hours_per_day', 8))
        target_hours = st.number_input(
            "Target Jam Kerja per Hari",
            min_value=1.0,
            max_value=24.0,
            value=current_target,
            step=0.5,
            help="Target jam kerja harian yang ingin dicapai"
        )
        
        # Threshold efisiensi
        current_threshold = float(settings.get('efficiency_threshold', 0.7))
        efficiency_threshold = st.slider(
            "Threshold Efisiensi",
            min_value=0.0,
            max_value=1.0,
            value=current_threshold,
            step=0.05,
            help="Batas minimum efisiensi yang dianggap baik (0.7 = 70%)"
        )
        
        # Info
        st.info(
            f"📊 Dengan threshold {efficiency_threshold:.0%}, proyek dianggap "
            f"berjalan baik jika efisiensinya di atas {efficiency_threshold * 100:.0f}%"
        )
        
        submitted = st.form_submit_button("💾 Simpan Pengaturan", type="primary")
        
        if submitted:
            _save_settings(target_hours, efficiency_threshold)


def _save_settings(target_hours: float, efficiency_threshold: float):
    """
    Menyimpan pengaturan ke database.
    
    Args:
        target_hours: Target jam per hari
        efficiency_threshold: Threshold efisiensi
    """
    try:
        db.set_setting('target_hours_per_day', str(target_hours))
        db.set_setting('efficiency_threshold', str(efficiency_threshold))
        st.success(SUCCESS_MESSAGES['settings_saved'])
    except Exception as e:
        st.error(f"{ERROR_MESSAGES['database_error']} Detail: {str(e)}")


def _render_export_section():
    """
    Merender section untuk export data ke CSV.
    """
    st.subheader("📤 Export Data")
    
    # Export aktivitas
    try:
        activities = db.get_all_activities()
        if activities:
            df_activities = pd.DataFrame(activities)
            csv_activities = df_activities.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Aktivitas (CSV)",
                data=csv_activities,
                file_name="logbook_aktivitas.csv",
                mime="text/csv",
                help="Download semua data aktivitas dalam format CSV"
            )
        else:
            st.info("Belum ada data aktivitas untuk di-export.")
    except Exception as e:
        st.error(f"Gagal menyiapkan data aktivitas: {str(e)}")
    
    st.write("")  # Spacer
    
    # Export proyek
    try:
        projects = db.get_all_projects()
        if projects:
            df_projects = pd.DataFrame(projects)
            csv_projects = df_projects.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Proyek (CSV)",
                data=csv_projects,
                file_name="logbook_proyek.csv",
                mime="text/csv",
                help="Download semua data proyek dalam format CSV"
            )
        else:
            st.info("Belum ada data proyek untuk di-export.")
    except Exception as e:
        st.error(f"Gagal menyiapkan data proyek: {str(e)}")
    
    # Info format
    st.caption(
        "💡 File CSV dapat dibuka dengan Microsoft Excel, "
        "Google Sheets, atau aplikasi spreadsheet lainnya."
    )


def _render_danger_zone():
    """
    Merender danger zone untuk reset database.
    """
    st.subheader("⚠️ Danger Zone")
    
    st.warning(
        "**Perhatian!** Tindakan di bawah ini tidak dapat dibatalkan. "
        "Pastikan Anda sudah mengexport data penting sebelum melanjutkan."
    )
    
    # Tombol reset
    if st.button("🗑️ Reset Database", type="secondary"):
        st.session_state['confirm_reset'] = True
    
    # Dialog konfirmasi
    if st.session_state.get('confirm_reset'):
        _render_reset_confirmation()


def _render_reset_confirmation():
    """
    Merender dialog konfirmasi untuk reset database.
    """
    st.error(
        "⚠️ **PERINGATAN KERAS!**\n\n"
        "Anda akan menghapus **SEMUA DATA** termasuk:\n"
        "- Semua proyek\n"
        "- Semua catatan aktivitas\n"
        "- Semua pengaturan\n\n"
        "Tindakan ini **TIDAK DAPAT DIBATALKAN**!"
    )
    
    col_confirm, col_cancel = st.columns(2)
    
    with col_confirm:
        if st.button("✅ Ya, Hapus Semua Data", type="primary"):
            _reset_database()
    
    with col_cancel:
        if st.button("❌ Batal"):
            del st.session_state['confirm_reset']
            st.rerun()


def _reset_database():
    """
    Mereset database dengan menghapus file dan membuat ulang.
    """
    try:
        # Hapus file database jika ada
        if os.path.exists(DATABASE_FILE):
            os.remove(DATABASE_FILE)
        
        # Reinisialisasi database
        db.init_database()
        
        # Bersihkan session state
        if 'confirm_reset' in st.session_state:
            del st.session_state['confirm_reset']
        
        st.success(SUCCESS_MESSAGES['database_reset'])
        st.balloons()
        st.rerun()
        
    except Exception as e:
        st.error(f"Gagal mereset database: {str(e)}")
