# ==================== HALAMAN ANALISIS ====================

def page_analysis():
    """Halaman analisis statistik."""
    st.header("📈 Analisis Statistik")
    
    durations = db.get_duration_array()
    
    if not durations:
        st.info("Belum ada data untuk dianalisis.)"
        return
    
    dur_array = np.array(durations)
    
    # Statistics
    st.subheader("📊 Statistik Durasi (NumPy & SciPy)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Ukuran Pemusatan**")
        st.metric("Mean", f"{np.mean(dur_array):.2f} jam")
        st.metric("Median", f"{np.median(dur_array):.2f} jam")
    
    with col2:
        st.write("**Ukuran Penyebaran**")
        st.metric("Std Deviasi", f"{np.std(dur_array):.2f} jam")
        st.metric("Range", f"{np.ptp(dur_array):.2f} jam")
    
    with col3:
        st.write("**Kuartil**")
        st.metric("Q1 (25%)", f"{np.percentile(dur_array, 25):.2f} jam")
        st.metric("Q3 (75%)", f"{np.percentile(dur_array, 75):.2f} jam")
    
    if len(dur_array) >= 3:
        st.write(f"**Skewness:** {stats.skew(dur_array):.3f} | **Kurtosis:** {stats.kurtosis(dur_array):.3f}")
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Histogram")
        
        # Buat dataframe untuk histogram
        df_hist = pd.DataFrame({'durasi': dur_array})
        
        fig = px.histogram(
            df_hist, 
            x='durasi', 
            nbins=10,
            labels={'durasi': 'Durasi (jam)', 'count': 'Frekuensi'}
        )
        
        # Perbaiki hover
        fig.update_traces(
            hovertemplate="<b>Rentang: %{x:.1f} jam</b><br>" +
                          "Frekuensi: <b>%{y} aktivitas</b><extra></extra>",
            marker_color='rgb(99, 110, 250)'
        )
        
        # Tambah garis mean
        mean_val = np.mean(dur_array)
        fig.add_vline(
            x=mean_val, 
            line_dash="dash", 
            line_color="red",
            annotation_text=f"Mean: {mean_val:.2f}j",
            annotation_position="top"
        )
        
        fig.update_xaxes(title_text="Durasi (jam)")
        fig.update_yaxes(title_text="Frekuensi")
        fig.update_layout(
            height=300, 
            margin=dict(l=0, r=0, t=10, b=0), 
            showlegend=False,
            bargap=0.1
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Box Plot")
        
        # Hitung statistik untuk hover
        q1 = np.percentile(dur_array, 25)
        median = np.median(dur_array)
        q3 = np.percentile(dur_array, 75)
        min_val = np.min(dur_array)
        max_val = np.max(dur_array)
        
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            y=dur_array,
            name='Durasi',
            boxpoints='outliers',
            marker_color='rgb(99, 110, 250)',
            line_color='rgb(99, 110, 250)',
            hoverinfo='y',
            hovertemplate="<b>%{y:.2f} jam</b><extra></extra>"
        ))
        
        fig.update_yaxes(title_text="Durasi (jam)")
        fig.update_layout(
            height=300, 
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False
        )
        
        # Tambahkan anotasi statistik
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Min: {min_val:.2f}j | Q1: {q1:.2f}j | Median: {median:.2f}j | Q3: {q3:.2f}j | Max: {max_val:.2f}j")
    
    # Efficiency
    st.subheader("⚡ Efisiensi Proyek")
    project_stats = db.get_project_statistics()
    
    if project_stats:
        eff_data = []
        for proj in project_stats:
            logged = proj['total_logged_hours'] if proj['total_logged_hours'] else 0
            estimated = proj['estimated_hours'] if proj['estimated_hours'] else 1
            eff = calculate_efficiency(logged, estimated)
            eff_data.append({
                'Proyek': proj['name'], 
                'Efisiensi': eff,
                'Tercatat': logged,
                'Estimasi': estimated
            })
        
        df_eff = pd.DataFrame(eff_data)
        
        # Buat bar chart dengan go.Figure untuk kontrol lebih baik
        fig = go.Figure()
        
        # Tentukan warna berdasarkan efisiensi
        colors = []
        for eff in df_eff['Efisiensi']:
            if eff >= 100:
                colors.append('rgb(40, 167, 69)')   # Hijau
            elif eff >= 80:
                colors.append('rgb(40, 167, 69)')   # Hijau
            elif eff >= 50:
                colors.append('rgb(255, 193, 7)')   # Kuning
            else:
                colors.append('rgb(220, 53, 69)')   # Merah
        
        fig.add_trace(go.Bar(
            y=df_eff['Proyek'],
            x=df_eff['Efisiensi'],
            orientation='h',
            marker_color=colors,
            text=[f"{e:.0f}%" for e in df_eff['Efisiensi']],
            textposition='outside',
            hovertemplate="<b>%{y}</b><br>" +
                          "Efisiensi: <b>%{x:.1f}%</b><br>" +
                          "<extra></extra>",
            customdata=df_eff[['Tercatat', 'Estimasi']].values
        ))
        
        # Tambah garis target 100%
        fig.add_vline(
            x=100, 
            line_dash="dash", 
            line_color="gray",
            annotation_text="Target 100%",
            annotation_position="top"
        )
        
        fig.update_xaxes(title_text="Efisiensi (%)", range=[0, max(df_eff['Efisiensi'].max() * 1.2, 120)])
        fig.update_yaxes(title_text="")
        fig.update_layout(
            height=max(200, len(df_eff) * 50),  # Tinggi dinamis berdasarkan jumlah proyek
            margin=dict(l=0, r=50, t=10, b=0),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)


