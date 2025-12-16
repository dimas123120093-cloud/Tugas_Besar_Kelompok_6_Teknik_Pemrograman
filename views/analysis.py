"""
================================================================================
ANALYSIS PAGE - Halaman Analisis Statistik
================================================================================
Halaman ini menampilkan analisis statistik dari data aktivitas
menggunakan NumPy dan SciPy untuk perhitungan, serta Plotly
untuk visualisasi.
================================================================================
Mata Kuliah: Teknik Pemrograman
Program Studi: Teknik Geofisika - Semester 5
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import database as db
from utils import (
    format_duration,
    calculate_efficiency,
    calculate_statistics,
    get_efficiency_color
)
from constants import CHART_CONFIG, CHART_COLORS


def render():
    """
    Merender halaman Analisis Statistik.

    Halaman ini menampilkan:
    1. Statistik deskriptif (mean, median, std, quartiles, dll)
    2. Bar chart rata-rata durasi per proyek
    3. Bar chart efisiensi proyek
    """
    st.header("📈 Analisis Statistik")

    # Ambil data durasi
    try:
        durations = db.get_duration_array()
    except Exception as e:
        st.error(f"Gagal mengambil data: {str(e)}")
        return

    if not durations:
        st.info(
            "Belum ada data aktivitas untuk dianalisis. "
            "Silakan catat beberapa aktivitas terlebih dahulu."
        )
        return

    # Konversi ke numpy array
    duration_array = np.array(durations)

    # ==================== SECTION: STATISTIK DESKRIPTIF ====================
    _render_descriptive_statistics(duration_array)

    st.divider()

    # ==================== SECTION: DURASI PER PROYEK ====================
    _render_duration_per_project()

    st.divider()

    # ==================== SECTION: EFISIENSI PROYEK ====================
    _render_efficiency_chart()


def _render_descriptive_statistics(data: np.ndarray):
    """
    Merender statistik deskriptif menggunakan NumPy dan SciPy.

    Args:
        data: Array numpy berisi durasi aktivitas
    """
    st.subheader("📊 Statistik Deskriptif Durasi Aktivitas")
    st.caption("Dihitung menggunakan NumPy dan SciPy")

    # Hitung statistik
    stats = calculate_statistics(data.tolist())

    # Tampilkan dalam 3 kolom
    col_central, col_spread, col_quartile = st.columns(3)

    with col_central:
        st.write("**Ukuran Pemusatan**")
        st.metric(
            label="Mean (Rata-rata)",
            value=f"{stats['mean']:.2f} jam",
            help="Nilai rata-rata dari semua durasi aktivitas"
        )
        st.metric(
            label="Median (Nilai Tengah)",
            value=f"{stats['median']:.2f} jam",
            help="Nilai tengah ketika data diurutkan"
        )

    with col_spread:
        st.write("**Ukuran Penyebaran**")
        st.metric(
            label="Standar Deviasi",
            value=f"{stats['std']:.2f} jam",
            help="Ukuran seberapa tersebar data dari rata-rata"
        )
        st.metric(
            label="Range (Rentang)",
            value=f"{stats['range']:.2f} jam",
            help="Selisih antara nilai maksimum dan minimum"
        )

    with col_quartile:
        st.write("**Kuartil**")
        st.metric(
            label="Q1 (Kuartil 1 - 25%)",
            value=f"{stats['q1']:.2f} jam",
            help="25% data berada di bawah nilai ini"
        )
        st.metric(
            label="Q3 (Kuartil 3 - 75%)",
            value=f"{stats['q3']:.2f} jam",
            help="75% data berada di bawah nilai ini"
        )


def _render_duration_per_project():
    """
    Merender bar chart rata-rata durasi aktivitas per proyek.
    """
    st.subheader("⏱️ Rata-rata Durasi per Proyek")

    try:
        project_stats = db.get_project_statistics()
    except Exception as e:
        st.error(f"Gagal mengambil statistik proyek: {str(e)}")
        return

    if not project_stats:
        st.info("Belum ada data proyek untuk dianalisis.")
        return

    # Siapkan data
    duration_data = []
    for project in project_stats:
        avg_duration = project['avg_duration'] or 0
        activity_count = project['activity_count'] or 0

        if activity_count > 0:
            duration_data.append({
                'Proyek': project['name'],
                'Rata-rata Durasi': avg_duration,
                'Jumlah Aktivitas': activity_count
            })

    if not duration_data:
        st.info("Belum ada aktivitas tercatat untuk proyek manapun.")
        return

    df_duration = pd.DataFrame(duration_data)

    # Buat bar chart horizontal
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df_duration['Proyek'],
        x=df_duration['Rata-rata Durasi'],
        orientation='h',
        marker_color=CHART_COLORS['primary'],
        text=[f"{d:.1f} jam" for d in df_duration['Rata-rata Durasi']],
        textposition='outside',
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Rata-rata: <b>%{x:.2f} jam</b><br>"
            "<extra></extra>"
        )
    ))

    # Layout
    max_duration = df_duration['Rata-rata Durasi'].max()
    fig.update_xaxes(
        title_text="Rata-rata Durasi (jam)",
        range=[0, max_duration * 1.3]
    )
    fig.update_yaxes(title_text="")

    # Tinggi dinamis
    chart_height = max(CHART_CONFIG['height_small'], len(df_duration) * 50)

    fig.update_layout(
        height=chart_height,
        margin=CHART_CONFIG['margin_with_labels'],
        showlegend=False
    )

    st.plotly_chart(fig, width="stretch")

    # Keterangan
    st.caption("📌 Grafik menunjukkan rata-rata durasi per aktivitas untuk setiap proyek")


def _render_efficiency_chart():
    """
    Merender bar chart efisiensi proyek dengan penjelasan yang mudah dipahami.
    """
    st.subheader("⚡ Efisiensi Proyek")
    
    # Alert penjelasan
    st.info(
        "**Apa itu Efisiensi?** Perbandingan antara waktu yang sudah dikerjakan "
        "dengan waktu yang diestimasi di awal.\n\n"
        "**Rumus:** Efisiensi (%) = (Jam Tercatat ÷ Jam Estimasi) × 100"
    )

    try:
        project_stats = db.get_project_statistics()
    except Exception as e:
        st.error(f"Gagal mengambil statistik proyek: {str(e)}")
        return

    if not project_stats:
        st.info("Belum ada data proyek untuk dianalisis.")
        return

    # Siapkan data efisiensi
    efficiency_data = []
    for project in project_stats:
        logged = project['total_logged_hours'] or 0
        estimated = project['estimated_hours'] or 1
        efficiency = calculate_efficiency(logged, estimated)
        
        # Tentukan status dan interpretasi berdasarkan efisiensi
        if efficiency < 50:
            status = "🔴 Baru Dimulai"
            sisa = estimated - logged
            interpretasi = f"Sisa {sisa:.1f} jam lagi untuk mencapai target"
        elif efficiency < 80:
            status = "🟡 Sedang Berjalan"
            sisa = estimated - logged
            interpretasi = f"Sisa {sisa:.1f} jam lagi ({100-efficiency:.0f}%)"
        elif efficiency < 100:
            status = "🟢 Hampir Selesai"
            sisa = estimated - logged
            interpretasi = f"Tinggal {sisa:.1f} jam lagi!"
        elif efficiency == 100:
            status = "🟢 Selesai"
            interpretasi = "Target tercapai tepat waktu!"
        else:
            status = "🔵 Melebihi Estimasi"
            lebih = logged - estimated
            interpretasi = f"Lebih {lebih:.1f} jam dari estimasi awal"

        efficiency_data.append({
            'Proyek': project['name'],
            'Efisiensi': efficiency,
            'Tercatat': logged,
            'Estimasi': estimated,
            'Status': status,
            'Interpretasi': interpretasi
        })

    df_efficiency = pd.DataFrame(efficiency_data)

    # Tentukan warna berdasarkan efisiensi
    colors = [get_efficiency_color(eff) for eff in df_efficiency['Efisiensi']]

    # Buat bar chart horizontal
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df_efficiency['Proyek'],
        x=df_efficiency['Efisiensi'],
        orientation='h',
        marker_color=colors,
        text=[f"{eff:.0f}%" for eff in df_efficiency['Efisiensi']],
        textposition='outside',
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Efisiensi: <b>%{x:.1f}%</b><br>"
            "<extra></extra>"
        ),
        customdata=df_efficiency[['Tercatat', 'Estimasi']].values
    ))

    # Tambahkan garis target 100%
    fig.add_vline(
        x=100,
        line_dash="dash",
        line_color="gray",
        annotation_text="Target 100%",
        annotation_position="top"
    )

    # Layout
    max_efficiency = df_efficiency['Efisiensi'].max()
    fig.update_xaxes(
        title_text="Efisiensi (%)",
        range=[0, max(max_efficiency * 1.2, 120)]
    )
    fig.update_yaxes(title_text="")

    # Tinggi dinamis berdasarkan jumlah proyek
    chart_height = max(CHART_CONFIG['height_small'], len(df_efficiency) * 50)

    fig.update_layout(
        height=chart_height,
        margin=CHART_CONFIG['margin_with_labels'],
        showlegend=False
    )

    st.plotly_chart(fig, width="stretch")

    # Legenda warna
    st.markdown(
        """
        | Warna | Range | Arti |
        |-------|-------|------|
        | 🔴 Merah | < 50% | Proyek baru dimulai |
        | 🟡 Kuning | 50-80% | Sedang berjalan |
        | 🟢 Hijau | 80-99% | Hampir selesai |
        | 🟢 Hijau | = 100% | Selesai tepat waktu |
        | 🔵 Biru | > 100% | Waktu melebihi estimasi awal |
        """
    )
    
    st.divider()
    
    # Tabel detail per proyek
    st.subheader("📋 Detail Efisiensi per Proyek")
    
    for idx, row in df_efficiency.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                st.write(f"**{row['Proyek']}**")
                st.caption(f"Tercatat: {row['Tercatat']:.1f} jam / Estimasi: {row['Estimasi']:.1f} jam")
            
            with col2:
                st.write(f"**{row['Efisiensi']:.0f}%**")
                st.caption(row['Status'])
            
            with col3:
                # Tampilkan interpretasi dengan warna yang sesuai
                if row['Efisiensi'] < 50:
                    st.error(row['Interpretasi'])
                elif row['Efisiensi'] < 80:
                    st.warning(row['Interpretasi'])
                elif row['Efisiensi'] <= 100:
                    st.success(row['Interpretasi'])
                else:
                    st.info(row['Interpretasi'])
            
            st.divider()
