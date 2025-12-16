"""
================================================================================
SAMPLE DATA GENERATOR - Generator Data Contoh
================================================================================
Script ini mengisi database dengan data contoh agar pengguna dapat
langsung mencoba fitur analisis dan visualisasi tanpa harus
menginput data secara manual terlebih dahulu.

Penggunaan:
    python generate_sample_data.py
================================================================================
Mata Kuliah: Teknik Pemrograman
Program Studi: Teknik Geofisika - Semester 5
================================================================================
"""

import random
from datetime import datetime, timedelta

import database as db


# ==================== DATA CONTOH PROYEK ====================
SAMPLE_PROJECTS = [
    {
        "name": "Pengolahan Data Seismik Laut Jawa",
        "description": (
            "Pemrosesan dan interpretasi data seismik 2D untuk "
            "identifikasi struktur bawah permukaan di Laut Jawa bagian utara. "
            "Meliputi filtering, migrasi, dan picking horizon."
        ),
        "estimated_hours": 45.0,
        "category": "Pengolahan Data Seismik"
    },
    {
        "name": "Survey Gravity Daerah Panas Bumi Kamojang",
        "description": (
            "Pengukuran dan interpretasi data gravity untuk eksplorasi "
            "panas bumi di daerah Kamojang, Jawa Barat. Termasuk koreksi "
            "terrain dan pembuatan peta anomali Bouguer."
        ),
        "estimated_hours": 30.0,
        "category": "Interpretasi Data Gravity"
    },
    {
        "name": "Pemodelan Resistivitas Akuifer Bandung",
        "description": (
            "Pemodelan 2D data resistivitas untuk pemetaan akuifer "
            "di cekungan Bandung menggunakan metode inversi. "
            "Bertujuan untuk identifikasi zona potensi air tanah."
        ),
        "estimated_hours": 25.0,
        "category": "Pemodelan Resistivitas"
    },
    {
        "name": "Analisis Well Log Sumur Eksplorasi X-1",
        "description": (
            "Interpretasi well log untuk karakterisasi reservoir "
            "dan identifikasi zona prospek hidrokarbon. Meliputi "
            "analisis GR, SP, resistivitas, dan neutron-density."
        ),
        "estimated_hours": 35.0,
        "category": "Analisis Well Log"
    },
    {
        "name": "Laporan Tugas Akhir - Bab 3 Metodologi",
        "description": (
            "Penulisan bab metodologi penelitian tugas akhir "
            "tentang aplikasi metode seismik refraksi untuk "
            "penentuan kedalaman batuan dasar."
        ),
        "estimated_hours": 20.0,
        "category": "Penulisan Laporan"
    },
    {
        "name": "Praktikum Geolistrik Lapangan",
        "description": (
            "Pengukuran geolistrik metode Schlumberger di lokasi "
            "praktikum kampus. Meliputi pengambilan data, input, "
            "dan interpretasi kurva sounding."
        ),
        "estimated_hours": 15.0,
        "category": "Pengukuran Lapangan"
    }
]

# ==================== CATATAN AKTIVITAS CONTOH ====================
SAMPLE_NOTES = [
    "Quality control data mentah",
    "Preprocessing dan filtering noise",
    "Picking horizon reflector utama",
    "Koreksi terrain dan elevasi",
    "Pembuatan peta anomali Bouguer",
    "Pemodelan inversi 2D",
    "Interpretasi hasil pemodelan",
    "Review literatur terkait",
    "Diskusi dengan dosen pembimbing",
    "Revisi berdasarkan feedback dosen",
    "Dokumentasi hasil pengolahan",
    "Persiapan presentasi progress",
    "Analisis sensitivitas parameter model",
    "Validasi model dengan data sumur",
    "Penulisan draft laporan",
    "Kalibrasi alat ukur di lapangan",
    "Pengambilan data lapangan",
    "Input data ke software pengolahan",
    "Pembuatan cross-section interpretasi",
    "Korelasi antar sumur eksplorasi"
]


def generate_sample_data():
    """
    Generate data contoh untuk testing aplikasi.
    
    Fungsi ini akan:
    1. Menginisialisasi ulang database
    2. Membuat 6 proyek contoh dengan kategori berbeda
    3. Membuat aktivitas random selama 31 hari terakhir
    4. Menambahkan 1 aktivitas ongoing
    """
    print("=" * 60)
    print("   GENERATE SAMPLE DATA - Logbook Teknik Geofisika")
    print("=" * 60)
    
    # Reinitialize database
    db.init_database()
    print("\n✓ Database initialized")
    
    # Generate proyek
    project_ids = _generate_projects()
    
    # Generate aktivitas
    activity_count = _generate_activities(project_ids)
    
    # Tampilkan ringkasan
    _print_summary()
    
    print("\n" + "=" * 60)
    print("   Jalankan aplikasi dengan perintah:")
    print("   $ streamlit run app.py")
    print("=" * 60)