# ==================== HALAMAN PENGATURAN ====================

def page_settings():
    """Halaman pengaturan."""
    st.header("⚙️ Pengaturan")
    
    settings = db.get_all_settings()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Target")
        with st.form("settings_form"):
            target = st.number_input("Target jam/hari", value=float(settings.get('target_hours_per_day', 8)), min_value=1.0, max_value=24.0)
            threshold = st.slider("Threshold efisiensi", 0.0, 1.0, float(settings.get('efficiency_threshold', 0.7)))
            
            if st.form_submit_button("Simpan"):
                db.set_setting('target_hours_per_day', str(target))
                db.set_setting('efficiency_threshold', str(threshold))
                st.success("✅ Tersimpan!")
    
    with col2:
        st.subheader("Export Data")
        
        activities = db.get_all_activities()
        if activities:
            df = pd.DataFrame(activities)
            st.download_button("Download Aktivitas (CSV)", df.to_csv(index=False), "aktivitas.csv", "text/csv")
        
        projects = db.get_all_projects()
        if projects:
            df = pd.DataFrame(projects)
            st.download_button("Download Proyek (CSV)", df.to_csv(index=False), "proyek.csv", "text/csv")
    
    st.divider()
    
    st.subheader("⚠️ Reset Data")
    if st.button("Reset Database"):
        st.session_state['confirm_reset'] = True
    
    if st.session_state.get('confirm_reset'):
        st.warning("Semua data akan dihapus!")
        c1, c2 = st.columns(2)
        if c1.button("Ya, Hapus Semua"):
            import os
            if os.path.exists(db.DATABASE_FILE):
                os.remove(db.DATABASE_FILE)
            db.init_database()
            del st.session_state['confirm_reset']
            st.success("Database direset!")
            st.rerun()
        if c2.button("Batal"):
            del st.session_state['confirm_reset']
            st.rerun()


# ==================== MAIN APP ====================

def main():
    """Main application."""
    
    # Sidebar navigation
    with st.sidebar:
        st.title("📋 Logbook")
        st.caption("Teknik Geofisika")
        st.divider()
        
        page = st.radio(
            "Menu",
            ["Dashboard", "Proyek", "Aktivitas", "Analisis", "Pengaturan"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Quick stats
        stats = db.get_overall_statistics()
        st.caption(f"📁 {stats['total_projects']} Proyek")
        st.caption(f"⏱️ {format_duration(stats['total_hours'])} Total")
        st.caption(f"📅 {stats['active_days']} Hari Aktif")
    
    # Page routing
    if page == "Dashboard":
        page_dashboard()
    elif page == "Proyek":
        page_projects()
    elif page == "Aktivitas":
        page_activities()
    elif page == "Analisis":
        page_analysis()
    elif page == "Pengaturan":
        page_settings()


if __name__ == "__main__":
    main()
