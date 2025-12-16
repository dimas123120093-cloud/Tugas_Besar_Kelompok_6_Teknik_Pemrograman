"""
================================================================================
PROJECTS PAGE - Halaman Manajemen Proyek
================================================================================
Halaman ini menangani operasi CRUD (Create, Read, Update, Delete)
untuk proyek-proyek dalam aplikasi Logbook.
================================================================================
Mata Kuliah: Teknik Pemrograman
Program Studi: Teknik Geofisika - Semester 5
================================================================================
"""

import streamlit as st

import database as db
from utils import (
    format_duration, 
    calculate_efficiency,
    validate_project,
    sanitize_string
)
from constants import (
    CATEGORIES, 
    STATUS_OPTIONS, 
    STATUS_LABELS,
    SUCCESS_MESSAGES,
    ERROR_MESSAGES
)


def render():
    """
    Merender halaman Manajemen Proyek.
    
    Halaman ini memiliki dua tab:
    1. Daftar Proyek: Melihat, edit, dan hapus proyek
    2. Tambah Baru: Form untuk membuat proyek baru
    """
    st.header("📁 Manajemen Proyek")
    
    tab_list, tab_add = st.tabs(["📋 Daftar Proyek", "➕ Tambah Baru"])
    
    with tab_list:
        _render_project_list()
    
    with tab_add:
        _render_add_project_form()


def _render_project_list():
    """
    Merender daftar semua proyek dengan opsi edit dan hapus.
    """
    try:
        projects = db.get_all_projects()
    except Exception as e:
        st.error(f"{ERROR_MESSAGES['database_error']} Detail: {str(e)}")
        return
    
    if not projects:
        st.info("Belum ada proyek. Silakan tambah proyek baru di tab 'Tambah Baru'.")
        return
    
    # Render setiap proyek
    for project in projects:
        _render_project_card(project)
    
    # Form edit jika ada proyek yang sedang diedit
    if 'editing_project' in st.session_state:
        _render_edit_form()


def _render_project_card(project: dict):
    """
    Merender kartu untuk satu proyek.
    
    Args:
        project: Dictionary data proyek
    """
    logged_hours = project.get('total_logged_hours', 0) or 0
    estimated_hours = project['estimated_hours']
    efficiency = calculate_efficiency(logged_hours, estimated_hours)
    
    with st.container():
        col_info, col_edit, col_delete = st.columns([4, 1, 1])
        
        with col_info:
            st.write(f"**{project['name']}** - {project['category']}")
            status_label = STATUS_LABELS.get(project['status'], project['status'])
            progress_text = (
                f"{status_label} | "
                f"Progress: {format_duration(logged_hours)} / "
                f"{format_duration(estimated_hours)} ({efficiency:.0f}%)"
            )
            st.caption(progress_text)
        
        with col_edit:
            if st.button("✏️ Edit", key=f"edit_{project['id']}"):
                st.session_state['editing_project'] = project['id']
                st.rerun()
        
        with col_delete:
            if st.button("🗑️ Hapus", key=f"del_{project['id']}"):
                _delete_project(project['id'])
        
        st.divider()


