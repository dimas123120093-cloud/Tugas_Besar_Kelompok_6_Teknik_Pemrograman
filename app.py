"""
================================================================================
APLIKASI LOGBOOK PENCATAT WAKTU PROYEK & ANALISIS EFISIENSI
================================================================================
Versi: Streamlit + SQLite (Simplified UI)
Mata Kuliah: Teknik Pemrograman
Program Studi: Teknik Geofisika - Semester 5
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date, time
from typing import Optional
import math

# Import database module
import database as db

# ==================== KONFIGURASI HALAMAN ====================
st.set_page_config(
    page_title="Logbook Proyek",
    page_icon="📋",
    layout="wide"
)

# ==================== KONSTANTA ====================
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

STATUS_OPTIONS = ["active", "completed", "paused"]
STATUS_LABELS = {"active": "🟢 Aktif", "completed": "🔵 Selesai", "paused": "🟡 Ditunda"}

# ==================== HELPER FUNCTIONS ====================

def format_duration(hours: float) -> str:
    """Format durasi dalam jam menjadi string readable."""
    if hours is None or (isinstance(hours, float) and math.isnan(hours)):
        return "0j 0m"
    if hours == 0:
        return "0j 0m"
    total_minutes = int(hours * 60)
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h}j {m}m"


def calculate_efficiency(logged: float, estimated: float) -> float:
    """Hitung efisiensi proyek."""
    if logged is None or (isinstance(logged, float) and math.isnan(logged)):
        logged = 0
    if estimated is None or estimated == 0 or (isinstance(estimated, float) and math.isnan(estimated)):
        return 0
    return (logged / estimated) * 100


def get_efficiency_color(efficiency: float) -> str:
    """Dapatkan warna berdasarkan efisiensi."""
    if efficiency < 50:
        return "#dc3545"
    elif efficiency < 80:
        return "#ffc107"
    elif efficiency <= 100:
        return "#28a745"
    else:
        return "#17a2b8"


# ==================== HALAMAN DASHBOARD ====================

def page_dashboard():
    """Halaman Dashboard utama."""
    st.header("📊 Dashboard")
    
    stats_data = db.get_overall_statistics()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Proyek", stats_data['total_projects'], f"{stats_data['active_projects']} aktif")
    col2.metric("Total Aktivitas", stats_data['total_activities'], f"{stats_data['ongoing_activities']} berjalan")
    col3.metric("Total Jam", format_duration(stats_data['total_hours']))
    col4.metric("Rata-rata/Hari", f"{stats_data['avg_hours_per_day']:.1f} jam")
    
    st.divider()
    
    # Charts
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📈 Tren Waktu Kerja (30 Hari)")
        daily_data = db.get_daily_hours(30)
        
        if daily_data:
            df_daily = pd.DataFrame(daily_data)
            df_daily['date'] = pd.to_datetime(df_daily['date'], format='mixed')
            df_daily['tanggal_format'] = df_daily['date'].dt.strftime('%d %b %Y')
            
            fig = px.area(df_daily, x='date', y='total_hours',
                         custom_data=['tanggal_format', 'total_hours'])
            
            # Format hover yang lebih informatif
            fig.update_traces(
                hovertemplate="<b>%{customdata[0]}</b><br>" +
                              "Jam Kerja: <b>%{customdata[1]:.1f} jam</b><extra></extra>",
                fillcolor='rgba(99, 110, 250, 0.4)',
                line=dict(color='rgb(99, 110, 250)', width=2)
            )
            
            # Format sumbu X hanya tampilkan tanggal (hari)
            fig.update_xaxes(
                title_text="Tanggal",
                tickformat="%d %b",  # Format: 10 Dec
                dtick="D1",  # Interval 1 hari
                tickangle=45
            )
            fig.update_yaxes(title_text="Jam Kerja")
            fig.update_layout(
                height=300, 
                margin=dict(l=0, r=0, t=10, b=0),
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data.")
    
    with col_right:
        st.subheader("📁 Per Kategori")
        cat_data = db.get_category_distribution()
        
        if cat_data:
            df_cat = pd.DataFrame(cat_data)
            fig = px.pie(df_cat, values='total_hours', names='category', hole=0.4)
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data.")
    
    # Project stats
    st.subheader("📊 Progress Proyek")
    project_stats = db.get_project_statistics()
    
    if project_stats:
        for proj in project_stats:
            logged = proj['total_logged_hours'] if proj['total_logged_hours'] else 0
            estimated = proj['estimated_hours'] if proj['estimated_hours'] else 1
            eff = calculate_efficiency(logged, estimated)
            
            # Pastikan nilai progress antara 0 dan 1
            progress_value = min(max(eff / 100, 0.0), 1.0)
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{proj['name']}**")
                st.progress(progress_value)
            with col2:
                st.write(f"{format_duration(logged)} / {format_duration(estimated)}")
            with col3:
                # Warna berdasarkan efisiensi
                if eff > 100:
                    st.write(f"🔵 **{eff:.0f}%**")
                elif eff >= 80:
                    st.write(f"🟢 **{eff:.0f}%**")
                elif eff >= 50:
                    st.write(f"🟡 **{eff:.0f}%**")
                else:
                    st.write(f"🔴 **{eff:.0f}%**")


# ==================== HALAMAN PROYEK ====================

def page_projects():
    """Halaman manajemen proyek."""
    st.header("📁 Manajemen Proyek")
    
    tab1, tab2 = st.tabs(["Daftar Proyek", "Tambah Baru"])
    
    with tab1:
        projects = db.get_all_projects()
        
        if not projects:
            st.info("Belum ada proyek.")
        else:
            for proj in projects:
                eff = calculate_efficiency(proj.get('total_logged_hours', 0), proj['estimated_hours'])
                
                with st.container():
                    col1, col2, col3 = st.columns([4, 1, 1])
                    
                    with col1:
                        st.write(f"**{proj['name']}** - {proj['category']}")
                        st.caption(f"{STATUS_LABELS.get(proj['status'])} | Progress: {format_duration(proj.get('total_logged_hours', 0))} / {format_duration(proj['estimated_hours'])} ({eff:.0f}%)")
                    
                    with col2:
                        if st.button("Edit", key=f"edit_{proj['id']}"):
                            st.session_state['editing_project'] = proj['id']
                    
                    with col3:
                        if st.button("Hapus", key=f"del_{proj['id']}"):
                            db.delete_project(proj['id'])
                            st.rerun()
                    
                    st.divider()
            
            # Edit form
            if 'editing_project' in st.session_state:
                proj = db.get_project_by_id(st.session_state['editing_project'])
                if proj:
                    st.subheader("Edit Proyek")
                    with st.form("edit_form"):
                        name = st.text_input("Nama", value=proj['name'])
                        desc = st.text_area("Deskripsi", value=proj.get('description', ''))
                        estimated = st.number_input("Estimasi (jam)", value=float(proj['estimated_hours']), min_value=0.5)
                        category = st.selectbox("Kategori", CATEGORIES, index=CATEGORIES.index(proj['category']) if proj['category'] in CATEGORIES else 0)
                        status = st.selectbox("Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(proj['status']), format_func=lambda x: STATUS_LABELS.get(x, x))
                        
                        col1, col2 = st.columns(2)
                        if col1.form_submit_button("Simpan"):
                            db.update_project(proj['id'], name, desc, estimated, category, status)
                            del st.session_state['editing_project']
                            st.rerun()
                        if col2.form_submit_button("Batal"):
                            del st.session_state['editing_project']
                            st.rerun()
    
    with tab2:
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("Nama Proyek *")
            desc = st.text_area("Deskripsi")
            col1, col2 = st.columns(2)
            estimated = col1.number_input("Estimasi Waktu (jam) *", min_value=0.5, value=10.0)
            category = col2.selectbox("Kategori *", CATEGORIES)
            
            if st.form_submit_button("Simpan Proyek", type="primary"):
                if name.strip():
                    db.create_project(name, desc, estimated, category)
                    st.success("✅ Proyek berhasil ditambahkan!")
                else:
                    st.error("Nama proyek wajib diisi!")


# ==================== HALAMAN AKTIVITAS ====================

def page_activities():
    """Halaman pencatatan aktivitas."""
    st.header("⏱️ Pencatatan Waktu")
    
    # Ongoing activities
    ongoing = db.get_ongoing_activities()
    if ongoing:
        st.subheader("🔴 Sedang Berjalan")
        for act in ongoing:
            start_time = datetime.fromisoformat(act['start_time'])
            elapsed = (datetime.now() - start_time).total_seconds() / 3600
            
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"**{act['project_name']}** - Mulai: {start_time.strftime('%d/%m %H:%M')}")
            col2.write(f"⏱️ {format_duration(elapsed)}")
            
            if col3.button("Selesai", key=f"end_{act['id']}"):
                st.session_state[f'ending_{act["id"]}'] = True
            
            if st.session_state.get(f'ending_{act["id"]}'):
                with st.form(f"end_form_{act['id']}"):
                    end_option = st.radio("Waktu selesai:", ["Sekarang", "Manual"], horizontal=True)
                    if end_option == "Manual":
                        c1, c2 = st.columns(2)
                        end_date = c1.date_input("Tanggal", value=date.today())
                        end_time_input = c2.time_input("Jam", value=datetime.now().time())
                    
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("Konfirmasi"):
                        end_dt = datetime.now() if end_option == "Sekarang" else datetime.combine(end_date, end_time_input)
                        if end_dt > start_time:
                            db.end_activity(act['id'], end_dt)
                            del st.session_state[f'ending_{act["id"]}']
                            st.rerun()
                        else:
                            st.error("Waktu selesai harus setelah waktu mulai!")
                    if c2.form_submit_button("Batal"):
                        del st.session_state[f'ending_{act["id"]}']
                        st.rerun()
        st.divider()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Mulai Aktivitas", "Input Manual", "Riwayat"])
    
    with tab1:
        active_projects = db.get_active_projects()
        if not active_projects:
            st.warning("Tidak ada proyek aktif.")
        else:
            with st.form("start_form"):
                project_options = {p['id']: p['name'] for p in active_projects}
                project = st.selectbox("Proyek", options=list(project_options.keys()), format_func=lambda x: project_options[x])
                
                start_option = st.radio("Waktu mulai:", ["Sekarang", "Manual"], horizontal=True)
                if start_option == "Manual":
                    c1, c2 = st.columns(2)
                    start_date = c1.date_input("Tanggal", value=date.today())
                    start_time_input = c2.time_input("Jam", value=time(9, 0))
                
                notes = st.text_input("Catatan (opsional)")
                
                if st.form_submit_button("Mulai Aktivitas", type="primary"):
                    start_dt = datetime.now() if start_option == "Sekarang" else datetime.combine(start_date, start_time_input)
                    db.create_activity(project, start_dt, notes=notes)
                    st.success("✅ Aktivitas dimulai!")
                    st.rerun()
    
    with tab2:
        active_projects = db.get_active_projects()
        if not active_projects:
            st.warning("Tidak ada proyek aktif.")
        else:
            with st.form("manual_form", clear_on_submit=True):
                project_options = {p['id']: p['name'] for p in active_projects}
                project = st.selectbox("Proyek", options=list(project_options.keys()), format_func=lambda x: project_options[x], key="manual_proj")
                
                st.write("**Waktu Mulai**")
                c1, c2 = st.columns(2)
                start_date = c1.date_input("Tanggal", value=date.today(), key="m_sd")
                start_time_input = c2.time_input("Jam", value=time(9, 0), key="m_st")
                
                st.write("**Waktu Selesai**")
                c3, c4 = st.columns(2)
                end_date = c3.date_input("Tanggal", value=date.today(), key="m_ed")
                end_time_input = c4.time_input("Jam", value=time(17, 0), key="m_et")
                
                notes = st.text_input("Catatan", key="m_notes")
                
                # Preview
                start_dt = datetime.combine(start_date, start_time_input)
                end_dt = datetime.combine(end_date, end_time_input)
                duration = (end_dt - start_dt).total_seconds() / 3600
                
                if duration > 0:
                    st.info(f"Durasi: **{format_duration(duration)}**")
                
                if st.form_submit_button("Simpan", type="primary"):
                    if end_dt <= start_dt:
                        st.error("Waktu selesai harus setelah waktu mulai!")
                    else:
                        db.create_activity(project, start_dt, end_dt, notes)
                        st.success(f"✅ Aktivitas tersimpan! ({format_duration(duration)})")
    
    with tab3:
        # Filters
        c1, c2 = st.columns(2)
        all_projects = db.get_all_projects()
        filter_options = {"all": "Semua Proyek"}
        filter_options.update({p['id']: p['name'] for p in all_projects})
        selected_filter = c1.selectbox("Filter Proyek", options=list(filter_options.keys()), format_func=lambda x: filter_options[x])
        
        date_range = c2.date_input("Rentang Tanggal", value=(date.today() - timedelta(days=30), date.today()))
        
        # Get data
        activities = db.get_all_activities() if selected_filter == "all" else db.get_activities_by_project(selected_filter)
        
        if not activities:
            st.info("Belum ada aktivitas.")
        else:
            df = pd.DataFrame(activities)
            df['start_time'] = pd.to_datetime(df['start_time'], format='mixed')
            df['end_time'] = pd.to_datetime(df['end_time'], format='mixed', errors='coerce')
            
            # Filter by date
            if len(date_range) == 2:
                start_filter = datetime.combine(date_range[0], time(0, 0))
                end_filter = datetime.combine(date_range[1], time(23, 59, 59))
                df = df[(df['start_time'] >= start_filter) & (df['start_time'] <= end_filter)]
            
            if df.empty:
                st.info("Tidak ada data pada rentang tanggal ini.")
            else:
                # Summary
                total_hours = df['duration_hours'].sum() if df['duration_hours'].notna().any() else 0
                st.write(f"**{len(df)} aktivitas** | Total: **{format_duration(total_hours)}**")
                
                # Table
                df['Durasi'] = df['duration_hours'].apply(lambda x: format_duration(x) if pd.notna(x) else "🔴 Berjalan")
                df['Waktu'] = df['start_time'].dt.strftime('%d/%m/%Y %H:%M')
                
                display_df = df[['project_name', 'Waktu', 'Durasi', 'notes']].rename(columns={
                    'project_name': 'Proyek',
                    'notes': 'Catatan'
                })
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Edit/Delete section
                st.divider()
                st.write("**Kelola Aktivitas**")
                
                activity_options = {row['id']: f"{row['project_name']} - {row['start_time'].strftime('%d/%m %H:%M')}" for _, row in df.iterrows()}
                selected_act = st.selectbox("Pilih aktivitas:", options=list(activity_options.keys()), format_func=lambda x: activity_options[x])
                
                c1, c2 = st.columns(2)
                if c1.button("Edit Aktivitas"):
                    st.session_state['edit_activity'] = selected_act
                if c2.button("Hapus Aktivitas"):
                    db.delete_activity(selected_act)
                    st.success("Aktivitas dihapus!")
                    st.rerun()
                
                # Edit form
                if st.session_state.get('edit_activity'):
                    act_id = st.session_state['edit_activity']
                    act_data = df[df['id'] == act_id].iloc[0]
                    
                    with st.form("edit_activity_form"):
                        st.write("**Edit Aktivitas**")
                        
                        proj_options = {p['id']: p['name'] for p in all_projects}
                        new_proj = st.selectbox("Proyek", options=list(proj_options.keys()), format_func=lambda x: proj_options[x],
                                               index=list(proj_options.keys()).index(act_data['project_id']) if act_data['project_id'] in proj_options else 0)
                        
                        c1, c2 = st.columns(2)
                        new_start_date = c1.date_input("Tgl Mulai", value=act_data['start_time'].date())
                        new_start_time = c2.time_input("Jam Mulai", value=act_data['start_time'].time())
                        
                        if pd.notna(act_data['end_time']):
                            c3, c4 = st.columns(2)
                            new_end_date = c3.date_input("Tgl Selesai", value=act_data['end_time'].date())
                            new_end_time = c4.time_input("Jam Selesai", value=act_data['end_time'].time())
                        else:
                            new_end_date, new_end_time = None, None
                            st.info("Aktivitas masih berjalan")
                        
                        new_notes = st.text_input("Catatan", value=act_data['notes'] if act_data['notes'] else "")
                        
                        c1, c2 = st.columns(2)
                        if c1.form_submit_button("Simpan"):
                            new_start = datetime.combine(new_start_date, new_start_time)
                            new_end = datetime.combine(new_end_date, new_end_time) if new_end_date and new_end_time else None
                            
                            if new_end and new_end <= new_start:
                                st.error("Waktu selesai harus setelah waktu mulai!")
                            else:
                                db.update_activity(act_id, new_proj, new_start, new_end, new_notes)
                                del st.session_state['edit_activity']
                                st.success("✅ Aktivitas diperbarui!")
                                st.rerun()
                        
                        if c2.form_submit_button("Batal"):
                            del st.session_state['edit_activity']
                            st.rerun()