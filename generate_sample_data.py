"""
================================================================================
SAMPLE DATA GENERATOR
================================================================================
Script untuk mengisi database dengan data contoh agar bisa langsung
mencoba fitur analisis dan visualisasi.
================================================================================
"""

import random
from datetime import datetime, timedelta
import database as db

# Data contoh proyek
SAMPLE_PROJECTS = [
    {
        "name": "Pengolahan Data Seismik Laut Jawa",
        "description": "Pemrosesan dan interpretasi data seismik 2D untuk identifikasi struktur bawah permukaan di Laut Jawa bagian utara",
        "estimated_hours": 45.0,
        "category": "Pengolahan Data Seismik"
    },
    {
        "name": "Survey Gravity Daerah Panas Bumi Kamojang",
        "description": "Pengukuran dan interpretasi data gravity untuk eksplorasi panas bumi di daerah Kamojang, Jawa Barat",
        "estimated_hours": 30.0,
        "category": "Interpretasi Data Gravity"
    },
    {
        "name": "Pemodelan Resistivitas Akuifer Bandung",
        "description": "Pemodelan 2D data resistivitas untuk pemetaan akuifer di cekungan Bandung",
        "estimated_hours": 25.0,
        "category": "Pemodelan Resistivitas"
    },
    {
        "name": "Analisis Well Log Sumur Eksplorasi X-1",
        "description": "Interpretasi well log untuk karakterisasi reservoir dan identifikasi zona prospek",
        "estimated_hours": 35.0,
        "category": "Analisis Well Log"
    },
    {
        "name": "Laporan Tugas Akhir - Bab 3 Metodologi",
        "description": "Penulisan bab metodologi penelitian tugas akhir tentang metode seismik refraksi",
        "estimated_hours": 20.0,
        "category": "Penulisan Laporan"
    },
    {
        "name": "Praktikum Geolistrik Lapangan",
        "description": "Pengukuran geolistrik metode Schlumberger di lokasi praktikum kampus",
        "estimated_hours": 15.0,
        "category": "Pengukuran Lapangan"
    }
]

# Catatan aktivitas contoh
SAMPLE_NOTES = [
    "Quality control data mentah",
    "Preprocessing dan filtering noise",
    "Picking horizon reflector",
    "Koreksi terrain dan elevasi",
    "Pembuatan peta anomali Bouguer",
    "Pemodelan inversi 2D",
    "Interpretasi hasil pemodelan",
    "Review literatur terkait",
    "Diskusi dengan dosen pembimbing",
    "Revisi berdasarkan feedback",
    "Dokumentasi hasil pengolahan",
    "Persiapan presentasi progress",
    "Analisis sensitivitas parameter",
    "Validasi model dengan data sumur",
    "Penulisan draft laporan",
    "Kalibrasi alat ukur",
    "Pengambilan data lapangan",
    "Input data ke software",
    "Pembuatan cross-section",
    "Korelasi antar sumur"
]


def generate_sample_data():
    """Generate sample data untuk testing aplikasi."""
    
    print("="*60)
    print("   GENERATE SAMPLE DATA")
    print("="*60)
    
    # Reinitialize database
    db.init_database()
    print("\n✓ Database initialized")
    
    # Generate proyek
    print("\n📁 Membuat proyek...")
    project_ids = []
    
    for i, proj_info in enumerate(SAMPLE_PROJECTS):
        project_id = db.create_project(
            proj_info["name"],
            proj_info["description"],
            proj_info["estimated_hours"],
            proj_info["category"]
        )
        project_ids.append(project_id)
        
        # Update status untuk beberapa proyek
        if i == 3:  # Proyek ke-4 selesai
            db.update_project_status(project_id, "completed")
        elif i == 5:  # Proyek ke-6 ditunda
            db.update_project_status(project_id, "paused")
        
        print(f"   ✓ {proj_info['name'][:40]}...")
    
    # Generate aktivitas
    print("\n⏱️  Membuat aktivitas...")
    start_date = datetime.now() - timedelta(days=30)
    activity_count = 0
    
    for day_offset in range(31):  # 31 hari data
        current_date = start_date + timedelta(days=day_offset)
        
        # Skip weekend dengan probabilitas 70%
        if current_date.weekday() >= 5 and random.random() > 0.3:
            continue
        
        # 1-4 aktivitas per hari
        num_activities = random.randint(1, 4)
        day_start_hour = 8
        
        for _ in range(num_activities):
            # Pilih proyek secara random (lebih sering proyek awal)
            weights = [3, 3, 2, 2, 1, 1]
            project_idx = random.choices(range(len(project_ids)), weights=weights[:len(project_ids)])[0]
            project_id = project_ids[project_idx]
            
            # Generate waktu
            start_hour = day_start_hour + random.randint(0, 2)
            start_minute = random.randint(0, 59)
            duration_hours = round(random.uniform(0.5, 4.0), 1)
            
            start_time = current_date.replace(
                hour=min(start_hour, 17), 
                minute=start_minute, 
                second=0, 
                microsecond=0
            )
            end_time = start_time + timedelta(hours=duration_hours)
            
            # Buat aktivitas
            db.create_activity(
                project_id,
                start_time,
                end_time,
                random.choice(SAMPLE_NOTES)
            )
            
            activity_count += 1
            day_start_hour = end_time.hour + 1
            
            # Jangan lebih dari jam 6 sore
            if day_start_hour >= 18:
                break
    
    print(f"   ✓ {activity_count} aktivitas dibuat")
    
    # Tambahkan satu aktivitas yang sedang berjalan
    ongoing_project = project_ids[0]
    db.create_activity(
        ongoing_project,
        datetime.now() - timedelta(hours=1, minutes=30),
        None,  # Belum selesai
        "Sedang mengerjakan QC data"
    )
    print("   ✓ 1 aktivitas ongoing ditambahkan")
    
    # Tampilkan ringkasan
    print("\n" + "="*60)
    print("   RINGKASAN")
    print("="*60)
    
    stats = db.get_overall_statistics()
    print(f"\n   Total Proyek      : {stats['total_projects']}")
    print(f"   Proyek Aktif      : {stats['active_projects']}")
    print(f"   Total Aktivitas   : {stats['total_activities']}")
    print(f"   Total Jam Kerja   : {stats['total_hours']:.1f} jam")
    print(f"   Aktivitas Ongoing : {stats['ongoing_activities']}")
    print(f"   Hari Aktif        : {stats['active_days']}")
    
    print("\n✅ Sample data berhasil dibuat!")
    print("\n   Jalankan aplikasi dengan:")
    print("   $ streamlit run app.py")
    print("="*60)


if __name__ == "__main__":
    generate_sample_data()