def _render_edit_form():
    """
    Merender form untuk mengedit proyek yang dipilih.
    """
    project_id = st.session_state['editing_project']
    
    try:
        project = db.get_project_by_id(project_id)
    except Exception as e:
        st.error(f"Gagal mengambil data proyek: {str(e)}")
        del st.session_state['editing_project']
        return
    
    if not project:
        st.error(ERROR_MESSAGES['project_not_found'])
        del st.session_state['editing_project']
        return
    
    st.subheader("✏️ Edit Proyek")
    
    with st.form("edit_project_form"):
        nama_proyek = st.text_input(
            "Nama Proyek *", 
            value=project['name'],
            help="Nama proyek minimal 3 karakter"
        )
        
        deskripsi = st.text_area(
            "Deskripsi", 
            value=project.get('description', '') or '',
            help="Deskripsi opsional tentang proyek"
        )
        
        estimasi_jam = st.number_input(
            "Estimasi Waktu (jam) *", 
            value=float(project['estimated_hours']), 
            min_value=0.5,
            max_value=1000.0,
            help="Estimasi total jam yang dibutuhkan (0.5 - 1000 jam)"
        )
        
        kategori_index = (
            CATEGORIES.index(project['category']) 
            if project['category'] in CATEGORIES 
            else 0
        )
        kategori = st.selectbox("Kategori *", CATEGORIES, index=kategori_index)
        
        status_index = (
            STATUS_OPTIONS.index(project['status']) 
            if project['status'] in STATUS_OPTIONS 
            else 0
        )
        status = st.selectbox(
            "Status", 
            STATUS_OPTIONS, 
            index=status_index,
            format_func=lambda x: STATUS_LABELS.get(x, x)
        )
        
        col_save, col_cancel = st.columns(2)
        submitted = col_save.form_submit_button("💾 Simpan", type="primary")
        cancelled = col_cancel.form_submit_button("❌ Batal")
        
        if submitted:
            _update_project(
                project['id'], nama_proyek, deskripsi, 
                estimasi_jam, kategori, status
            )
        
        if cancelled:
            del st.session_state['editing_project']
            st.rerun()


def _render_add_project_form():
    """
    Merender form untuk menambah proyek baru.
    """
    with st.form("add_project_form", clear_on_submit=True):
        nama_proyek = st.text_input(
            "Nama Proyek *",
            help="Nama proyek minimal 3 karakter"
        )
        
        deskripsi = st.text_area(
            "Deskripsi",
            help="Deskripsi opsional tentang proyek"
        )
        
        col_estimasi, col_kategori = st.columns(2)
        
        with col_estimasi:
            estimasi_jam = st.number_input(
                "Estimasi Waktu (jam) *", 
                min_value=0.5, 
                max_value=1000.0,
                value=10.0,
                help="Estimasi total jam yang dibutuhkan"
            )
        
        with col_kategori:
            kategori = st.selectbox("Kategori *", CATEGORIES)
        
        submitted = st.form_submit_button("💾 Simpan Proyek", type="primary")
        
        if submitted:
            _create_project(nama_proyek, deskripsi, estimasi_jam, kategori)


def _create_project(name: str, description: str, estimated_hours: float, 
                    category: str):
    """
    Membuat proyek baru dengan validasi.
    """
    name = sanitize_string(name)
    description = sanitize_string(description)
    
    is_valid, errors = validate_project(name, estimated_hours, category)
    
    if not is_valid:
        for error in errors:
            st.error(error)
        return
    
    try:
        db.create_project(name, description, estimated_hours, category)
        st.success(SUCCESS_MESSAGES['project_created'])
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"{ERROR_MESSAGES['database_error']} Detail: {str(e)}")


def _update_project(project_id: int, name: str, description: str, 
                    estimated_hours: float, category: str, status: str):
    """
    Memperbarui proyek dengan validasi.
    """
    name = sanitize_string(name)
    description = sanitize_string(description)
    
    is_valid, errors = validate_project(name, estimated_hours, category)
    
    if not is_valid:
        for error in errors:
            st.error(error)
        return
    
    try:
        success = db.update_project(
            project_id, name, description, estimated_hours, category, status
        )
        
        if success:
            st.success(SUCCESS_MESSAGES['project_updated'])
            del st.session_state['editing_project']
            st.rerun()
        else:
            st.error(ERROR_MESSAGES['project_not_found'])
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"{ERROR_MESSAGES['database_error']} Detail: {str(e)}")


def _delete_project(project_id: int):
    """
    Menghapus proyek.
    """
    try:
        success = db.delete_project(project_id)
        
        if success:
            st.success(SUCCESS_MESSAGES['project_deleted'])
            st.rerun()
        else:
            st.error(ERROR_MESSAGES['project_not_found'])
    except Exception as e:
        st.error(f"{ERROR_MESSAGES['database_error']} Detail: {str(e)}")
