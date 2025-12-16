"""
================================================================================
DASHBOARD PAGE - Halaman Dashboard Utama
================================================================================
Halaman ini menampilkan ringkasan statistik dan visualisasi data
termasuk metrik utama, tren waktu kerja, dan progress proyek.
================================================================================
Mata Kuliah: Teknik Pemrograman
Program Studi: Teknik Geofisika - Semester 5
================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

import database as db
from utils import format_duration, calculate_efficiency
from constants import CHART_CONFIG, CHART_COLORS


def render():
    st.header("Dashboard")
    
    try:
        stats_data = db.get_overall_statistics()
    except Exception as e:
        st.error(f"Gagal mengambil statistik: {str(e)}")
        return
    
    _render_metrics(stats_data)
    
    st.divider()
    
    _render_trend_chart()
    
    st.divider()
    
    col_category, col_progress = st.columns([1, 2])
    
    with col_category:
        _render_category_chart()
    
    with col_progress:
        _render_project_progress()


def _render_metrics(stats_data: dict):
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(
        label="Total Proyek", 
        value=stats_data['total_projects'], 
        delta=f"{stats_data['active_projects']} aktif"
    )
    
    col2.metric(
        label="Total Aktivitas", 
        value=stats_data['total_activities'], 
        delta=f"{stats_data['ongoing_activities']} berjalan"
    )
    
    col3.metric(
        label="Total Jam Kerja", 
        value=format_duration(stats_data['total_hours'])
    )
    
    col4.metric(
        label="Rata-rata/Hari", 
        value=f"{stats_data['avg_hours_per_day']:.1f} jam"
    )


def _render_trend_chart():
    st.subheader("Tren Waktu Kerja")
    
    try:
        all_activities = db.get_all_activities()
    except Exception as e:
        st.error(f"Gagal mengambil data: {str(e)}")
        return
    
    if not all_activities:
        st.info("Belum ada data aktivitas untuk ditampilkan.")
        return
    
    df = pd.DataFrame(all_activities)
    df['start_time'] = pd.to_datetime(df['start_time'], format='mixed')
    
    df['year_month'] = df['start_time'].dt.to_period('M')
    available_months = sorted(df['year_month'].unique(), reverse=True)
    
    nama_bulan = {
        1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
        5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
        9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
    }
    
    month_options = {}
    for period in available_months:
        month_name = nama_bulan[period.month]
        year = period.year
        label = f"{month_name} {year}"
        month_options[label] = period
    
    col_filter, col_spacer = st.columns([1, 3])
    with col_filter:
        selected_label = st.selectbox(
            "Pilih Bulan",
            options=list(month_options.keys()),
            index=0
        )
    
    selected_period = month_options[selected_label]
    
    df_filtered = df[df['year_month'] == selected_period].copy()
    
    # Hitung total jam per hari (HANYA hari yang ada aktivitas)
    df_daily = df_filtered.groupby(df_filtered['start_time'].dt.date)['duration_hours'].sum().reset_index()
    df_daily.columns = ['date', 'total_hours']
    df_daily['date'] = pd.to_datetime(df_daily['date'])
    df_daily = df_daily.sort_values('date')
    
    # Format tanggal untuk tampilan
    df_daily['tanggal_format'] = df_daily['date'].dt.strftime('%d %b')
    
    # Buat grafik area (hanya hari aktif)
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_daily['tanggal_format'],
        y=df_daily['total_hours'],
        mode='lines+markers',
        fill='tozeroy',
        fillcolor='rgba(99, 110, 250, 0.3)',
        line=dict(color='rgb(99, 110, 250)', width=2),
        marker=dict(size=8),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Jam Kerja: <b>%{y:.1f} jam</b>"
            "<extra></extra>"
        )
    ))
    
    fig.update_xaxes(title_text="Tanggal")
    fig.update_yaxes(title_text="Jam Kerja")
    
    fig.update_layout(
        height=280,
        margin={"l": 0, "r": 0, "t": 10, "b": 0},
        hovermode='x unified',
        showlegend=False
    )
    
    st.plotly_chart(fig, width="stretch")
    
    _render_month_summary(df_filtered, selected_label)


def _render_month_summary(df_filtered, month_label):
    total_hours = df_filtered['duration_hours'].sum() if not df_filtered.empty else 0
    days_active = df_filtered['start_time'].dt.date.nunique() if not df_filtered.empty else 0
    total_activities = len(df_filtered)
    avg_per_day = total_hours / days_active if days_active > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Total Jam", value=f"{total_hours:.1f} jam")
    
    with col2:
        st.metric(label="Hari Aktif", value=f"{days_active} hari")
    
    with col3:
        st.metric(label="Aktivitas", value=f"{total_activities}")
    
    with col4:
        st.metric(label="Rata-rata/Hari", value=f"{avg_per_day:.1f} jam")


def _render_category_chart():
    st.subheader("Per Kategori")
    
    try:
        cat_data = db.get_category_distribution()
    except Exception as e:
        st.error(f"Gagal mengambil data: {str(e)}")
        return
    
    if not cat_data:
        st.info("Belum ada data.")
        return
    
    df_cat = pd.DataFrame(cat_data)
    
    fig = px.pie(
        df_cat, 
        values='total_hours', 
        names='category', 
        hole=0.4
    )
    
    fig.update_layout(
        height=CHART_CONFIG['height_medium'],
        margin=CHART_CONFIG['margin'],
        showlegend=False
    )
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label'
    )
    
    st.plotly_chart(fig, width="stretch")


def _render_project_progress():
    st.subheader("Progress Proyek")
    
    try:
        project_stats = db.get_project_statistics()
    except Exception as e:
        st.error(f"Gagal mengambil statistik proyek: {str(e)}")
        return
    
    if not project_stats:
        st.info("Belum ada proyek.")
        return
    
    for project in project_stats:
        logged_hours = project['total_logged_hours'] or 0
        estimated_hours = project['estimated_hours'] or 1
        
        efficiency = calculate_efficiency(logged_hours, estimated_hours)
        progress_value = min(max(efficiency / 100, 0.0), 1.0)
        
        # Tentukan status dan interpretasi
        if efficiency < 50:
            status_text = "Baru Dimulai"
            sisa = estimated_hours - logged_hours
            interpretasi = f"Sisa {sisa:.1f} jam lagi"
        elif efficiency < 80:
            status_text = "Sedang Berjalan"
            sisa = estimated_hours - logged_hours
            interpretasi = f"Sisa {sisa:.1f} jam ({100-efficiency:.0f}%)"
        elif efficiency < 100:
            status_text = "Hampir Selesai"
            sisa = estimated_hours - logged_hours
            interpretasi = f"Tinggal {sisa:.1f} jam lagi!"
        elif efficiency == 100:
            status_text = "Selesai"
            interpretasi = "Target tercapai!"
        else:
            status_text = "Melebihi Estimasi"
            lebih = logged_hours - estimated_hours
            interpretasi = f"Lebih {lebih:.1f} jam"
        
        with st.container():
            # Baris 1: Nama dan persentase
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{project['name']}**")
            
            with col2:
                st.write(f"**{efficiency:.0f}%**")
            
            # Baris 2: Progress bar
            st.progress(progress_value)
            
            # Baris 3: Detail dengan status
            col_detail1, col_detail2 = st.columns(2)
            
            with col_detail1:
                st.caption(f"{format_duration(logged_hours)} / {format_duration(estimated_hours)}")
            
            with col_detail2:
                # Tampilkan status dengan warna
                if efficiency < 50:
                    st.error(f"{status_text}: {interpretasi}")
                elif efficiency < 80:
                    st.warning(f"{status_text}: {interpretasi}")
                elif efficiency <= 100:
                    st.success(f"{status_text}: {interpretasi}")
                else:
                    st.info(f"{status_text}: {interpretasi}")
            
            st.write("")