def _generate_projects() -> list:
    """
    Generate proyek-proyek contoh.
    
    Returns:
        list: Daftar ID proyek yang dibuat
    """
    print("\n📁 Membuat proyek...")
    project_ids = []
    
    for index, project_info in enumerate(SAMPLE_PROJECTS):
        # Buat proyek
        project_id = db.create_project(
            project_info["name"],
            project_info["description"],
            project_info["estimated_hours"],
            project_info["category"]
        )
        project_ids.append(project_id)
        
        # Update status untuk variasi
        if index == 3:  # Proyek ke-4 selesai
            db.update_project_status(project_id, "completed")
        elif index == 5:  # Proyek ke-6 ditunda
            db.update_project_status(project_id, "paused")
        
        # Tampilkan progress
        status_icon = "✓" if index not in [3, 5] else "○"
        print(f"   {status_icon} {project_info['name'][:45]}...")
    
    return project_ids


def _generate_activities(project_ids: list) -> int:
    """
    Generate aktivitas-aktivitas contoh.
    
    Args:
        project_ids: Daftar ID proyek yang tersedia
    
    Returns:
        int: Jumlah aktivitas yang dibuat
    """
    print("\n⏱️  Membuat aktivitas...")
    
    start_date = datetime.now() - timedelta(days=30)
    activity_count = 0
    
    # Generate aktivitas untuk 31 hari
    for day_offset in range(31):
        current_date = start_date + timedelta(days=day_offset)
        
        # Skip weekend dengan probabilitas 70%
        if current_date.weekday() >= 5 and random.random() > 0.3:
            continue
        
        # 1-4 aktivitas per hari
        num_activities = random.randint(1, 4)
        day_start_hour = 8
        
        for _ in range(num_activities):
            # Pilih proyek (proyek awal lebih sering)
            weights = [3, 3, 2, 2, 1, 1]
            project_index = random.choices(
                range(len(project_ids)), 
                weights=weights[:len(project_ids)]
            )[0]
            project_id = project_ids[project_index]
            
            # Generate waktu
            start_hour = day_start_hour + random.randint(0, 2)
            start_minute = random.randint(0, 59)
            duration_hours = round(random.uniform(0.5, 4.0), 1)
            
            # Buat datetime
            start_time = current_date.replace(
                hour=min(start_hour, 17),
                minute=start_minute,
                second=0,
                microsecond=0
            )
            end_time = start_time + timedelta(hours=duration_hours)
            
            # Buat aktivitas
            try:
                db.create_activity(
                    project_id,
                    start_time,
                    end_time,
                    random.choice(SAMPLE_NOTES)
                )
                activity_count += 1
            except ValueError:
                # Skip jika validasi gagal
                pass
            
            # Update jam mulai berikutnya
            day_start_hour = end_time.hour + 1
            
            # Jangan lebih dari jam 6 sore
            if day_start_hour >= 18:
                break
    
    print(f"   ✓ {activity_count} aktivitas berhasil dibuat")
    
    # Tambahkan aktivitas ongoing
    _add_ongoing_activity(project_ids[0])
    
    return activity_count


def _add_ongoing_activity(project_id: int):
    """
    Menambahkan aktivitas yang sedang berjalan.
    
    Args:
        project_id: ID proyek untuk aktivitas ongoing
    """
    try:
        db.create_activity(
            project_id,
            datetime.now() - timedelta(hours=1, minutes=30),
            None,  # Belum selesai
            "Sedang mengerjakan QC data seismik"
        )
        print("   ✓ 1 aktivitas ongoing ditambahkan")
    except Exception as e:
        print(f"   ⚠ Gagal menambah aktivitas ongoing: {e}")


def _print_summary():
    """
    Menampilkan ringkasan data yang dibuat.
    """
    print("\n" + "=" * 60)
    print("   RINGKASAN DATA")
    print("=" * 60)
    
    stats = db.get_overall_statistics()
    
    print(f"\n   Total Proyek       : {stats['total_projects']}")
    print(f"   Proyek Aktif       : {stats['active_projects']}")
    print(f"   Total Aktivitas    : {stats['total_activities']}")
    print(f"   Total Jam Kerja    : {stats['total_hours']:.1f} jam")
    print(f"   Aktivitas Ongoing  : {stats['ongoing_activities']}")
    print(f"   Hari Aktif         : {stats['active_days']}")
    print(f"   Rata-rata/Hari     : {stats['avg_hours_per_day']:.1f} jam")
    
    print("\n✅ Sample data berhasil dibuat!")


# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    generate_sample_data()
