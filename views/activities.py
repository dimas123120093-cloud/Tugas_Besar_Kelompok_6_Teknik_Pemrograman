"""
================================================================================
ACTIVITIES PAGE - Halaman Pencatatan Waktu/Aktivitas
================================================================================
Halaman ini menangani pencatatan waktu kerja termasuk:
- Memulai aktivitas baru (timer)
- Input waktu manual
- Melihat dan mengelola riwayat aktivitas
================================================================================
Mata Kuliah: Teknik Pemrograman
Program Studi: Teknik Geofisika - Semester 5
================================================================================
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta

import database as db
from utils import (
    format_duration,
    format_elapsed_time,
    validate_time_range,
    validate_notes,
    sanitize_string
)
from constants import (
    SUCCESS_MESSAGES,
    ERROR_MESSAGES,
    DEFAULT_SETTINGS,
    DISPLAY_CONFIG
)


def render():
    """
    Merender halaman Pencatatan Waktu.
    
    Halaman ini menampilkan:
    1. Aktivitas yang sedang berjalan (ongoing)
    2. Tab untuk memulai aktivitas baru
    3. Tab untuk input manual
    4. Tab untuk riwayat aktivitas
    """
    st.header("⏱️ Pencatatan Waktu")
    
    # Tampilkan aktivitas ongoing di atas
    _render_ongoing_activities()
    
    # Tab utama
    tab_start, tab_manual, tab_history = st.tabs([
        "▶️ Mulai Aktivitas", 
        "📝 Input Manual", 
        "📜 Riwayat"
    ])
    
    with tab_start:
        _render_start_activity_form()
    
    with tab_manual:
        _render_manual_input_form()
    
    with tab_history:
        _render_activity_history()


def _render_ongoing_activities():
    """
    Merender daftar aktivitas yang sedang berjalan.
    """
    try:
        ongoing = db.get_ongoing_activities()
    except Exception as e:
        st.error(f"Gagal mengambil aktivitas: {str(e)}")
        return
    
    if not ongoing:
        return
    
    st.subheader("🔴 Aktivitas Sedang Berjalan")
    
    for activity in ongoing:
        _render_ongoing_card(activity)
    
    st.divider()


def _render_ongoing_card(activity: dict):
    """
    Merender kartu untuk aktivitas yang sedang berjalan.
    
    Args:
        activity: Dictionary data aktivitas
    """
    start_time = datetime.fromisoformat(activity['start_time'])
    elapsed = format_elapsed_time(start_time)
    
    col_info, col_elapsed, col_action = st.columns([3, 1, 1])
    
    with col_info:
        st.write(f"**{activity['project_name']}**")
        st.caption(f"Mulai: {start_time.strftime('%d/%m/%Y %H:%M')}")
    
    with col_elapsed:
        st.write(f"⏱️ {elapsed}")
    
    with col_action:
        if st.button("⏹️ Selesai", key=f"end_{activity['id']}"):
            st.session_state[f'ending_{activity["id"]}'] = True
    
    # Form untuk menyelesaikan aktivitas
    if st.session_state.get(f'ending_{activity["id"]}'):
        _render_end_activity_form(activity, start_time)


def _render_end_activity_form(activity: dict, start_time: datetime):
    """
    Merender form untuk menyelesaikan aktivitas.
    
    Args:
        activity: Dictionary data aktivitas
        start_time: Waktu mulai aktivitas
    """
    with st.form(f"end_form_{activity['id']}"):
        end_option = st.radio(
            "Waktu selesai:", 
            ["Sekarang", "Manual"], 
            horizontal=True
        )
        
        if end_option == "Manual":
            col_date, col_time = st.columns(2)
            end_date = col_date.date_input("Tanggal", value=date.today())
            end_time_input = col_time.time_input(
                "Jam", 
                value=datetime.now().time()
            )
        
        col_confirm, col_cancel = st.columns(2)
        confirmed = col_confirm.form_submit_button("✅ Konfirmasi", type="primary")
        cancelled = col_cancel.form_submit_button("❌ Batal")
        
        if confirmed:
            if end_option == "Sekarang":
                end_dt = datetime.now()
            else:
                end_dt = datetime.combine(end_date, end_time_input)
            
            _end_activity(activity['id'], end_dt, start_time)
        
        if cancelled:
            del st.session_state[f'ending_{activity["id"]}']
            st.rerun()


def _render_start_activity_form():
    """
    Merender form untuk memulai aktivitas baru.
    """
    try:
        active_projects = db.get_active_projects()
    except Exception as e:
        st.error(f"Gagal mengambil proyek: {str(e)}")
        return
    
    if not active_projects:
        st.warning(
            "Tidak ada proyek aktif. "
            "Silakan buat proyek baru di menu Proyek terlebih dahulu."
        )
        return
    
    with st.form("start_activity_form"):
        # Pilih proyek
        project_options = {p['id']: p['name'] for p in active_projects}
        selected_project = st.selectbox(
            "Pilih Proyek *",
            options=list(project_options.keys()),
            format_func=lambda x: project_options[x]
        )
        
        # Pilih waktu mulai
        start_option = st.radio(
            "Waktu mulai:", 
            ["Sekarang", "Manual"], 
            horizontal=True
        )
        
        if start_option == "Manual":
            col_date, col_time = st.columns(2)
            start_date = col_date.date_input("Tanggal", value=date.today())
            start_time_input = col_time.time_input(
                "Jam", 
                value=time(DEFAULT_SETTINGS['default_work_start_hour'], 0)
            )
        
        # Catatan
        notes = st.text_input(
            "Catatan (opsional)",
            help="Deskripsi singkat tentang apa yang akan dikerjakan"
        )
        
        submitted = st.form_submit_button("▶️ Mulai Aktivitas", type="primary")
        
        if submitted:
            if start_option == "Sekarang":
                start_dt = datetime.now()
            else:
                start_dt = datetime.combine(start_date, start_time_input)
            
            _start_activity(selected_project, start_dt, notes)


def _render_manual_input_form():
    """
    Merender form untuk input aktivitas manual (dengan waktu mulai dan selesai).
    """
    try:
        active_projects = db.get_active_projects()
    except Exception as e:
        st.error(f"Gagal mengambil proyek: {str(e)}")
        return
    
    if not active_projects:
        st.warning(
            "Tidak ada proyek aktif. "
            "Silakan buat proyek baru di menu Proyek terlebih dahulu."
        )
        return
    
    with st.form("manual_activity_form", clear_on_submit=True):
        # Pilih proyek
        project_options = {p['id']: p['name'] for p in active_projects}
        selected_project = st.selectbox(
            "Pilih Proyek *",
            options=list(project_options.keys()),
            format_func=lambda x: project_options[x],
            key="manual_project"
        )
        
        # Waktu mulai
        st.write("**Waktu Mulai**")
        col_start_date, col_start_time = st.columns(2)
        start_date = col_start_date.date_input(
            "Tanggal Mulai", 
            value=date.today(),
            key="manual_start_date"
        )
        start_time_input = col_start_time.time_input(
            "Jam Mulai", 
            value=time(DEFAULT_SETTINGS['default_work_start_hour'], 0),
            key="manual_start_time"
        )
        
        # Waktu selesai
        st.write("**Waktu Selesai**")
        col_end_date, col_end_time = st.columns(2)
        end_date = col_end_date.date_input(
            "Tanggal Selesai", 
            value=date.today(),
            key="manual_end_date"
        )
        end_time_input = col_end_time.time_input(
            "Jam Selesai", 
            value=time(DEFAULT_SETTINGS['default_work_end_hour'], 0),
            key="manual_end_time"
        )
        
        # Catatan
        notes = st.text_input(
            "Catatan",
            key="manual_notes",
            help="Deskripsi tentang aktivitas yang dikerjakan"
        )
        
        # Preview durasi
        start_dt = datetime.combine(start_date, start_time_input)
        end_dt = datetime.combine(end_date, end_time_input)
        
        if end_dt > start_dt:
            duration_hours = (end_dt - start_dt).total_seconds() / 3600
            st.info(f"📊 Durasi: **{format_duration(duration_hours)}**")
        elif end_dt <= start_dt:
            st.warning("⚠️ Waktu selesai harus setelah waktu mulai!")
        
        submitted = st.form_submit_button("💾 Simpan Aktivitas", type="primary")
        
        if submitted:
            _create_manual_activity(selected_project, start_dt, end_dt, notes)


def _render_activity_history():
    """
    Merender riwayat aktivitas dengan filter.
    """
    # Filter
    col_project_filter, col_date_filter = st.columns(2)
    
    try:
        all_projects = db.get_all_projects()
    except Exception as e:
        st.error(f"Gagal mengambil proyek: {str(e)}")
        return
    
    with col_project_filter:
        filter_options = {"all": "Semua Proyek"}
        filter_options.update({p['id']: p['name'] for p in all_projects})
        selected_filter = st.selectbox(
            "Filter Proyek",
            options=list(filter_options.keys()),
            format_func=lambda x: filter_options[x]
        )
    
    with col_date_filter:
        default_start = date.today() - timedelta(days=DISPLAY_CONFIG['default_days_filter'])
        date_range = st.date_input(
            "Rentang Tanggal",
            value=(default_start, date.today())
        )
    
    # Ambil data
    try:
        if selected_filter == "all":
            activities = db.get_all_activities()
        else:
            activities = db.get_activities_by_project(selected_filter)
    except Exception as e:
        st.error(f"Gagal mengambil aktivitas: {str(e)}")
        return
    
    if not activities:
        st.info("Belum ada aktivitas tercatat.")
        return
    
    # Konversi ke DataFrame
    df = pd.DataFrame(activities)
    df['start_time'] = pd.to_datetime(df['start_time'], format='mixed')
    df['end_time'] = pd.to_datetime(df['end_time'], format='mixed', errors='coerce')
    
    # Filter berdasarkan tanggal
    if len(date_range) == 2:
        start_filter = datetime.combine(date_range[0], time(0, 0))
        end_filter = datetime.combine(date_range[1], time(23, 59, 59))
        df = df[(df['start_time'] >= start_filter) & (df['start_time'] <= end_filter)]
    
    if df.empty:
        st.info("Tidak ada aktivitas pada rentang tanggal ini.")
        return
    
    # Ringkasan
    total_hours = df['duration_hours'].sum() if df['duration_hours'].notna().any() else 0
    st.write(f"**{len(df)} aktivitas** | Total: **{format_duration(total_hours)}**")
    
    # Format kolom tampilan
    df['Durasi'] = df['duration_hours'].apply(
        lambda x: format_duration(x) if pd.notna(x) else "🔴 Berjalan"
    )
    df['Waktu'] = df['start_time'].dt.strftime(DISPLAY_CONFIG['datetime_format'])
    
    display_df = df[['project_name', 'Waktu', 'Durasi', 'notes']].rename(columns={
        'project_name': 'Proyek',
        'notes': 'Catatan'
    })
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Kelola aktivitas
    st.divider()
    _render_activity_management(df, all_projects)


def _render_activity_management(df: pd.DataFrame, all_projects: list):
    """
    Merender bagian untuk mengedit/menghapus aktivitas.
    
    Args:
        df: DataFrame aktivitas
        all_projects: List semua proyek
    """
    st.write("**Kelola Aktivitas**")
    
    activity_options = {
        row['id']: f"{row['project_name']} - {row['start_time'].strftime('%d/%m %H:%M')}" 
        for _, row in df.iterrows()
    }
    
    selected_activity = st.selectbox(
        "Pilih aktivitas:",
        options=list(activity_options.keys()),
        format_func=lambda x: activity_options[x]
    )
    
    col_edit, col_delete = st.columns(2)
    
    with col_edit:
        if st.button("✏️ Edit Aktivitas"):
            st.session_state['edit_activity'] = selected_activity
    
    with col_delete:
        if st.button("🗑️ Hapus Aktivitas"):
            _delete_activity(selected_activity)
    
    # Form edit
    if st.session_state.get('edit_activity'):
        _render_edit_activity_form(df, all_projects)


def _render_edit_activity_form(df: pd.DataFrame, all_projects: list):
    """
    Merender form untuk mengedit aktivitas.
    """
    activity_id = st.session_state['edit_activity']
    activity_data = df[df['id'] == activity_id].iloc[0]
    
    with st.form("edit_activity_form"):
        st.write("**Edit Aktivitas**")
        
        # Pilih proyek
        project_options = {p['id']: p['name'] for p in all_projects}
        current_project_index = list(project_options.keys()).index(activity_data['project_id']) \
            if activity_data['project_id'] in project_options else 0
        
        new_project = st.selectbox(
            "Proyek",
            options=list(project_options.keys()),
            format_func=lambda x: project_options[x],
            index=current_project_index
        )
        
        # Waktu mulai
        col_start_date, col_start_time = st.columns(2)
        new_start_date = col_start_date.date_input(
            "Tanggal Mulai", 
            value=activity_data['start_time'].date()
        )
        new_start_time = col_start_time.time_input(
            "Jam Mulai", 
            value=activity_data['start_time'].time()
        )
        
        # Waktu selesai (jika ada)
        if pd.notna(activity_data['end_time']):
            col_end_date, col_end_time = st.columns(2)
            new_end_date = col_end_date.date_input(
                "Tanggal Selesai", 
                value=activity_data['end_time'].date()
            )
            new_end_time = col_end_time.time_input(
                "Jam Selesai", 
                value=activity_data['end_time'].time()
            )
        else:
            new_end_date, new_end_time = None, None
            st.info("Aktivitas ini masih berjalan (ongoing)")
        
        # Catatan
        new_notes = st.text_input(
            "Catatan", 
            value=activity_data['notes'] if activity_data['notes'] else ""
        )
        
        col_save, col_cancel = st.columns(2)
        submitted = col_save.form_submit_button("💾 Simpan", type="primary")
        cancelled = col_cancel.form_submit_button("❌ Batal")
        
        if submitted:
            new_start = datetime.combine(new_start_date, new_start_time)
            new_end = datetime.combine(new_end_date, new_end_time) \
                if new_end_date and new_end_time else None
            
            _update_activity(activity_id, new_project, new_start, new_end, new_notes)
        
        if cancelled:
            del st.session_state['edit_activity']
            st.rerun()


# ==================== HELPER FUNCTIONS ====================

def _start_activity(project_id: int, start_time: datetime, notes: str):
    """Memulai aktivitas baru."""
    notes = sanitize_string(notes)
    
    is_valid, error = validate_notes(notes)
    if not is_valid:
        st.error(error)
        return
    
    try:
        db.create_activity(project_id, start_time, notes=notes)
        st.success(SUCCESS_MESSAGES['activity_started'])
        st.rerun()
    except Exception as e:
        st.error(f"{ERROR_MESSAGES['database_error']} Detail: {str(e)}")


def _end_activity(activity_id: int, end_time: datetime, start_time: datetime):
    """Menyelesaikan aktivitas yang sedang berjalan."""
    is_valid, error = validate_time_range(start_time, end_time)
    if not is_valid:
        st.error(error)
        return
    
    try:
        db.end_activity(activity_id, end_time)
        # Bersihkan session state
        if f'ending_{activity_id}' in st.session_state:
            del st.session_state[f'ending_{activity_id}']
        st.success(SUCCESS_MESSAGES['activity_ended'])
        st.rerun()
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"{ERROR_MESSAGES['database_error']} Detail: {str(e)}")


def _create_manual_activity(project_id: int, start_time: datetime, 
                            end_time: datetime, notes: str):
    """Membuat aktivitas dengan input manual."""
    notes = sanitize_string(notes)
    
    is_valid, error = validate_time_range(start_time, end_time)
    if not is_valid:
        st.error(error)
        return
    
    is_valid, error = validate_notes(notes)
    if not is_valid:
        st.error(error)
        return
    
    try:
        db.create_activity(project_id, start_time, end_time, notes)
        duration = (end_time - start_time).total_seconds() / 3600
        st.success(f"{SUCCESS_MESSAGES['activity_ended']} ({format_duration(duration)})")
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"{ERROR_MESSAGES['database_error']} Detail: {str(e)}")


def _update_activity(activity_id: int, project_id: int, start_time: datetime,
                     end_time: datetime, notes: str):
    """Memperbarui aktivitas."""
    notes = sanitize_string(notes)
    
    if end_time:
        is_valid, error = validate_time_range(start_time, end_time)
        if not is_valid:
            st.error(error)
            return
    
    try:
        success = db.update_activity(activity_id, project_id, start_time, end_time, notes)
        if success:
            st.success(SUCCESS_MESSAGES['activity_updated'])
            del st.session_state['edit_activity']
            st.rerun()
        else:
            st.error(ERROR_MESSAGES['activity_not_found'])
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"{ERROR_MESSAGES['database_error']} Detail: {str(e)}")


def _delete_activity(activity_id: int):
    """Menghapus aktivitas."""
    try:
        success = db.delete_activity(activity_id)
        if success:
            st.success(SUCCESS_MESSAGES['activity_deleted'])
            st.rerun()
        else:
            st.error(ERROR_MESSAGES['activity_not_found'])
    except Exception as e:
        st.error(f"{ERROR_MESSAGES['database_error']} Detail: {str(e)}")
