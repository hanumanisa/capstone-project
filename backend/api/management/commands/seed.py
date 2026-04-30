from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from api.models import (
    Directorate, Division, Employee, Profile, 
    CourseCategory, Course, Hotel, Vendor, TnaPeriod, TnaMaster, TnaParticipant,
    TrainingMaster, TrainingEvent, EventLocation, EventSchedule
)


class Command(BaseCommand):
    help = 'Seeds the database with groups, superuser, company structure, employees, course categories, courses, and hotels.'

    def handle(self, *args, **kwargs):
        # Group roles
        group_names = [
            'Super Administrator',
            'Administrator',
            'Dean',
            'Head of Division',
            'Team Leader',
            'Employee'
        ]

        self.stdout.write('Seeding Groups...')
        for name in group_names:
            group, created = Group.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created group: {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'  [SKIP] Group already exists: {name}'))

        # Super user
        self.stdout.write('\nSeeding Superuser...')
        username = 'hanumanisa0905@gmail.com'
        email = 'hanumanisa0905@gmail.com'
        password = 'Hanum955955'

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_superuser(username=username, email=email, password=password)
            super_admin_group = Group.objects.get(name='Super Administrator')
            user.groups.add(super_admin_group)
            self.stdout.write(self.style.SUCCESS(f'  [OK] Created superuser: {username}'))
        else:
            self.stdout.write(self.style.WARNING(f'  [SKIP] Superuser already exists: {username}'))

        # Seeding Data

        self.stdout.write('\nSeeding Directorates...')
        directorates_data = [
            {'id': 1, 'name': 'Direktorat Utama'},
            {'id': 2, 'name': 'Direktorat Manajemen Risiko'},
            {'id': 3, 'name': 'Direktorat Operasional dan Keuangan'},
            {'id': 4, 'name': 'Direktorat Pembiayaan dan Investasi'},
            {'id': 5, 'name': 'Direktorat Pembiayaan Publik dan Pengembangan Proyek'}
        ]

        for d_data in directorates_data:
            obj, created = Directorate.objects.get_or_create(
                directorate_id=d_data['id'],
                defaults={'directorate_name': d_data['name']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  [OK] Created Directorate: {d_data['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"  [SKIP] Directorate already exists: {d_data['name']}"))

     
        self.stdout.write('\nSeeding Divisions...')
        divisions_data = [
            {"id": "DAAA22", "name": "Divisi Akuntansi Administrasi Aset", "dir_id": 3},
            {"id": "DAI22", "name": "Divisi Audit Internal", "dir_id": 1},
            {"id": "DELST22", "name": "Divisi Evaluasi Lingkungan Sosial & Teknik", "dir_id": 2},
            {"id": "DEPI22", "name": "Divisi Evaluasi Pembiayaan dan Investasi", "dir_id": 2},
            {"id": "DH22", "name": "Divisi Hukum", "dir_id": 2},
            {"id": "DJK22", "name": "Divisi Jasa Konsultasi", "dir_id": 4},
            {"id": "DK22", "name": "Divisi Kepatuhan", "dir_id": 2},
            {"id": "DKHI22", "name": "Divisi Keuangan & Hubungan Investor", "dir_id": 3},
            {"id": "DMRT22", "name": "Divisi Manajemen Risiko Terintegrasi", "dir_id": 2},
            {"id": "DP122", "name": "Divisi Pembiayaan 1", "dir_id": 4},
            {"id": "DP222", "name": "Divisi Pembiayaan 2", "dir_id": 4},
            {"id": "DPB22", "name": "Divisi Pembiayaan Berkelanjutan", "dir_id": 4},
            {"id": "DPKMI22", "name": "Divisi Pengembangan Korporasi & Manajemen Inisiatif", "dir_id": 1},
            {"id": "DPM22", "name": "Divisi Penyertaan Modal", "dir_id": 4},
            {"id": "DPOP22", "name": "Divisi Pengelolaan Operasional Pembiayaan", "dir_id": 3},
            {"id": "DPP122", "name": "Divisi Pembiayaan Publik 1", "dir_id": 5},
            {"id": "DPP222", "name": "Divisi Pembiayaan Publik 2", "dir_id": 5},
            {"id": "DPP322", "name": "Divisi Pembiayaan Publik 3", "dir_id": 5},
            {"id": "DPPK22", "name": "Divisi Pengelolaan Pembiayaan & Investasi Khusus", "dir_id": 2},
            {"id": "DPPRO22", "name": "Divisi Pengembangan Proyek", "dir_id": 5},
            {"id": "DRE22", "name": "Divisi Riset Ekonomi", "dir_id": 1},
            {"id": "DSDM22", "name": "Divisi Sumber Daya Manusia", "dir_id": 1},
            {"id": "DSP22", "name": "Divisi Sekretariat Perusahaan", "dir_id": 1},
            {"id": "DTI22", "name": "Divisi Teknologi Informasi", "dir_id": 3},
            {"id": "DUP22", "name": "Divisi Umum & Pengadaan", "dir_id": 3},
            {"id": "DUS22", "name": "Divisi Usaha Syariah", "dir_id": 4}
        ]

        for div in divisions_data:
            try:
                directorate_instance = Directorate.objects.get(directorate_id=div['dir_id'])
                obj, created = Division.objects.get_or_create(
                    division_id=div['id'],
                    defaults={
                        'division_name': div['name'],
                        'directorate': directorate_instance
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  [OK] Created Division: {div['name']}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  [SKIP] Division already exists: {div['name']}"))
            except Directorate.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"  [ERROR] Cannot create Division {div['name']} - Directorate {div['dir_id']} missing!"))


        self.stdout.write('\nSeeding Employees...')

        # Position mapping
        POSITION_MAP = {
            'KD221': 'Kepala Divisi',
            'TL222': 'Team Leader',
            'STF221': 'Staff',
            'STF222': 'Staff',
            'STF223': 'Staff',
            'STF224': 'Staff',
        }

        employees_data = [
            (200001, "Hendra Wijaya Permata", "DAAA22", "KD221", 200001, "Strategy Analyst", "Manajerial Executive", "Pria", "hendra.permata1@ptsmi.co.id", "6287700000001", "Universitas Hasanuddin", "Manajemen", "2026-04-05", "Karyawan Kontrak"),
            (200002, "Nanda Kusuma Gunawan", "DAAA22", "TL222", 200001, "Business Analyst", "Manajerial Senior", "Pria", "nanda.gunawan2@ptsmi.co.id", "6287700000002", "Universitas Hasanuddin", "Manajemen", "2026-04-04", "Karyawan Kontrak"),
            (200003, "Taufik Ramadhan Wibowo", "DAAA22", "TL222", 200001, "Strategy Analyst", "Manajerial Senior", "Pria", "taufik.wibowo3@ptsmi.co.id", "6287700000003", "Binus University", "Statistika", "2026-04-03", "Karyawan Kontrak"),
            (200004, "Bagas Kurniawan Pratama", "DAAA22", "STF221", 200002, "Business Analyst", "Manajerial Madya", "Pria", "bagas.pratama4@ptsmi.co.id", "6287700000004", "Universitas Sebelas Maret", "Ekonomi", "2026-04-02", "Karyawan Kontrak"),
            (200005, "Farhan Lestari Utama", "DAAA22", "STF222", 200002, "Business Analyst", "Manajerial Senior", "Pria", "farhan.utama5@ptsmi.co.id", "6287700000005", "Universitas Andalas", "Ekonomi", "2026-04-01", "Karyawan Kontrak"),
            (200006, "Dewi Wijaya Kurniawan", "DAAA22", "STF223", 200002, "Operation Analyst", "Manajerial Junior", "Wanita", "dewi.kurniawan6@ptsmi.co.id", "6287700000006", "Universitas Brawijaya", "Bisnis", "2026-03-31", "Karyawan Kontrak"),
            (200007, "Indah Kusuma Prasetyo", "DAAA22", "STF224", 200002, "Business Analyst", "Manajerial Madya", "Wanita", "indah.prasetyo7@ptsmi.co.id", "6287700000007", "Universitas Gadjah Mada", "Manajemen", "2026-03-30", "Karyawan Tetap"),
            (200008, "Putri Ramadhan Hidayat", "DAAA22", "STF221", 200002, "Business Analyst", "Manajerial Senior", "Wanita", "putri.hidayat8@ptsmi.co.id", "6287700000008", "Universitas Diponegoro", "Ekonomi", "2026-03-29", "Karyawan Tetap"),
            (200009, "Yuni Kurniawan Siregar", "DAAA22", "STF222", 200002, "Strategy Analyst", "Manajerial Junior", "Wanita", "yuni.siregar9@ptsmi.co.id", "6287700000009", "Universitas Airlangga", "Bisnis", "2026-03-28", "Karyawan Tetap"),
            (200010, "Budi Lestari Susanto", "DAAA22", "STF223", 200002, "Operation Analyst", "Manajerial Madya", "Pria", "budi.susanto10@ptsmi.co.id", "6287700000010", "Universitas Gadjah Mada", "Statistika", "2026-03-27", "Karyawan Tetap"),
            (200011, "Joko Wijaya Wijaya", "DAAA22", "STF224", 200002, "Operation Analyst", "Manajerial Senior", "Pria", "joko.wijaya11@ptsmi.co.id", "6287700000011", "Universitas Mercu Buana", "Manajemen", "2026-03-26", "Karyawan Tetap"),
            (200012, "Oka Kusuma Mahendra", "DAAA22", "STF221", 200002, "Strategy Analyst", "Manajerial Junior", "Pria", "oka.mahendra12@ptsmi.co.id", "6287700000012", "Universitas Diponegoro", "Manajemen", "2026-03-25", "Karyawan Tetap"),
            (200013, "Wahyu Ramadhan Purnama", "DAAA22", "STF222", 200002, "Strategy Analyst", "Manajerial Madya", "Pria", "wahyu.purnama13@ptsmi.co.id", "6287700000013", "Universitas Brawijaya", "Manajemen", "2026-03-24", "Karyawan Tetap"),
            (200014, "Chandra Kurniawan Ananda", "DAAA22", "STF223", 200002, "Business Analyst", "Manajerial Senior", "Pria", "chandra.ananda14@ptsmi.co.id", "6287700000014", "Universitas Negeri Jakarta", "Statistika", "2026-03-23", "Karyawan Tetap"),
            (200015, "Galih Lestari Lestari", "DAAA22", "STF224", 200002, "Business Analyst", "Manajerial Junior", "Pria", "galih.lestari15@ptsmi.co.id", "6287700000015", "Universitas Airlangga", "Ekonomi", "2026-03-22", "Karyawan Tetap"),
            (200016, "Citra Wijaya Ramadhan", "DAAA22", "STF221", 200002, "Strategy Analyst", "Manajerial Madya", "Wanita", "citra.ramadhan16@ptsmi.co.id", "6287700000016", "Telkom University", "Bisnis", "2026-03-21", "Karyawan Tetap"),
            (200017, "Kartika Kusuma Hartono", "DAAA22", "STF222", 200002, "Strategy Analyst", "Manajerial Senior", "Wanita", "kartika.hartono17@ptsmi.co.id", "6287700000017", "Universitas Airlangga", "Bisnis", "2026-03-20", "Karyawan Tetap"),
            (200018, "Sari Ramadhan Saputra", "DAAA22", "STF223", 200002, "Business Analyst", "Manajerial Junior", "Wanita", "sari.saputra18@ptsmi.co.id", "6287700000018", "Universitas Gadjah Mada", "Manajemen", "2026-03-19", "Karyawan Tetap"),
            (200019, "Aulia Kurniawan Kusuma", "DAAA22", "STF224", 200002, "Operation Analyst", "Manajerial Madya", "Wanita", "aulia.kusuma19@ptsmi.co.id", "6287700000019", "Binus University", "Ekonomi", "2026-03-18", "Karyawan Tetap"),
            (200020, "Fajar Lestari Handoko", "DAAA22", "STF221", 200002, "Business Analyst", "Manajerial Senior", "Pria", "fajar.handoko20@ptsmi.co.id", "6287700000020", "Telkom University", "Bisnis", "2026-03-17", "Karyawan Tetap"),
            (200021, "Lukman Wijaya Syahputra", "DAAA22", "STF222", 200002, "Business Analyst", "Manajerial Junior", "Pria", "lukman.syahputra21@ptsmi.co.id", "6287700000021", "Universitas Gunadarma", "Bisnis", "2026-03-16", "Karyawan Tetap"),
            (200022, "Rizky Kusuma Nugroho", "DAI22", "KD221", 200022, "Operation Analyst", "Manajerial Executive", "Pria", "rizky.nugroho22@ptsmi.co.id", "6287700000022", "Universitas Indonesia", "Statistika", "2026-03-15", "Karyawan Tetap"),
            (200023, "Zaki Ramadhan Firmansyah", "DAI22", "TL222", 200022, "Strategy Analyst", "Manajerial Senior", "Pria", "zaki.firmansyah23@ptsmi.co.id", "6287700000023", "Universitas Indonesia", "Manajemen", "2026-03-14", "Karyawan Tetap"),
            (200024, "Dimas Kurniawan Febrianto", "DAI22", "TL222", 200022, "Operation Analyst", "Manajerial Senior", "Pria", "dimas.febrianto24@ptsmi.co.id", "6287700000024", "Universitas Padjadjaran", "Manajemen", "2026-03-13", "Karyawan Tetap"),
            (200025, "Hafiz Lestari Putri", "DAI22", "STF221", 200023, "Business Analyst", "Manajerial Madya", "Pria", "hafiz.putri25@ptsmi.co.id", "6287700000025", "Universitas Gadjah Mada", "Manajemen", "2026-03-12", "Karyawan Tetap"),
            (200026, "Gita Wijaya Permata", "DAI22", "STF222", 200023, "Operation Analyst", "Manajerial Senior", "Wanita", "gita.permata26@ptsmi.co.id", "6287700000026", "Universitas Brawijaya", "Statistika", "2026-03-11", "Karyawan Tetap"),
            (200027, "Maya Kusuma Gunawan", "DAI22", "STF223", 200023, "Strategy Analyst", "Manajerial Junior", "Wanita", "maya.gunawan27@ptsmi.co.id", "6287700000027", "Institut Teknologi Bandung", "Statistika", "2026-03-10", "Karyawan Tetap"),
            (200028, "Vina Ramadhan Wibowo", "DAI22", "STF224", 200023, "Operation Analyst", "Manajerial Madya", "Wanita", "vina.wibowo28@ptsmi.co.id", "6287700000028", "Universitas Padjadjaran", "Statistika", "2026-03-09", "Karyawan Tetap"),
            (200029, "Andi Kurniawan Pratama", "DAI22", "STF221", 200023, "Business Analyst", "Manajerial Senior", "Pria", "andi.pratama29@ptsmi.co.id", "6287700000029", "Universitas Airlangga", "Ekonomi", "2026-03-08", "Karyawan Tetap"),
            (200030, "Hendra Lestari Utama", "DAI22", "STF222", 200023, "Operation Analyst", "Manajerial Junior", "Pria", "hendra.utama30@ptsmi.co.id", "6287700000030", "Institut Teknologi Bandung", "Bisnis", "2026-03-07", "Karyawan Tetap"),
            (200031, "Nanda Wijaya Kurniawan", "DAI22", "STF223", 200023, "Strategy Analyst", "Manajerial Madya", "Pria", "nanda.kurniawan31@ptsmi.co.id", "6287700000031", "Universitas Mercu Buana", "Statistika", "2026-03-06", "Karyawan Tetap"),
            (200032, "Taufik Kusuma Prasetyo", "DAI22", "STF224", 200023, "Strategy Analyst", "Manajerial Senior", "Pria", "taufik.prasetyo32@ptsmi.co.id", "6287700000032", "Universitas Padjadjaran", "Bisnis", "2026-03-05", "Karyawan Tetap"),
            (200033, "Bagas Ramadhan Hidayat", "DELST22", "KD221", 200033, "Strategy Analyst", "Manajerial Executive", "Pria", "bagas.hidayat33@ptsmi.co.id", "6287700000033", "Telkom University", "Bisnis", "2026-03-04", "Karyawan Tetap"),
            (200034, "Farhan Kurniawan Siregar", "DELST22", "TL222", 200033, "Operation Analyst", "Manajerial Senior", "Pria", "farhan.siregar34@ptsmi.co.id", "6287700000034", "Universitas Brawijaya", "Statistika", "2026-03-03", "Karyawan Tetap"),
            (200035, "Dewi Lestari Susanto", "DELST22", "TL222", 200033, "Business Analyst", "Manajerial Senior", "Wanita", "dewi.susanto35@ptsmi.co.id", "6287700000035", "Institut Teknologi Bandung", "Administrasi", "2026-03-02", "Karyawan Tetap"),
            (200036, "Indah Wijaya Wijaya", "DELST22", "STF221", 200034, "Operation Analyst", "Manajerial Madya", "Wanita", "indah.wijaya36@ptsmi.co.id", "6287700000036", "Universitas Gadjah Mada", "Statistika", "2026-03-01", "Karyawan Tetap"),
            (200037, "Putri Kusuma Mahendra", "DELST22", "STF222", 200034, "Strategy Analyst", "Manajerial Senior", "Wanita", "putri.mahendra37@ptsmi.co.id", "6287700000037", "Universitas Indonesia", "Statistika", "2026-02-28", "Karyawan Tetap"),
            (200038, "Yuni Ramadhan Purnama", "DELST22", "STF223", 200034, "Operation Analyst", "Manajerial Junior", "Wanita", "yuni.purnama38@ptsmi.co.id", "6287700000038", "Universitas Padjadjaran", "Statistika", "2026-02-27", "Karyawan Tetap"),
            (200039, "Budi Kurniawan Ananda", "DELST22", "STF224", 200034, "Business Analyst", "Manajerial Madya", "Pria", "budi.ananda39@ptsmi.co.id", "6287700000039", "Universitas Padjadjaran", "Manajemen", "2026-02-26", "Karyawan Tetap"),
            (200040, "Joko Lestari Lestari", "DELST22", "STF221", 200034, "Strategy Analyst", "Manajerial Senior", "Pria", "joko.lestari40@ptsmi.co.id", "6287700000040", "Universitas Mercu Buana", "Ekonomi", "2026-02-25", "Karyawan Tetap"),
            (200041, "Oka Wijaya Ramadhan", "DELST22", "STF222", 200034, "Operation Analyst", "Manajerial Junior", "Pria", "oka.ramadhan41@ptsmi.co.id", "6287700000041", "Universitas Negeri Jakarta", "Statistika", "2026-02-24", "Karyawan Tetap"),
            (200042, "Wahyu Kusuma Hartono", "DELST22", "STF223", 200034, "Operation Analyst", "Manajerial Madya", "Pria", "wahyu.hartono42@ptsmi.co.id", "6287700000042", "Universitas Hasanuddin", "Manajemen", "2026-02-23", "Karyawan Tetap"),
            (200043, "Chandra Ramadhan Saputra", "DELST22", "STF224", 200034, "Business Analyst", "Manajerial Senior", "Pria", "chandra.saputra43@ptsmi.co.id", "6287700000043", "Universitas Sebelas Maret", "Administrasi", "2026-02-22", "Karyawan Tetap"),
            (200044, "Galih Kurniawan Kusuma", "DELST22", "STF221", 200034, "Business Analyst", "Manajerial Junior", "Pria", "galih.kusuma44@ptsmi.co.id", "6287700000044", "Universitas Gunadarma", "Administrasi", "2026-02-21", "Karyawan Tetap"),
            (200045, "Citra Lestari Handoko", "DELST22", "STF222", 200034, "Strategy Analyst", "Manajerial Madya", "Wanita", "citra.handoko45@ptsmi.co.id", "6287700000045", "Binus University", "Statistika", "2026-02-20", "Karyawan Tetap"),
            (200046, "Kartika Wijaya Syahputra", "DELST22", "STF223", 200034, "Operation Analyst", "Manajerial Senior", "Wanita", "kartika.syahputra46@ptsmi.co.id", "6287700000046", "Universitas Hasanuddin", "Administrasi", "2026-02-19", "Karyawan Tetap"),
            (200047, "Sari Kusuma Nugroho", "DELST22", "STF224", 200034, "Business Analyst", "Manajerial Junior", "Wanita", "sari.nugroho47@ptsmi.co.id", "6287700000047", "Universitas Indonesia", "Administrasi", "2026-02-18", "Karyawan Tetap"),
            (200048, "Aulia Ramadhan Firmansyah", "DELST22", "STF221", 200034, "Business Analyst", "Manajerial Madya", "Wanita", "aulia.firmansyah48@ptsmi.co.id", "6287700000048", "Universitas Sebelas Maret", "Statistika", "2026-02-17", "Karyawan Tetap"),
            (200049, "Fajar Kurniawan Febrianto", "DELST22", "STF222", 200034, "Strategy Analyst", "Manajerial Senior", "Pria", "fajar.febrianto49@ptsmi.co.id", "6287700000049", "Institut Teknologi Bandung", "Ekonomi", "2026-02-16", "Karyawan Tetap"),
            (200050, "Lukman Lestari Putri", "DELST22", "STF223", 200034, "Business Analyst", "Manajerial Junior", "Pria", "lukman.putri50@ptsmi.co.id", "6287700000050", "Universitas Andalas", "Manajemen", "2026-02-15", "Karyawan Tetap"),
            (200051, "Rizky Wijaya Permata", "DELST22", "STF224", 200034, "Business Analyst", "Manajerial Madya", "Pria", "rizky.permata51@ptsmi.co.id", "6287700000051", "Universitas Gunadarma", "Manajemen", "2026-02-14", "Karyawan Tetap"),
            (200052, "Zaki Kusuma Gunawan", "DELST22", "STF221", 200034, "Operation Analyst", "Manajerial Senior", "Pria", "zaki.gunawan52@ptsmi.co.id", "6287700000052", "Universitas Sebelas Maret", "Ekonomi", "2026-02-13", "Karyawan Tetap"),
            (200053, "Dimas Ramadhan Wibowo", "DEPI22", "KD221", 200053, "Strategy Analyst", "Manajerial Executive", "Pria", "dimas.wibowo53@ptsmi.co.id", "6287700000053", "Binus University", "Statistika", "2026-02-12", "Karyawan Tetap"),
            (200054, "Hafiz Kurniawan Pratama", "DEPI22", "TL222", 200053, "Operation Analyst", "Manajerial Senior", "Pria", "hafiz.pratama54@ptsmi.co.id", "6287700000054", "Universitas Indonesia", "Manajemen", "2026-02-11", "Karyawan Tetap"),
            (200055, "Gita Lestari Utama", "DEPI22", "TL222", 200053, "Operation Analyst", "Manajerial Senior", "Wanita", "gita.utama55@ptsmi.co.id", "6287700000055", "Universitas Airlangga", "Bisnis", "2026-02-10", "Karyawan Tetap"),
            (200056, "Maya Wijaya Kurniawan", "DEPI22", "STF221", 200054, "Operation Analyst", "Manajerial Madya", "Wanita", "maya.kurniawan56@ptsmi.co.id", "6287700000056", "Universitas Mercu Buana", "Manajemen", "2026-02-09", "Karyawan Tetap"),
            (200057, "Vina Kusuma Prasetyo", "DEPI22", "STF222", 200054, "Business Analyst", "Manajerial Senior", "Wanita", "vina.prasetyo57@ptsmi.co.id", "6287700000057", "Universitas Gunadarma", "Ekonomi", "2026-02-08", "Karyawan Tetap"),
            (200058, "Andi Ramadhan Hidayat", "DEPI22", "STF223", 200054, "Business Analyst", "Manajerial Junior", "Pria", "andi.hidayat58@ptsmi.co.id", "6287700000058", "Telkom University", "Manajemen", "2026-02-07", "Karyawan Tetap"),
            (200059, "Hendra Kurniawan Siregar", "DEPI22", "STF224", 200054, "Business Analyst", "Manajerial Madya", "Pria", "hendra.siregar59@ptsmi.co.id", "6287700000059", "Universitas Gunadarma", "Statistika", "2026-02-06", "Karyawan Tetap"),
            (200060, "Nanda Lestari Susanto", "DEPI22", "STF221", 200054, "Operation Analyst", "Manajerial Senior", "Pria", "nanda.susanto60@ptsmi.co.id", "6287700000060", "Universitas Gunadarma", "Statistika", "2026-02-05", "Karyawan Tetap"),
            (200061, "Taufik Wijaya Wijaya", "DEPI22", "STF222", 200054, "Operation Analyst", "Manajerial Junior", "Pria", "taufik.wijaya61@ptsmi.co.id", "6287700000061", "Binus University", "Ekonomi", "2026-02-04", "Karyawan Tetap"),
            (200062, "Bagas Kusuma Mahendra", "DEPI22", "STF223", 200054, "Strategy Analyst", "Manajerial Madya", "Pria", "bagas.mahendra62@ptsmi.co.id", "6287700000062", "Universitas Gadjah Mada", "Bisnis", "2026-02-03", "Karyawan Tetap"),
            (200063, "Farhan Ramadhan Purnama", "DEPI22", "STF224", 200054, "Business Analyst", "Manajerial Senior", "Pria", "farhan.purnama63@ptsmi.co.id", "6287700000063", "Universitas Airlangga", "Manajemen", "2026-02-02", "Karyawan Tetap"),
            (200064, "Dewi Kurniawan Ananda", "DEPI22", "STF221", 200054, "Operation Analyst", "Manajerial Junior", "Wanita", "dewi.ananda64@ptsmi.co.id", "6287700000064", "Institut Teknologi Bandung", "Statistika", "2026-02-01", "Karyawan Tetap"),
            (200065, "Indah Lestari Lestari", "DEPI22", "STF222", 200054, "Business Analyst", "Manajerial Madya", "Wanita", "indah.lestari65@ptsmi.co.id", "6287700000065", "Institut Teknologi Bandung", "Statistika", "2026-01-31", "Karyawan Tetap"),
            (200066, "Putri Wijaya Ramadhan", "DEPI22", "STF223", 200054, "Business Analyst", "Manajerial Senior", "Wanita", "putri.ramadhan66@ptsmi.co.id", "6287700000066", "Telkom University", "Statistika", "2026-01-30", "Karyawan Tetap"),
            (200067, "Yuni Kusuma Hartono", "DEPI22", "STF224", 200054, "Operation Analyst", "Manajerial Junior", "Wanita", "yuni.hartono67@ptsmi.co.id", "6287700000067", "Universitas Gadjah Mada", "Statistika", "2026-01-29", "Karyawan Tetap"),
            (200068, "Budi Ramadhan Saputra", "DH22", "KD221", 200068, "Business Analyst", "Manajerial Executive", "Pria", "budi.saputra68@ptsmi.co.id", "6287700000068", "Universitas Padjadjaran", "Statistika", "2026-01-28", "Karyawan Tetap"),
            (200069, "Joko Kurniawan Kusuma", "DH22", "TL222", 200068, "Strategy Analyst", "Manajerial Senior", "Pria", "joko.kusuma69@ptsmi.co.id", "6287700000069", "Universitas Sebelas Maret", "Statistika", "2026-01-27", "Karyawan Tetap"),
            (200070, "Oka Lestari Handoko", "DH22", "TL222", 200068, "Strategy Analyst", "Manajerial Senior", "Pria", "oka.handoko70@ptsmi.co.id", "6287700000070", "Universitas Hasanuddin", "Manajemen", "2026-01-26", "Karyawan Tetap"),
            (200071, "Wahyu Wijaya Syahputra", "DH22", "STF221", 200069, "Strategy Analyst", "Manajerial Madya", "Pria", "wahyu.syahputra71@ptsmi.co.id", "6287700000071", "Telkom University", "Administrasi", "2026-01-25", "Karyawan Tetap"),
            (200072, "Chandra Kusuma Nugroho", "DH22", "STF222", 200069, "Operation Analyst", "Manajerial Senior", "Pria", "chandra.nugroho72@ptsmi.co.id", "6287700000072", "Universitas Padjadjaran", "Manajemen", "2026-01-24", "Karyawan Tetap"),
            (200073, "Galih Ramadhan Firmansyah", "DH22", "STF223", 200069, "Strategy Analyst", "Manajerial Junior", "Pria", "galih.firmansyah73@ptsmi.co.id", "6287700000073", "Universitas Andalas", "Statistika", "2026-01-23", "Karyawan Tetap"),
            (200074, "Citra Kurniawan Febrianto", "DH22", "STF224", 200069, "Business Analyst", "Manajerial Madya", "Wanita", "citra.febrianto74@ptsmi.co.id", "6287700000074", "Universitas Airlangga", "Bisnis", "2026-01-22", "Karyawan Tetap"),
            (200075, "Kartika Lestari Putri", "DH22", "STF221", 200069, "Operation Analyst", "Manajerial Senior", "Wanita", "kartika.putri75@ptsmi.co.id", "6287700000075", "Universitas Indonesia", "Bisnis", "2026-01-21", "Karyawan Tetap"),
            (200076, "Sari Wijaya Permata", "DH22", "STF222", 200069, "Operation Analyst", "Manajerial Junior", "Wanita", "sari.permata76@ptsmi.co.id", "6287700000076", "Universitas Hasanuddin", "Ekonomi", "2026-01-20", "Karyawan Tetap"),
            (200077, "Aulia Kusuma Gunawan", "DH22", "STF223", 200069, "Business Analyst", "Manajerial Madya", "Wanita", "aulia.gunawan77@ptsmi.co.id", "6287700000077", "Telkom University", "Administrasi", "2026-01-19", "Karyawan Tetap"),
            (200078, "Fajar Ramadhan Wibowo", "DH22", "STF224", 200069, "Operation Analyst", "Manajerial Senior", "Pria", "fajar.wibowo78@ptsmi.co.id", "6287700000078", "Universitas Mercu Buana", "Administrasi", "2026-01-18", "Karyawan Tetap"),
            (200079, "Lukman Kurniawan Pratama", "DH22", "STF221", 200069, "Operation Analyst", "Manajerial Junior", "Pria", "lukman.pratama79@ptsmi.co.id", "6287700000079", "Universitas Mercu Buana", "Ekonomi", "2026-01-17", "Karyawan Tetap"),
            (200080, "Rizky Lestari Utama", "DH22", "STF222", 200069, "Business Analyst", "Manajerial Madya", "Pria", "rizky.utama80@ptsmi.co.id", "6287700000080", "Universitas Brawijaya", "Administrasi", "2026-01-16", "Karyawan Tetap"),
            (200081, "Zaki Wijaya Kurniawan", "DH22", "STF223", 200069, "Strategy Analyst", "Manajerial Senior", "Pria", "zaki.kurniawan81@ptsmi.co.id", "6287700000081", "Universitas Brawijaya", "Statistika", "2026-01-15", "Karyawan Tetap"),
            (200082, "Dimas Kusuma Prasetyo", "DH22", "STF224", 200069, "Strategy Analyst", "Manajerial Junior", "Pria", "dimas.prasetyo82@ptsmi.co.id", "6287700000082", "Universitas Andalas", "Ekonomi", "2026-01-14", "Karyawan Tetap"),
            (200083, "Hafiz Ramadhan Hidayat", "DH22", "STF221", 200069, "Business Analyst", "Manajerial Madya", "Pria", "hafiz.hidayat83@ptsmi.co.id", "6287700000083", "Telkom University", "Statistika", "2026-01-13", "Karyawan Tetap"),
            (200084, "Gita Kurniawan Siregar", "DH22", "STF222", 200069, "Operation Analyst", "Manajerial Senior", "Wanita", "gita.siregar84@ptsmi.co.id", "6287700000084", "Institut Teknologi Bandung", "Manajemen", "2026-01-12", "Karyawan Tetap"),
            (200085, "Maya Lestari Susanto", "DH22", "STF223", 200069, "Business Analyst", "Manajerial Junior", "Wanita", "maya.susanto85@ptsmi.co.id", "6287700000085", "Universitas Diponegoro", "Manajemen", "2026-01-11", "Karyawan Tetap"),
            (200086, "Vina Wijaya Wijaya", "DH22", "STF224", 200069, "Business Analyst", "Manajerial Madya", "Wanita", "vina.wijaya86@ptsmi.co.id", "6287700000086", "Universitas Andalas", "Statistika", "2026-01-10", "Karyawan Tetap"),
            (200087, "Andi Kusuma Mahendra", "DH22", "STF221", 200069, "Business Analyst", "Manajerial Senior", "Pria", "andi.mahendra87@ptsmi.co.id", "6287700000087", "Universitas Andalas", "Statistika", "2026-01-09", "Karyawan Tetap"),
            (200088, "Hendra Ramadhan Purnama", "DH22", "STF222", 200069, "Business Analyst", "Manajerial Junior", "Pria", "hendra.purnama88@ptsmi.co.id", "6287700000088", "Universitas Padjadjaran", "Ekonomi", "2026-01-08", "Karyawan Tetap"),
            (200089, "Nanda Kurniawan Ananda", "DH22", "STF223", 200069, "Business Analyst", "Manajerial Madya", "Pria", "nanda.ananda89@ptsmi.co.id", "6287700000089", "Universitas Padjadjaran", "Ekonomi", "2026-01-07", "Karyawan Tetap"),
            (200090, "Taufik Lestari Lestari", "DH22", "STF224", 200069, "Operation Analyst", "Manajerial Senior", "Pria", "taufik.lestari90@ptsmi.co.id", "6287700000090", "Universitas Negeri Jakarta", "Administrasi", "2026-01-06", "Karyawan Tetap"),
            (200091, "Bagas Wijaya Ramadhan", "DH22", "STF221", 200069, "Operation Analyst", "Manajerial Junior", "Pria", "bagas.ramadhan91@ptsmi.co.id", "6287700000091", "Universitas Indonesia", "Ekonomi", "2026-01-05", "Karyawan Tetap"),
            (200092, "Farhan Kusuma Hartono", "DH22", "STF222", 200069, "Operation Analyst", "Manajerial Madya", "Pria", "farhan.hartono92@ptsmi.co.id", "6287700000092", "Binus University", "Ekonomi", "2026-01-04", "Karyawan Tetap"),
            (200093, "Dewi Ramadhan Saputra", "DH22", "STF223", 200069, "Business Analyst", "Manajerial Senior", "Wanita", "dewi.saputra93@ptsmi.co.id", "6287700000093", "Binus University", "Bisnis", "2026-01-03", "Karyawan Tetap"),
            (200094, "Indah Kurniawan Kusuma", "DJK22", "KD221", 200094, "Operation Analyst", "Manajerial Executive", "Wanita", "indah.kusuma94@ptsmi.co.id", "6287700000094", "Universitas Gunadarma", "Manajemen", "2026-01-02", "Karyawan Tetap"),
            (200095, "Putri Lestari Handoko", "DJK22", "TL222", 200094, "Business Analyst", "Manajerial Senior", "Wanita", "putri.handoko95@ptsmi.co.id", "6287700000095", "Binus University", "Bisnis", "2026-01-01", "Karyawan Tetap"),
            (200096, "Yuni Wijaya Syahputra", "DJK22", "TL222", 200094, "Strategy Analyst", "Manajerial Senior", "Wanita", "yuni.syahputra96@ptsmi.co.id", "6287700000096", "Institut Teknologi Bandung", "Manajemen", "2025-12-31", "Karyawan Tetap"),
            (200097, "Budi Kusuma Nugroho", "DJK22", "STF221", 200095, "Business Analyst", "Manajerial Madya", "Pria", "budi.nugroho97@ptsmi.co.id", "6287700000097", "Universitas Sebelas Maret", "Ekonomi", "2025-12-30", "Karyawan Tetap"),
            (200098, "Joko Ramadhan Firmansyah", "DJK22", "STF222", 200095, "Strategy Analyst", "Manajerial Senior", "Pria", "joko.firmansyah98@ptsmi.co.id", "6287700000098", "Universitas Diponegoro", "Ekonomi", "2025-12-29", "Karyawan Tetap"),
            (200099, "Oka Kurniawan Febrianto", "DJK22", "STF223", 200095, "Operation Analyst", "Manajerial Junior", "Pria", "oka.febrianto99@ptsmi.co.id", "6287700000099", "Universitas Indonesia", "Manajemen", "2025-12-28", "Karyawan Tetap"),
            (200100, "Wahyu Lestari Putri", "DJK22", "STF224", 200095, "Operation Analyst", "Manajerial Madya", "Pria", "wahyu.putri100@ptsmi.co.id", "6287700000100", "Binus University", "Ekonomi", "2025-12-27", "Karyawan Tetap"),
            (200101, "Chandra Wijaya Permata", "DJK22", "STF221", 200095, "Strategy Analyst", "Manajerial Senior", "Pria", "chandra.permata101@ptsmi.co.id", "6287700000101", "Telkom University", "Bisnis", "2025-12-26", "Karyawan Tetap"),
            (200102, "Galih Kusuma Gunawan", "DJK22", "STF222", 200095, "Strategy Analyst", "Manajerial Junior", "Pria", "galih.gunawan102@ptsmi.co.id", "6287700000102", "Binus University", "Ekonomi", "2025-12-25", "Karyawan Tetap"),
            (200103, "Citra Ramadhan Wibowo", "DJK22", "STF223", 200095, "Operation Analyst", "Manajerial Madya", "Wanita", "citra.wibowo103@ptsmi.co.id", "6287700000103", "Universitas Andalas", "Administrasi", "2025-12-24", "Karyawan Tetap"),
            (200104, "Kartika Kurniawan Pratama", "DJK22", "STF224", 200095, "Operation Analyst", "Manajerial Senior", "Wanita", "kartika.pratama104@ptsmi.co.id", "6287700000104", "Universitas Airlangga", "Manajemen", "2025-12-23", "Karyawan Tetap"),
            (200105, "Sari Lestari Utama", "DJK22", "STF221", 200095, "Operation Analyst", "Manajerial Junior", "Wanita", "sari.utama105@ptsmi.co.id", "6287700000105", "Universitas Gadjah Mada", "Ekonomi", "2025-12-22", "Karyawan Tetap"),
            (200106, "Aulia Wijaya Kurniawan", "DK22", "KD221", 200106, "Tax Specialist", "Manajerial Executive", "Wanita", "aulia.kurniawan106@ptsmi.co.id", "6287700000106", "Universitas Andalas", "Ekonomi", "2025-12-21", "Karyawan Tetap"),
            (200107, "Fajar Kusuma Prasetyo", "DK22", "TL222", 200106, "Financial Analyst", "Manajerial Senior", "Pria", "fajar.prasetyo107@ptsmi.co.id", "6287700000107", "Universitas Hasanuddin", "Ekonomi", "2025-12-20", "Karyawan Tetap"),
            (200108, "Lukman Ramadhan Hidayat", "DK22", "TL222", 200106, "Auditor", "Manajerial Senior", "Pria", "lukman.hidayat108@ptsmi.co.id", "6287700000108", "Institut Teknologi Bandung", "Manajemen", "2025-12-19", "Karyawan Tetap"),
            (200109, "Rizky Kurniawan Siregar", "DK22", "STF221", 200107, "Tax Specialist", "Manajerial Madya", "Pria", "rizky.siregar109@ptsmi.co.id", "6287700000109", "Universitas Diponegoro", "Manajemen", "2025-12-18", "Karyawan Tetap"),
            (200110, "Zaki Lestari Susanto", "DK22", "STF222", 200107, "Accountant", "Manajerial Senior", "Pria", "zaki.susanto110@ptsmi.co.id", "6287700000110", "Universitas Padjadjaran", "Keuangan", "2025-12-17", "Karyawan Tetap"),
            (200111, "Dimas Wijaya Wijaya", "DK22", "STF223", 200107, "Tax Specialist", "Manajerial Junior", "Pria", "dimas.wijaya111@ptsmi.co.id", "6287700000111", "Universitas Mercu Buana", "Ekonomi", "2025-12-16", "Karyawan Tetap"),
            (200112, "Hafiz Kusuma Mahendra", "DK22", "STF224", 200107, "Accountant", "Manajerial Madya", "Pria", "hafiz.mahendra112@ptsmi.co.id", "6287700000112", "Universitas Diponegoro", "Akuntansi", "2025-12-15", "Karyawan Tetap"),
            (200113, "Gita Ramadhan Purnama", "DK22", "STF221", 200107, "Tax Specialist", "Manajerial Senior", "Wanita", "gita.purnama113@ptsmi.co.id", "6287700000113", "Universitas Airlangga", "Akuntansi", "2025-12-14", "Karyawan Tetap"),
            (200114, "Maya Kurniawan Ananda", "DK22", "STF222", 200107, "Auditor", "Manajerial Junior", "Wanita", "maya.ananda114@ptsmi.co.id", "6287700000114", "Telkom University", "Akuntansi", "2025-12-13", "Karyawan Tetap"),
            (200115, "Vina Lestari Lestari", "DK22", "STF223", 200107, "Financial Analyst", "Manajerial Madya", "Wanita", "vina.lestari115@ptsmi.co.id", "6287700000115", "Universitas Andalas", "Keuangan", "2025-12-12", "Karyawan Tetap"),
            (200116, "Andi Wijaya Ramadhan", "DK22", "STF224", 200107, "Accountant", "Manajerial Senior", "Pria", "andi.ramadhan116@ptsmi.co.id", "6287700000116", "Binus University", "Perpajakan", "2025-12-11", "Karyawan Tetap"),
            (200117, "Hendra Kusuma Hartono", "DK22", "STF221", 200107, "Accountant", "Manajerial Junior", "Pria", "hendra.hartono117@ptsmi.co.id", "6287700000117", "Universitas Padjadjaran", "Manajemen", "2025-12-10", "Karyawan Tetap"),
            (200118, "Nanda Ramadhan Saputra", "DKHI22", "KD221", 200118, "Accountant", "Manajerial Executive", "Pria", "nanda.saputra118@ptsmi.co.id", "6287700000118", "Universitas Sebelas Maret", "Ekonomi", "2025-12-09", "Karyawan Tetap"),
            (200119, "Taufik Kurniawan Kusuma", "DKHI22", "TL222", 200118, "Tax Specialist", "Manajerial Senior", "Pria", "taufik.kusuma119@ptsmi.co.id", "6287700000119", "Institut Teknologi Bandung", "Akuntansi", "2025-12-08", "Karyawan Tetap"),
            (200120, "Bagas Lestari Handoko", "DKHI22", "TL222", 200118, "Auditor", "Manajerial Senior", "Pria", "bagas.handoko120@ptsmi.co.id", "6287700000120", "Binus University", "Perpajakan", "2025-12-07", "Karyawan Tetap"),
            (200121, "Farhan Wijaya Syahputra", "DKHI22", "STF221", 200119, "Tax Specialist", "Manajerial Madya", "Pria", "farhan.syahputra121@ptsmi.co.id", "6287700000121", "Universitas Sebelas Maret", "Manajemen", "2025-12-06", "Karyawan Tetap"),
            (200122, "Dewi Kusuma Nugroho", "DKHI22", "STF222", 200119, "Accountant", "Manajerial Senior", "Wanita", "dewi.nugroho122@ptsmi.co.id", "6287700000122", "Universitas Gunadarma", "Perpajakan", "2025-12-05", "Karyawan Tetap"),
            (200123, "Indah Ramadhan Firmansyah", "DKHI22", "STF223", 200119, "Tax Specialist", "Manajerial Junior", "Wanita", "indah.firmansyah123@ptsmi.co.id", "6287700000123", "Universitas Brawijaya", "Ekonomi", "2025-12-04", "Karyawan Tetap"),
            (200124, "Putri Kurniawan Febrianto", "DKHI22", "STF224", 200119, "Tax Specialist", "Manajerial Madya", "Wanita", "putri.febrianto124@ptsmi.co.id", "6287700000124", "Universitas Padjadjaran", "Perpajakan", "2025-12-03", "Karyawan Tetap"),
            (200125, "Yuni Lestari Putri", "DKHI22", "STF221", 200119, "Financial Analyst", "Manajerial Senior", "Wanita", "yuni.putri125@ptsmi.co.id", "6287700000125", "Telkom University", "Manajemen", "2025-12-02", "Karyawan Tetap"),
            (200126, "Budi Wijaya Permata", "DKHI22", "STF222", 200119, "Financial Analyst", "Manajerial Junior", "Pria", "budi.permata126@ptsmi.co.id", "6287700000126", "Institut Teknologi Bandung", "Ekonomi", "2025-12-01", "Karyawan Tetap"),
            (200127, "Joko Kusuma Gunawan", "DKHI22", "STF223", 200119, "Financial Analyst", "Manajerial Madya", "Pria", "joko.gunawan127@ptsmi.co.id", "6287700000127", "Universitas Hasanuddin", "Ekonomi", "2025-11-30", "Karyawan Tetap"),
            (200128, "Oka Ramadhan Wibowo", "DKHI22", "STF224", 200119, "Financial Analyst", "Manajerial Senior", "Pria", "oka.wibowo128@ptsmi.co.id", "6287700000128", "Universitas Indonesia", "Perpajakan", "2025-11-29", "Karyawan Tetap"),
            (200129, "Wahyu Kurniawan Pratama", "DKHI22", "STF221", 200119, "Auditor", "Manajerial Junior", "Pria", "wahyu.pratama129@ptsmi.co.id", "6287700000129", "Universitas Hasanuddin", "Ekonomi", "2025-11-28", "Karyawan Tetap"),
            (200130, "Chandra Lestari Utama", "DKHI22", "STF222", 200119, "Financial Analyst", "Manajerial Madya", "Pria", "chandra.utama130@ptsmi.co.id", "6287700000130", "Universitas Brawijaya", "Keuangan", "2025-11-27", "Karyawan Tetap"),
            (200131, "Galih Wijaya Kurniawan", "DKHI22", "STF223", 200119, "Financial Analyst", "Manajerial Senior", "Pria", "galih.kurniawan131@ptsmi.co.id", "6287700000131", "Universitas Diponegoro", "Perpajakan", "2025-11-26", "Karyawan Tetap"),
            (200132, "Citra Kusuma Prasetyo", "DKHI22", "STF224", 200119, "Financial Analyst", "Manajerial Junior", "Wanita", "citra.prasetyo132@ptsmi.co.id", "6287700000132", "Universitas Gunadarma", "Ekonomi", "2025-11-25", "Karyawan Tetap"),
            (200133, "Kartika Ramadhan Hidayat", "DKHI22", "STF221", 200119, "Auditor", "Manajerial Madya", "Wanita", "kartika.hidayat133@ptsmi.co.id", "6287700000133", "Universitas Padjadjaran", "Ekonomi", "2025-11-24", "Karyawan Tetap"),
            (200134, "Sari Kurniawan Siregar", "DKHI22", "STF222", 200119, "Auditor", "Manajerial Senior", "Wanita", "sari.siregar134@ptsmi.co.id", "6287700000134", "Institut Teknologi Bandung", "Manajemen", "2025-11-23", "Karyawan Tetap"),
            (200135, "Aulia Lestari Susanto", "DMRT22", "KD221", 200135, "Operation Analyst", "Manajerial Executive", "Wanita", "aulia.susanto135@ptsmi.co.id", "6287700000135", "Universitas Negeri Jakarta", "Administrasi", "2025-11-22", "Karyawan Tetap"),
            (200136, "Fajar Wijaya Wijaya", "DMRT22", "TL222", 200135, "Strategy Analyst", "Manajerial Senior", "Pria", "fajar.wijaya136@ptsmi.co.id", "6287700000136", "Institut Teknologi Bandung", "Ekonomi", "2025-11-21", "Karyawan Tetap"),
            (200137, "Lukman Kusuma Mahendra", "DMRT22", "TL222", 200135, "Operation Analyst", "Manajerial Senior", "Pria", "lukman.mahendra137@ptsmi.co.id", "6287700000137", "Binus University", "Bisnis", "2025-11-20", "Karyawan Tetap"),
            (200138, "Rizky Ramadhan Purnama", "DMRT22", "STF221", 200136, "Strategy Analyst", "Manajerial Madya", "Pria", "rizky.purnama138@ptsmi.co.id", "6287700000138", "Universitas Mercu Buana", "Administrasi", "2025-11-19", "Karyawan Tetap"),
            (200139, "Zaki Kurniawan Ananda", "DMRT22", "STF222", 200136, "Business Analyst", "Manajerial Senior", "Pria", "zaki.ananda139@ptsmi.co.id", "6287700000139", "Universitas Indonesia", "Bisnis", "2025-11-18", "Karyawan Tetap"),
            (200140, "Dimas Lestari Lestari", "DMRT22", "STF223", 200136, "Strategy Analyst", "Manajerial Junior", "Pria", "dimas.lestari140@ptsmi.co.id", "6287700000140", "Institut Teknologi Bandung", "Statistika", "2025-11-17", "Karyawan Tetap"),
            (200141, "Hafiz Wijaya Ramadhan", "DMRT22", "STF224", 200136, "Strategy Analyst", "Manajerial Madya", "Pria", "hafiz.ramadhan141@ptsmi.co.id", "6287700000141", "Universitas Mercu Buana", "Ekonomi", "2025-11-16", "Karyawan Tetap"),
            (200142, "Gita Kusuma Hartono", "DMRT22", "STF221", 200136, "Business Analyst", "Manajerial Senior", "Wanita", "gita.hartono142@ptsmi.co.id", "6287700000142", "Universitas Brawijaya", "Statistika", "2025-11-15", "Karyawan Tetap"),
            (200143, "Maya Ramadhan Saputra", "DMRT22", "STF222", 200136, "Strategy Analyst", "Manajerial Junior", "Wanita", "maya.saputra143@ptsmi.co.id", "6287700000143", "Universitas Gunadarma", "Manajemen", "2025-11-14", "Karyawan Tetap"),
            (200144, "Vina Kurniawan Kusuma", "DMRT22", "STF223", 200136, "Strategy Analyst", "Manajerial Madya", "Wanita", "vina.kusuma144@ptsmi.co.id", "6287700000144", "Universitas Brawijaya", "Ekonomi", "2025-11-13", "Karyawan Tetap"),
            (200145, "Andi Lestari Handoko", "DMRT22", "STF224", 200136, "Operation Analyst", "Manajerial Senior", "Pria", "andi.handoko145@ptsmi.co.id", "6287700000145", "Universitas Airlangga", "Statistika", "2025-11-12", "Karyawan Tetap"),
            (200146, "Hendra Wijaya Syahputra", "DMRT22", "STF221", 200136, "Operation Analyst", "Manajerial Junior", "Pria", "hendra.syahputra146@ptsmi.co.id", "6287700000146", "Universitas Brawijaya", "Ekonomi", "2025-11-11", "Karyawan Tetap"),
            (200147, "Nanda Kusuma Nugroho", "DMRT22", "STF222", 200136, "Business Analyst", "Manajerial Madya", "Pria", "nanda.nugroho147@ptsmi.co.id", "6287700000147", "Universitas Gunadarma", "Ekonomi", "2025-11-10", "Karyawan Tetap"),
            (200148, "Taufik Ramadhan Firmansyah", "DMRT22", "STF223", 200136, "Strategy Analyst", "Manajerial Senior", "Pria", "taufik.firmansyah148@ptsmi.co.id", "6287700000148", "Universitas Airlangga", "Manajemen", "2025-11-09", "Karyawan Tetap"),
            (200149, "Bagas Kurniawan Febrianto", "DMRT22", "STF224", 200136, "Strategy Analyst", "Manajerial Junior", "Pria", "bagas.febrianto149@ptsmi.co.id", "6287700000149", "Universitas Indonesia", "Ekonomi", "2025-11-08", "Karyawan Tetap"),
            (200150, "Farhan Lestari Putri", "DMRT22", "STF221", 200136, "Strategy Analyst", "Manajerial Madya", "Pria", "farhan.putri150@ptsmi.co.id", "6287700000150", "Universitas Mercu Buana", "Administrasi", "2025-11-07", "Karyawan Tetap"),
            (200151, "Dewi Wijaya Permata", "DMRT22", "STF222", 200136, "Operation Analyst", "Manajerial Senior", "Wanita", "dewi.permata151@ptsmi.co.id", "6287700000151", "Universitas Andalas", "Administrasi", "2025-11-06", "Karyawan Tetap"),
            (200152, "Indah Kusuma Gunawan", "DMRT22", "STF223", 200136, "Strategy Analyst", "Manajerial Junior", "Wanita", "indah.gunawan152@ptsmi.co.id", "6287700000152", "Universitas Negeri Jakarta", "Ekonomi", "2025-11-05", "Karyawan Tetap"),
            (200153, "Putri Ramadhan Wibowo", "DMRT22", "STF224", 200136, "Business Analyst", "Manajerial Madya", "Wanita", "putri.wibowo153@ptsmi.co.id", "6287700000153", "Binus University", "Manajemen", "2025-11-04", "Karyawan Tetap"),
            (200154, "Yuni Kurniawan Pratama", "DMRT22", "STF221", 200136, "Business Analyst", "Manajerial Senior", "Wanita", "yuni.pratama154@ptsmi.co.id", "6287700000154", "Universitas Hasanuddin", "Statistika", "2025-11-03", "Karyawan Tetap"),
            (200155, "Budi Lestari Utama", "DMRT22", "STF222", 200136, "Business Analyst", "Manajerial Junior", "Pria", "budi.utama155@ptsmi.co.id", "6287700000155", "Universitas Padjadjaran", "Statistika", "2025-11-02", "Karyawan Tetap"),
            (200156, "Joko Wijaya Kurniawan", "DMRT22", "STF223", 200136, "Business Analyst", "Manajerial Madya", "Pria", "joko.kurniawan156@ptsmi.co.id", "6287700000156", "Universitas Airlangga", "Ekonomi", "2025-11-01", "Karyawan Tetap"),
            (200157, "Oka Kusuma Prasetyo", "DP122", "KD221", 200157, "Project Analyst", "Manajerial Executive", "Pria", "oka.prasetyo157@ptsmi.co.id", "6287700000157", "Universitas Indonesia", "Bisnis", "2025-10-31", "Karyawan Tetap"),
            (200158, "Wahyu Ramadhan Hidayat", "DP122", "TL222", 200157, "Project Officer", "Manajerial Senior", "Pria", "wahyu.hidayat158@ptsmi.co.id", "6287700000158", "Universitas Brawijaya", "Bisnis", "2025-10-30", "Karyawan Tetap"),
            (200159, "Chandra Kurniawan Siregar", "DP122", "TL222", 200157, "Project Officer", "Manajerial Senior", "Pria", "chandra.siregar159@ptsmi.co.id", "6287700000159", "Universitas Gunadarma", "Teknik Industri", "2025-10-29", "Karyawan Tetap"),
            (200160, "Galih Lestari Susanto", "DP122", "STF221", 200158, "Project Analyst", "Manajerial Madya", "Pria", "galih.susanto160@ptsmi.co.id", "6287700000160", "Universitas Gadjah Mada", "Logistik", "2025-10-28", "Karyawan Tetap"),
            (200161, "Citra Wijaya Wijaya", "DP122", "STF222", 200158, "Project Officer", "Manajerial Senior", "Wanita", "citra.wijaya161@ptsmi.co.id", "6287700000161", "Universitas Hasanuddin", "Manajemen", "2025-10-27", "Karyawan Tetap"),
            (200162, "Kartika Kusuma Mahendra", "DP122", "STF223", 200158, "Project Coordinator", "Manajerial Junior", "Wanita", "kartika.mahendra162@ptsmi.co.id", "6287700000162", "Universitas Gadjah Mada", "Manajemen", "2025-10-26", "Karyawan Tetap"),
            (200163, "Sari Ramadhan Purnama", "DP122", "STF224", 200158, "Project Coordinator", "Manajerial Madya", "Wanita", "sari.purnama163@ptsmi.co.id", "6287700000163", "Institut Teknologi Bandung", "Logistik", "2025-10-25", "Karyawan Tetap"),
            (200164, "Aulia Kurniawan Ananda", "DP122", "STF221", 200158, "Project Coordinator", "Manajerial Senior", "Wanita", "aulia.ananda164@ptsmi.co.id", "6287700000164", "Universitas Hasanuddin", "Teknik Industri", "2025-10-24", "Karyawan Tetap"),
            (200165, "Fajar Lestari Lestari", "DP122", "STF222", 200158, "Project Officer", "Manajerial Junior", "Pria", "fajar.lestari165@ptsmi.co.id", "6287700000165", "Universitas Brawijaya", "Logistik", "2025-10-23", "Karyawan Tetap"),
            (200166, "Lukman Wijaya Ramadhan", "DP122", "STF223", 200158, "Project Analyst", "Manajerial Madya", "Pria", "lukman.ramadhan166@ptsmi.co.id", "6287700000166", "Universitas Gunadarma", "Teknik Industri", "2025-10-22", "Karyawan Tetap"),
            (200167, "Rizky Kusuma Hartono", "DP222", "KD221", 200167, "Project Analyst", "Manajerial Executive", "Pria", "rizky.hartono167@ptsmi.co.id", "6287700000167", "Universitas Andalas", "Logistik", "2025-10-21", "Karyawan Tetap"),
            (200168, "Zaki Ramadhan Saputra", "DP222", "TL222", 200167, "Project Analyst", "Manajerial Senior", "Pria", "zaki.saputra168@ptsmi.co.id", "6287700000168", "Universitas Mercu Buana", "Bisnis", "2025-10-20", "Karyawan Tetap"),
            (200169, "Dimas Kurniawan Kusuma", "DP222", "TL222", 200167, "Project Officer", "Manajerial Senior", "Pria", "dimas.kusuma169@ptsmi.co.id", "6287700000169", "Universitas Mercu Buana", "Teknik Industri", "2025-10-19", "Karyawan Tetap"),
            (200170, "Hafiz Lestari Handoko", "DP222", "STF221", 200168, "Project Coordinator", "Manajerial Madya", "Pria", "hafiz.handoko170@ptsmi.co.id", "6287700000170", "Universitas Gadjah Mada", "Bisnis", "2025-10-18", "Karyawan Tetap"),
            (200171, "Gita Wijaya Syahputra", "DP222", "STF222", 200168, "Project Analyst", "Manajerial Senior", "Wanita", "gita.syahputra171@ptsmi.co.id", "6287700000171", "Binus University", "Manajemen Proyek", "2025-10-17", "Karyawan Tetap"),
            (200172, "Maya Kusuma Nugroho", "DP222", "STF223", 200168, "Project Coordinator", "Manajerial Junior", "Wanita", "maya.nugroho172@ptsmi.co.id", "6287700000172", "Universitas Airlangga", "Bisnis", "2025-10-16", "Karyawan Tetap"),
            (200173, "Vina Ramadhan Firmansyah", "DP222", "STF224", 200168, "Project Officer", "Manajerial Madya", "Wanita", "vina.firmansyah173@ptsmi.co.id", "6287700000173", "Universitas Negeri Jakarta", "Bisnis", "2025-10-15", "Karyawan Tetap"),
            (200174, "Andi Kurniawan Febrianto", "DP222", "STF221", 200168, "Project Coordinator", "Manajerial Senior", "Pria", "andi.febrianto174@ptsmi.co.id", "6287700000174", "Universitas Indonesia", "Manajemen", "2025-10-14", "Karyawan Tetap"),
            (200175, "Hendra Lestari Putri", "DP222", "STF222", 200168, "Project Analyst", "Manajerial Junior", "Pria", "hendra.putri175@ptsmi.co.id", "6287700000175", "Universitas Gadjah Mada", "Teknik Industri", "2025-10-13", "Karyawan Tetap"),
            (200176, "Nanda Wijaya Permata", "DP222", "STF223", 200168, "Project Analyst", "Manajerial Madya", "Pria", "nanda.permata176@ptsmi.co.id", "6287700000176", "Institut Teknologi Bandung", "Manajemen Proyek", "2025-10-12", "Karyawan Tetap"),
            (200177, "Taufik Kusuma Gunawan", "DP222", "STF224", 200168, "Project Officer", "Manajerial Senior", "Pria", "taufik.gunawan177@ptsmi.co.id", "6287700000177", "Universitas Diponegoro", "Manajemen", "2025-10-11", "Karyawan Tetap"),
            (200178, "Bagas Ramadhan Wibowo", "DPB22", "KD221", 200178, "Project Coordinator", "Manajerial Executive", "Pria", "bagas.wibowo178@ptsmi.co.id", "6287700000178", "Universitas Hasanuddin", "Manajemen", "2025-10-10", "Karyawan Tetap"),
            (200179, "Farhan Kurniawan Pratama", "DPB22", "TL222", 200178, "Project Officer", "Manajerial Senior", "Pria", "farhan.pratama179@ptsmi.co.id", "6287700000179", "Telkom University", "Logistik", "2025-10-09", "Karyawan Tetap"),
            (200180, "Dewi Lestari Utama", "DPB22", "TL222", 200178, "Project Officer", "Manajerial Senior", "Wanita", "dewi.utama180@ptsmi.co.id", "6287700000180", "Institut Teknologi Bandung", "Manajemen Proyek", "2025-10-08", "Karyawan Tetap"),
            (200181, "Indah Wijaya Kurniawan", "DPB22", "STF221", 200179, "Project Officer", "Manajerial Madya", "Wanita", "indah.kurniawan181@ptsmi.co.id", "6287700000181", "Universitas Sebelas Maret", "Logistik", "2025-10-07", "Karyawan Tetap"),
            (200182, "Putri Kusuma Prasetyo", "DPB22", "STF222", 200179, "Project Analyst", "Manajerial Senior", "Wanita", "putri.prasetyo182@ptsmi.co.id", "6287700000182", "Universitas Brawijaya", "Teknik Industri", "2025-10-06", "Karyawan Tetap"),
            (200183, "Yuni Ramadhan Hidayat", "DPB22", "STF223", 200179, "Project Officer", "Manajerial Junior", "Wanita", "yuni.hidayat183@ptsmi.co.id", "6287700000183", "Universitas Hasanuddin", "Bisnis", "2025-10-05", "Karyawan Tetap"),
            (200184, "Budi Kurniawan Siregar", "DPB22", "STF224", 200179, "Project Coordinator", "Manajerial Madya", "Pria", "budi.siregar184@ptsmi.co.id", "6287700000184", "Universitas Diponegoro", "Bisnis", "2025-10-04", "Karyawan Tetap"),
            (200185, "Joko Lestari Susanto", "DPB22", "STF221", 200179, "Project Officer", "Manajerial Senior", "Pria", "joko.susanto185@ptsmi.co.id", "6287700000185", "Universitas Brawijaya", "Teknik Industri", "2025-10-03", "Karyawan Tetap"),
            (200186, "Oka Wijaya Wijaya", "DPB22", "STF222", 200179, "Project Coordinator", "Manajerial Junior", "Pria", "oka.wijaya186@ptsmi.co.id", "6287700000186", "Universitas Airlangga", "Teknik Industri", "2025-10-02", "Karyawan Tetap"),
            (200187, "Wahyu Kusuma Mahendra", "DPB22", "STF223", 200179, "Project Coordinator", "Manajerial Madya", "Pria", "wahyu.mahendra187@ptsmi.co.id", "6287700000187", "Institut Teknologi Bandung", "Teknik Industri", "2025-10-01", "Karyawan Tetap"),
            (200188, "Chandra Ramadhan Purnama", "DPB22", "STF224", 200179, "Project Officer", "Manajerial Senior", "Pria", "chandra.purnama188@ptsmi.co.id", "6287700000188", "Universitas Padjadjaran", "Bisnis", "2025-09-30", "Karyawan Tetap"),
            (200189, "Galih Kurniawan Ananda", "DPB22", "STF221", 200179, "Project Coordinator", "Manajerial Junior", "Pria", "galih.ananda189@ptsmi.co.id", "6287700000189", "Universitas Hasanuddin", "Manajemen", "2025-09-29", "Karyawan Tetap"),
            (200190, "Citra Lestari Lestari", "DPB22", "STF222", 200179, "Project Analyst", "Manajerial Madya", "Wanita", "citra.lestari190@ptsmi.co.id", "6287700000190", "Universitas Andalas", "Teknik Industri", "2025-09-28", "Karyawan Tetap"),
            (200191, "Kartika Wijaya Ramadhan", "DPB22", "STF223", 200179, "Project Officer", "Manajerial Senior", "Wanita", "kartika.ramadhan191@ptsmi.co.id", "6287700000191", "Binus University", "Bisnis", "2025-09-27", "Karyawan Tetap"),
            (200192, "Sari Kusuma Hartono", "DPB22", "STF224", 200179, "Project Officer", "Manajerial Junior", "Wanita", "sari.hartono192@ptsmi.co.id", "6287700000192", "Universitas Hasanuddin", "Manajemen Proyek", "2025-09-26", "Karyawan Tetap"),
            (200193, "Aulia Ramadhan Saputra", "DPKMI22", "KD221", 200193, "Project Coordinator", "Manajerial Executive", "Wanita", "aulia.saputra193@ptsmi.co.id", "6287700000193", "Universitas Airlangga", "Manajemen Proyek", "2025-09-25", "Karyawan Tetap"),
            (200194, "Fajar Kurniawan Kusuma", "DPKMI22", "TL222", 200193, "Project Coordinator", "Manajerial Senior", "Pria", "fajar.kusuma194@ptsmi.co.id", "6287700000194", "Universitas Brawijaya", "Logistik", "2025-09-24", "Karyawan Tetap"),
            (200195, "Lukman Lestari Handoko", "DPKMI22", "TL222", 200193, "Project Officer", "Manajerial Senior", "Pria", "lukman.handoko195@ptsmi.co.id", "6287700000195", "Universitas Hasanuddin", "Teknik Industri", "2025-09-23", "Karyawan Tetap"),
            (200196, "Rizky Wijaya Syahputra", "DPKMI22", "STF221", 200194, "Project Officer", "Manajerial Madya", "Pria", "rizky.syahputra196@ptsmi.co.id", "6287700000196", "Universitas Mercu Buana", "Bisnis", "2025-09-22", "Karyawan Tetap"),
            (200197, "Zaki Kusuma Nugroho", "DPKMI22", "STF222", 200194, "Project Officer", "Manajerial Senior", "Pria", "zaki.nugroho197@ptsmi.co.id", "6287700000197", "Binus University", "Bisnis", "2025-09-21", "Karyawan Tetap"),
            (200198, "Dimas Ramadhan Firmansyah", "DPKMI22", "STF223", 200194, "Project Coordinator", "Manajerial Junior", "Pria", "dimas.firmansyah198@ptsmi.co.id", "6287700000198", "Institut Teknologi Bandung", "Manajemen Proyek", "2025-09-20", "Karyawan Tetap"),
            (200199, "Hafiz Kurniawan Febrianto", "DPKMI22", "STF224", 200194, "Project Officer", "Manajerial Madya", "Pria", "hafiz.febrianto199@ptsmi.co.id", "6287700000199", "Universitas Gunadarma", "Teknik Industri", "2025-09-19", "Karyawan Tetap"),
            (200200, "Gita Lestari Putri", "DPKMI22", "STF221", 200194, "Project Officer", "Manajerial Senior", "Wanita", "gita.putri200@ptsmi.co.id", "6287700000200", "Universitas Indonesia", "Teknik Industri", "2025-09-18", "Karyawan Tetap"),
            (200201, "Maya Wijaya Permata", "DPKMI22", "STF222", 200194, "Project Coordinator", "Manajerial Junior", "Wanita", "maya.permata201@ptsmi.co.id", "6287700000201", "Telkom University", "Manajemen", "2025-09-17", "Karyawan Tetap"),
            (200202, "Vina Kusuma Gunawan", "DPKMI22", "STF223", 200194, "Project Officer", "Manajerial Madya", "Wanita", "vina.gunawan202@ptsmi.co.id", "6287700000202", "Institut Teknologi Bandung", "Manajemen", "2025-09-16", "Karyawan Tetap"),
            (200203, "Andi Ramadhan Wibowo", "DPM22", "KD221", 200203, "Project Officer", "Manajerial Executive", "Pria", "andi.wibowo203@ptsmi.co.id", "6287700000203", "Universitas Sebelas Maret", "Bisnis", "2025-09-15", "Karyawan Tetap"),
            (200204, "Hendra Kurniawan Pratama", "DPM22", "TL222", 200203, "Project Coordinator", "Manajerial Senior", "Pria", "hendra.pratama204@ptsmi.co.id", "6287700000204", "Universitas Padjadjaran", "Bisnis", "2025-09-14", "Karyawan Tetap"),
            (200205, "Nanda Lestari Utama", "DPM22", "TL222", 200203, "Project Officer", "Manajerial Senior", "Pria", "nanda.utama205@ptsmi.co.id", "6287700000205", "Universitas Airlangga", "Bisnis", "2025-09-13", "Karyawan Tetap"),
            (200206, "Taufik Wijaya Kurniawan", "DPM22", "STF221", 200204, "Project Officer", "Manajerial Madya", "Pria", "taufik.kurniawan206@ptsmi.co.id", "6287700000206", "Universitas Padjadjaran", "Manajemen", "2025-09-12", "Karyawan Tetap"),
            (200207, "Bagas Kusuma Prasetyo", "DPM22", "STF222", 200204, "Project Coordinator", "Manajerial Senior", "Pria", "bagas.prasetyo207@ptsmi.co.id", "6287700000207", "Universitas Indonesia", "Logistik", "2025-09-11", "Karyawan Tetap"),
            (200208, "Farhan Ramadhan Hidayat", "DPM22", "STF223", 200204, "Project Analyst", "Manajerial Junior", "Pria", "farhan.hidayat208@ptsmi.co.id", "6287700000208", "Universitas Diponegoro", "Manajemen Proyek", "2025-09-10", "Karyawan Tetap"),
            (200209, "Dewi Kurniawan Siregar", "DPM22", "STF224", 200204, "Project Officer", "Manajerial Madya", "Wanita", "dewi.siregar209@ptsmi.co.id", "6287700000209", "Universitas Andalas", "Manajemen Proyek", "2025-09-09", "Karyawan Tetap"),
            (200210, "Indah Lestari Susanto", "DPM22", "STF221", 200204, "Project Officer", "Manajerial Senior", "Wanita", "indah.susanto210@ptsmi.co.id", "6287700000210", "Universitas Hasanuddin", "Bisnis", "2025-09-08", "Karyawan Tetap"),
            (200211, "Putri Wijaya Wijaya", "DPM22", "STF222", 200204, "Project Officer", "Manajerial Junior", "Wanita", "putri.wijaya211@ptsmi.co.id", "6287700000211", "Universitas Hasanuddin", "Manajemen Proyek", "2025-09-07", "Karyawan Tetap"),
            (200212, "Yuni Kusuma Mahendra", "DPM22", "STF223", 200204, "Project Officer", "Manajerial Madya", "Wanita", "yuni.mahendra212@ptsmi.co.id", "6287700000212", "Universitas Diponegoro", "Bisnis", "2025-09-06", "Karyawan Tetap"),
            (200213, "Budi Ramadhan Purnama", "DPM22", "STF224", 200204, "Project Officer", "Manajerial Senior", "Pria", "budi.purnama213@ptsmi.co.id", "6287700000213", "Universitas Mercu Buana", "Bisnis", "2025-09-05", "Karyawan Tetap"),
            (200214, "Joko Kurniawan Ananda", "DPOP22", "KD221", 200214, "Project Officer", "Manajerial Executive", "Pria", "joko.ananda214@ptsmi.co.id", "6287700000214", "Universitas Indonesia", "Manajemen", "2025-09-04", "Karyawan Tetap"),
            (200215, "Oka Lestari Lestari", "DPOP22", "TL222", 200214, "Project Coordinator", "Manajerial Senior", "Pria", "oka.lestari215@ptsmi.co.id", "6287700000215", "Universitas Padjadjaran", "Manajemen", "2025-09-03", "Karyawan Tetap"),
            (200216, "Wahyu Wijaya Ramadhan", "DPOP22", "TL222", 200214, "Project Analyst", "Manajerial Senior", "Pria", "wahyu.ramadhan216@ptsmi.co.id", "6287700000216", "Universitas Andalas", "Logistik", "2025-09-02", "Karyawan Tetap"),
            (200217, "Chandra Kusuma Hartono", "DPOP22", "STF221", 200215, "Project Coordinator", "Manajerial Madya", "Pria", "chandra.hartono217@ptsmi.co.id", "6287700000217", "Telkom University", "Logistik", "2025-09-01", "Karyawan Tetap"),
            (200218, "Galih Ramadhan Saputra", "DPOP22", "STF222", 200215, "Project Coordinator", "Manajerial Senior", "Pria", "galih.saputra218@ptsmi.co.id", "6287700000218", "Universitas Andalas", "Manajemen", "2025-08-31", "Karyawan Tetap"),
            (200219, "Citra Kurniawan Kusuma", "DPOP22", "STF223", 200215, "Project Coordinator", "Manajerial Junior", "Wanita", "citra.kusuma219@ptsmi.co.id", "6287700000219", "Universitas Indonesia", "Manajemen", "2025-08-30", "Karyawan Tetap"),
            (200220, "Kartika Lestari Handoko", "DPOP22", "STF224", 200215, "Project Analyst", "Manajerial Madya", "Wanita", "kartika.handoko220@ptsmi.co.id", "6287700000220", "Universitas Gadjah Mada", "Logistik", "2025-08-29", "Karyawan Tetap"),
            (200221, "Sari Wijaya Syahputra", "DPOP22", "STF221", 200215, "Project Analyst", "Manajerial Senior", "Wanita", "sari.syahputra221@ptsmi.co.id", "6287700000221", "Universitas Brawijaya", "Manajemen Proyek", "2025-08-28", "Karyawan Tetap"),
            (200222, "Aulia Kusuma Nugroho", "DPOP22", "STF222", 200215, "Project Officer", "Manajerial Junior", "Wanita", "aulia.nugroho222@ptsmi.co.id", "6287700000222", "Binus University", "Teknik Industri", "2025-08-27", "Karyawan Tetap"),
            (200223, "Fajar Ramadhan Firmansyah", "DPOP22", "STF223", 200215, "Project Officer", "Manajerial Madya", "Pria", "fajar.firmansyah223@ptsmi.co.id", "6287700000223", "Universitas Indonesia", "Bisnis", "2025-08-26", "Karyawan Tetap"),
            (200224, "Lukman Kurniawan Febrianto", "DPOP22", "STF224", 200215, "Project Coordinator", "Manajerial Senior", "Pria", "lukman.febrianto224@ptsmi.co.id", "6287700000224", "Universitas Mercu Buana", "Logistik", "2025-08-25", "Karyawan Tetap"),
            (200225, "Rizky Lestari Putri", "DPOP22", "STF221", 200215, "Project Coordinator", "Manajerial Junior", "Pria", "rizky.putri225@ptsmi.co.id", "6287700000225", "Universitas Indonesia", "Logistik", "2025-08-24", "Karyawan Tetap"),
            (200226, "Zaki Wijaya Permata", "DPOP22", "STF222", 200215, "Project Coordinator", "Manajerial Madya", "Pria", "zaki.permata226@ptsmi.co.id", "6287700000226", "Universitas Padjadjaran", "Bisnis", "2025-08-23", "Karyawan Tetap"),
            (200227, "Dimas Kusuma Gunawan", "DPOP22", "STF223", 200215, "Project Coordinator", "Manajerial Senior", "Pria", "dimas.gunawan227@ptsmi.co.id", "6287700000227", "Universitas Gunadarma", "Teknik Industri", "2025-08-22", "Karyawan Tetap"),
            (200228, "Hafiz Ramadhan Wibowo", "DPOP22", "STF224", 200215, "Project Officer", "Manajerial Junior", "Pria", "hafiz.wibowo228@ptsmi.co.id", "6287700000228", "Binus University", "Manajemen Proyek", "2025-08-21", "Karyawan Tetap"),
            (200229, "Gita Kurniawan Pratama", "DPOP22", "STF221", 200215, "Project Coordinator", "Manajerial Madya", "Wanita", "gita.pratama229@ptsmi.co.id", "6287700000229", "Universitas Sebelas Maret", "Manajemen Proyek", "2025-08-20", "Karyawan Tetap"),
            (200230, "Maya Lestari Utama", "DPOP22", "STF222", 200215, "Project Coordinator", "Manajerial Senior", "Wanita", "maya.utama230@ptsmi.co.id", "6287700000230", "Telkom University", "Manajemen Proyek", "2025-08-19", "Karyawan Tetap"),
            (200231, "Vina Wijaya Kurniawan", "DPOP22", "STF223", 200215, "Project Coordinator", "Manajerial Junior", "Wanita", "vina.kurniawan231@ptsmi.co.id", "6287700000231", "Universitas Airlangga", "Logistik", "2025-08-18", "Karyawan Tetap"),
            (200232, "Andi Kusuma Prasetyo", "DPOP22", "STF224", 200215, "Project Coordinator", "Manajerial Madya", "Pria", "andi.prasetyo232@ptsmi.co.id", "6287700000232", "Binus University", "Teknik Industri", "2025-08-17", "Karyawan Tetap"),
            (200233, "Hendra Ramadhan Hidayat", "DPOP22", "STF221", 200215, "Project Coordinator", "Manajerial Senior", "Pria", "hendra.hidayat233@ptsmi.co.id", "6287700000233", "Universitas Diponegoro", "Bisnis", "2025-08-16", "Karyawan Tetap"),
            (200234, "Nanda Kurniawan Siregar", "DPP122", "KD221", 200234, "Project Coordinator", "Manajerial Executive", "Pria", "nanda.siregar234@ptsmi.co.id", "6287700000234", "Telkom University", "Manajemen Proyek", "2025-08-15", "Karyawan Tetap"),
            (200235, "Taufik Lestari Susanto", "DPP122", "TL222", 200234, "Project Analyst", "Manajerial Senior", "Pria", "taufik.susanto235@ptsmi.co.id", "6287700000235", "Telkom University", "Manajemen Proyek", "2025-08-14", "Karyawan Tetap"),
            (200236, "Bagas Wijaya Wijaya", "DPP122", "TL222", 200234, "Project Analyst", "Manajerial Senior", "Pria", "bagas.wijaya236@ptsmi.co.id", "6287700000236", "Universitas Hasanuddin", "Bisnis", "2025-08-13", "Karyawan Tetap"),
            (200237, "Farhan Kusuma Mahendra", "DPP122", "STF221", 200235, "Project Officer", "Manajerial Madya", "Pria", "farhan.mahendra237@ptsmi.co.id", "6287700000237", "Universitas Brawijaya", "Bisnis", "2025-08-12", "Karyawan Tetap"),
            (200238, "Dewi Ramadhan Purnama", "DPP122", "STF222", 200235, "Project Analyst", "Manajerial Senior", "Wanita", "dewi.purnama238@ptsmi.co.id", "6287700000238", "Universitas Airlangga", "Teknik Industri", "2025-08-11", "Karyawan Tetap"),
            (200239, "Indah Kurniawan Ananda", "DPP122", "STF223", 200235, "Project Analyst", "Manajerial Junior", "Wanita", "indah.ananda239@ptsmi.co.id", "6287700000239", "Universitas Gunadarma", "Manajemen Proyek", "2025-08-10", "Karyawan Tetap"),
            (200240, "Putri Lestari Lestari", "DPP122", "STF224", 200235, "Project Coordinator", "Manajerial Madya", "Wanita", "putri.lestari240@ptsmi.co.id", "6287700000240", "Telkom University", "Bisnis", "2025-08-09", "Karyawan Tetap"),
            (200241, "Yuni Wijaya Ramadhan", "DPP122", "STF221", 200235, "Project Officer", "Manajerial Senior", "Wanita", "yuni.ramadhan241@ptsmi.co.id", "6287700000241", "Telkom University", "Bisnis", "2025-08-08", "Karyawan Tetap"),
            (200242, "Budi Kusuma Hartono", "DPP122", "STF222", 200235, "Project Analyst", "Manajerial Junior", "Pria", "budi.hartono242@ptsmi.co.id", "6287700000242", "Institut Teknologi Bandung", "Manajemen Proyek", "2025-08-07", "Karyawan Tetap"),
            (200243, "Joko Ramadhan Saputra", "DPP122", "STF223", 200235, "Project Coordinator", "Manajerial Madya", "Pria", "joko.saputra243@ptsmi.co.id", "6287700000243", "Universitas Gunadarma", "Teknik Industri", "2025-08-06", "Karyawan Tetap"),
            (200244, "Oka Kurniawan Kusuma", "DPP122", "STF224", 200235, "Project Officer", "Manajerial Senior", "Pria", "oka.kusuma244@ptsmi.co.id", "6287700000244", "Universitas Mercu Buana", "Manajemen Proyek", "2025-08-05", "Karyawan Tetap"),
            (200245, "Wahyu Lestari Handoko", "DPP122", "STF221", 200235, "Project Officer", "Manajerial Junior", "Pria", "wahyu.handoko245@ptsmi.co.id", "6287700000245", "Universitas Hasanuddin", "Manajemen Proyek", "2025-08-04", "Karyawan Tetap"),
            (200246, "Chandra Wijaya Syahputra", "DPP122", "STF222", 200235, "Project Coordinator", "Manajerial Madya", "Pria", "chandra.syahputra246@ptsmi.co.id", "6287700000246", "Universitas Negeri Jakarta", "Teknik Industri", "2025-08-03", "Karyawan Tetap"),
            (200247, "Galih Kusuma Nugroho", "DPP122", "STF223", 200235, "Project Officer", "Manajerial Senior", "Pria", "galih.nugroho247@ptsmi.co.id", "6287700000247", "Universitas Negeri Jakarta", "Bisnis", "2025-08-02", "Karyawan Tetap"),
            (200248, "Citra Ramadhan Firmansyah", "DPP122", "STF224", 200235, "Project Coordinator", "Manajerial Junior", "Wanita", "citra.firmansyah248@ptsmi.co.id", "6287700000248", "Universitas Sebelas Maret", "Manajemen", "2025-08-01", "Karyawan Tetap"),
            (200249, "Kartika Kurniawan Febrianto", "DPP122", "STF221", 200235, "Project Analyst", "Manajerial Madya", "Wanita", "kartika.febrianto249@ptsmi.co.id", "6287700000249", "Universitas Airlangga", "Manajemen", "2025-07-31", "Karyawan Tetap"),
            (200250, "Sari Lestari Putri", "DPP122", "STF222", 200235, "Project Officer", "Manajerial Senior", "Wanita", "sari.putri250@ptsmi.co.id", "6287700000250", "Universitas Hasanuddin", "Manajemen Proyek", "2025-07-30", "Karyawan Tetap"),
            (200251, "Aulia Wijaya Permata", "DPP122", "STF223", 200235, "Project Coordinator", "Manajerial Junior", "Wanita", "aulia.permata251@ptsmi.co.id", "6287700000251", "Universitas Indonesia", "Bisnis", "2025-07-29", "Karyawan Tetap"),
            (200252, "Fajar Kusuma Gunawan", "DPP122", "STF224", 200235, "Project Coordinator", "Manajerial Madya", "Pria", "fajar.gunawan252@ptsmi.co.id", "6287700000252", "Universitas Sebelas Maret", "Logistik", "2025-07-28", "Karyawan Tetap"),
            (200253, "Lukman Ramadhan Wibowo", "DPP222", "KD221", 200253, "Project Coordinator", "Manajerial Executive", "Pria", "lukman.wibowo253@ptsmi.co.id", "6287700000253", "Universitas Andalas", "Logistik", "2025-07-27", "Karyawan Tetap"),
            (200254, "Rizky Kurniawan Pratama", "DPP222", "TL222", 200253, "Project Officer", "Manajerial Senior", "Pria", "rizky.pratama254@ptsmi.co.id", "6287700000254", "Universitas Negeri Jakarta", "Manajemen", "2025-07-26", "Karyawan Tetap"),
            (200255, "Zaki Lestari Utama", "DPP222", "TL222", 200253, "Project Officer", "Manajerial Senior", "Pria", "zaki.utama255@ptsmi.co.id", "6287700000255", "Institut Teknologi Bandung", "Manajemen", "2025-07-25", "Karyawan Tetap"),
            (200256, "Dimas Wijaya Kurniawan", "DPP222", "STF221", 200254, "Project Analyst", "Manajerial Madya", "Pria", "dimas.kurniawan256@ptsmi.co.id", "6287700000256", "Binus University", "Bisnis", "2025-07-24", "Karyawan Tetap"),
            (200257, "Hafiz Kusuma Prasetyo", "DPP222", "STF222", 200254, "Project Analyst", "Manajerial Senior", "Pria", "hafiz.prasetyo257@ptsmi.co.id", "6287700000257", "Universitas Mercu Buana", "Logistik", "2025-07-23", "Karyawan Tetap"),
            (200258, "Gita Ramadhan Hidayat", "DPP222", "STF223", 200254, "Project Coordinator", "Manajerial Junior", "Wanita", "gita.hidayat258@ptsmi.co.id", "6287700000258", "Universitas Indonesia", "Manajemen", "2025-07-22", "Karyawan Tetap"),
            (200259, "Maya Kurniawan Siregar", "DPP222", "STF224", 200254, "Project Analyst", "Manajerial Madya", "Wanita", "maya.siregar259@ptsmi.co.id", "6287700000259", "Universitas Andalas", "Teknik Industri", "2025-07-21", "Karyawan Tetap"),
            (200260, "Vina Lestari Susanto", "DPP222", "STF221", 200254, "Project Coordinator", "Manajerial Senior", "Wanita", "vina.susanto260@ptsmi.co.id", "6287700000260", "Universitas Indonesia", "Teknik Industri", "2025-07-20", "Karyawan Tetap"),
            (200261, "Andi Wijaya Wijaya", "DPP322", "KD221", 200261, "Project Coordinator", "Manajerial Executive", "Pria", "andi.wijaya261@ptsmi.co.id", "6287700000261", "Binus University", "Manajemen", "2025-07-19", "Karyawan Tetap"),
            (200262, "Hendra Kusuma Mahendra", "DPP322", "TL222", 200261, "Project Coordinator", "Manajerial Senior", "Pria", "hendra.mahendra262@ptsmi.co.id", "6287700000262", "Universitas Brawijaya", "Bisnis", "2025-07-18", "Karyawan Tetap"),
            (200263, "Nanda Ramadhan Purnama", "DPP322", "TL222", 200261, "Project Officer", "Manajerial Senior", "Pria", "nanda.purnama263@ptsmi.co.id", "6287700000263", "Universitas Brawijaya", "Manajemen Proyek", "2025-07-17", "Karyawan Tetap"),
            (200264, "Taufik Kurniawan Ananda", "DPP322", "STF221", 200262, "Project Coordinator", "Manajerial Madya", "Pria", "taufik.ananda264@ptsmi.co.id", "6287700000264", "Binus University", "Manajemen", "2025-07-16", "Karyawan Tetap"),
            (200265, "Bagas Lestari Lestari", "DPP322", "STF222", 200262, "Project Officer", "Manajerial Senior", "Pria", "bagas.lestari265@ptsmi.co.id", "6287700000265", "Universitas Andalas", "Bisnis", "2025-07-15", "Karyawan Tetap"),
            (200266, "Farhan Wijaya Ramadhan", "DPP322", "STF223", 200262, "Project Officer", "Manajerial Junior", "Pria", "farhan.ramadhan266@ptsmi.co.id", "6287700000266", "Binus University", "Manajemen Proyek", "2025-07-14", "Karyawan Tetap"),
            (200267, "Dewi Kusuma Hartono", "DPP322", "STF224", 200262, "Project Coordinator", "Manajerial Madya", "Wanita", "dewi.hartono267@ptsmi.co.id", "6287700000267", "Binus University", "Logistik", "2025-07-13", "Karyawan Tetap"),
            (200268, "Indah Ramadhan Saputra", "DPP322", "STF221", 200262, "Project Officer", "Manajerial Senior", "Wanita", "indah.saputra268@ptsmi.co.id", "6287700000268", "Telkom University", "Logistik", "2025-07-12", "Karyawan Tetap"),
            (200269, "Putri Kurniawan Kusuma", "DPP322", "STF222", 200262, "Project Analyst", "Manajerial Junior", "Wanita", "putri.kusuma269@ptsmi.co.id", "6287700000269", "Universitas Sebelas Maret", "Manajemen", "2025-07-11", "Karyawan Tetap"),
            (200270, "Yuni Lestari Handoko", "DPP322", "STF223", 200262, "Project Coordinator", "Manajerial Madya", "Wanita", "yuni.handoko270@ptsmi.co.id", "6287700000270", "Universitas Indonesia", "Teknik Industri", "2025-07-10", "Karyawan Tetap"),
            (200271, "Budi Wijaya Syahputra", "DPP322", "STF224", 200262, "Project Officer", "Manajerial Senior", "Pria", "budi.syahputra271@ptsmi.co.id", "6287700000271", "Universitas Sebelas Maret", "Logistik", "2025-07-09", "Karyawan Tetap"),
            (200272, "Joko Kusuma Nugroho", "DPP322", "STF221", 200262, "Project Coordinator", "Manajerial Junior", "Pria", "joko.nugroho272@ptsmi.co.id", "6287700000272", "Universitas Diponegoro", "Manajemen Proyek", "2025-07-08", "Karyawan Tetap"),
            (200273, "Oka Ramadhan Firmansyah", "DPP322", "STF222", 200262, "Project Analyst", "Manajerial Madya", "Pria", "oka.firmansyah273@ptsmi.co.id", "6287700000273", "Universitas Mercu Buana", "Manajemen Proyek", "2025-07-07", "Karyawan Tetap"),
            (200274, "Wahyu Kurniawan Febrianto", "DPP322", "STF223", 200262, "Project Officer", "Manajerial Senior", "Pria", "wahyu.febrianto274@ptsmi.co.id", "6287700000274", "Universitas Hasanuddin", "Teknik Industri", "2025-07-06", "Karyawan Tetap"),
            (200275, "Chandra Lestari Putri", "DPP322", "STF224", 200262, "Project Analyst", "Manajerial Junior", "Pria", "chandra.putri275@ptsmi.co.id", "6287700000275", "Institut Teknologi Bandung", "Manajemen", "2025-07-05", "Karyawan Tetap"),
            (200276, "Galih Wijaya Permata", "DPP322", "STF221", 200262, "Project Officer", "Manajerial Madya", "Pria", "galih.permata276@ptsmi.co.id", "6287700000276", "Universitas Mercu Buana", "Bisnis", "2025-07-04", "Karyawan Tetap"),
            (200277, "Citra Kusuma Gunawan", "DPP322", "STF222", 200262, "Project Analyst", "Manajerial Senior", "Wanita", "citra.gunawan277@ptsmi.co.id", "6287700000277", "Telkom University", "Manajemen Proyek", "2025-07-03", "Karyawan Tetap"),
            (200278, "Kartika Ramadhan Wibowo", "DPP322", "STF223", 200262, "Project Officer", "Manajerial Junior", "Wanita", "kartika.wibowo278@ptsmi.co.id", "6287700000278", "Universitas Andalas", "Manajemen", "2025-07-02", "Karyawan Tetap"),
            (200279, "Sari Kurniawan Pratama", "DPP322", "STF224", 200262, "Project Analyst", "Manajerial Madya", "Wanita", "sari.pratama279@ptsmi.co.id", "6287700000279", "Universitas Gunadarma", "Manajemen", "2025-07-01", "Karyawan Tetap"),
            (200280, "Aulia Lestari Utama", "DPP322", "STF221", 200262, "Project Officer", "Manajerial Senior", "Wanita", "aulia.utama280@ptsmi.co.id", "6287700000280", "Institut Teknologi Bandung", "Logistik", "2025-06-30", "Karyawan Tetap"),
            (200281, "Fajar Wijaya Kurniawan", "DPP322", "STF222", 200262, "Project Officer", "Manajerial Junior", "Pria", "fajar.kurniawan281@ptsmi.co.id", "6287700000281", "Telkom University", "Manajemen", "2025-06-29", "Karyawan Tetap"),
            (200282, "Lukman Kusuma Prasetyo", "DPPK22", "KD221", 200282, "Project Coordinator", "Manajerial Executive", "Pria", "lukman.prasetyo282@ptsmi.co.id", "6287700000282", "Universitas Andalas", "Manajemen Proyek", "2025-06-28", "Karyawan Tetap"),
            (200283, "Rizky Ramadhan Hidayat", "DPPK22", "TL222", 200282, "Project Analyst", "Manajerial Senior", "Pria", "rizky.hidayat283@ptsmi.co.id", "6287700000283", "Universitas Gadjah Mada", "Teknik Industri", "2025-06-27", "Karyawan Tetap"),
            (200284, "Zaki Kurniawan Siregar", "DPPK22", "TL222", 200282, "Project Analyst", "Manajerial Senior", "Pria", "zaki.siregar284@ptsmi.co.id", "6287700000284", "Institut Teknologi Bandung", "Manajemen", "2025-06-26", "Karyawan Tetap"),
            (200285, "Dimas Lestari Susanto", "DPPK22", "STF221", 200283, "Project Analyst", "Manajerial Madya", "Pria", "dimas.susanto285@ptsmi.co.id", "6287700000285", "Institut Teknologi Bandung", "Manajemen", "2025-06-25", "Karyawan Tetap"),
            (200286, "Hafiz Wijaya Wijaya", "DPPK22", "STF222", 200283, "Project Coordinator", "Manajerial Senior", "Pria", "hafiz.wijaya286@ptsmi.co.id", "6287700000286", "Telkom University", "Teknik Industri", "2025-06-24", "Karyawan Tetap"),
            (200287, "Gita Kusuma Mahendra", "DPPK22", "STF223", 200283, "Project Coordinator", "Manajerial Junior", "Wanita", "gita.mahendra287@ptsmi.co.id", "6287700000287", "Universitas Sebelas Maret", "Manajemen Proyek", "2025-06-23", "Karyawan Tetap"),
            (200288, "Maya Ramadhan Purnama", "DPPK22", "STF224", 200283, "Project Officer", "Manajerial Madya", "Wanita", "maya.purnama288@ptsmi.co.id", "6287700000288", "Universitas Mercu Buana", "Bisnis", "2025-06-22", "Karyawan Tetap"),
            (200289, "Vina Kurniawan Ananda", "DPPK22", "STF221", 200283, "Project Analyst", "Manajerial Senior", "Wanita", "vina.ananda289@ptsmi.co.id", "6287700000289", "Universitas Andalas", "Bisnis", "2025-06-21", "Karyawan Tetap"),
            (200290, "Andi Lestari Lestari", "DPPK22", "STF222", 200283, "Project Coordinator", "Manajerial Junior", "Pria", "andi.lestari290@ptsmi.co.id", "6287700000290", "Binus University", "Logistik", "2025-06-20", "Karyawan Tetap"),
            (200291, "Hendra Wijaya Ramadhan", "DPPK22", "STF223", 200283, "Project Coordinator", "Manajerial Madya", "Pria", "hendra.ramadhan291@ptsmi.co.id", "6287700000291", "Universitas Andalas", "Manajemen Proyek", "2025-06-19", "Karyawan Tetap"),
            (200292, "Nanda Kusuma Hartono", "DPPK22", "STF224", 200283, "Project Coordinator", "Manajerial Senior", "Pria", "nanda.hartono292@ptsmi.co.id", "6287700000292", "Universitas Sebelas Maret", "Bisnis", "2025-06-18", "Karyawan Tetap"),
            (200293, "Taufik Ramadhan Saputra", "DPPK22", "STF221", 200283, "Project Analyst", "Manajerial Junior", "Pria", "taufik.saputra293@ptsmi.co.id", "6287700000293", "Institut Teknologi Bandung", "Teknik Industri", "2025-06-17", "Karyawan Tetap"),
            (200294, "Bagas Kurniawan Kusuma", "DPPRO22", "KD221", 200294, "Project Analyst", "Manajerial Executive", "Pria", "bagas.kusuma294@ptsmi.co.id", "6287700000294", "Universitas Hasanuddin", "Teknik Industri", "2025-06-16", "Karyawan Tetap"),
            (200295, "Farhan Lestari Handoko", "DPPRO22", "TL222", 200294, "Project Coordinator", "Manajerial Senior", "Pria", "farhan.handoko295@ptsmi.co.id", "6287700000295", "Universitas Airlangga", "Logistik", "2025-06-15", "Karyawan Tetap"),
            (200296, "Dewi Wijaya Syahputra", "DPPRO22", "TL222", 200294, "Project Coordinator", "Manajerial Senior", "Wanita", "dewi.syahputra296@ptsmi.co.id", "6287700000296", "Universitas Negeri Jakarta", "Teknik Industri", "2025-06-14", "Karyawan Tetap"),
            (200297, "Indah Kusuma Nugroho", "DPPRO22", "STF221", 200295, "Project Officer", "Manajerial Madya", "Wanita", "indah.nugroho297@ptsmi.co.id", "6287700000297", "Universitas Brawijaya", "Logistik", "2025-06-13", "Karyawan Tetap"),
            (200298, "Putri Ramadhan Firmansyah", "DPPRO22", "STF222", 200295, "Project Coordinator", "Manajerial Senior", "Wanita", "putri.firmansyah298@ptsmi.co.id", "6287700000298", "Universitas Negeri Jakarta", "Bisnis", "2025-06-12", "Karyawan Tetap"),
            (200299, "Yuni Kurniawan Febrianto", "DPPRO22", "STF223", 200295, "Project Analyst", "Manajerial Junior", "Wanita", "yuni.febrianto299@ptsmi.co.id", "6287700000299", "Universitas Mercu Buana", "Logistik", "2025-06-11", "Karyawan Tetap"),
            (200300, "Budi Lestari Putri", "DPPRO22", "STF224", 200295, "Project Analyst", "Manajerial Madya", "Pria", "budi.putri300@ptsmi.co.id", "6287700000300", "Universitas Airlangga", "Bisnis", "2025-06-10", "Karyawan Tetap"),
            (200301, "Joko Wijaya Permata", "DPPRO22", "STF221", 200295, "Project Analyst", "Manajerial Senior", "Pria", "joko.permata301@ptsmi.co.id", "6287700000301", "Universitas Hasanuddin", "Manajemen", "2025-06-09", "Karyawan Tetap"),
            (200302, "Oka Kusuma Gunawan", "DPPRO22", "STF222", 200295, "Project Officer", "Manajerial Junior", "Pria", "oka.gunawan302@ptsmi.co.id", "6287700000302", "Universitas Indonesia", "Teknik Industri", "2025-06-08", "Karyawan Tetap"),
            (200303, "Wahyu Ramadhan Wibowo", "DPPRO22", "STF223", 200295, "Project Officer", "Manajerial Madya", "Pria", "wahyu.wibowo303@ptsmi.co.id", "6287700000303", "Universitas Mercu Buana", "Teknik Industri", "2025-06-07", "Karyawan Tetap"),
            (200304, "Chandra Kurniawan Pratama", "DPPRO22", "STF224", 200295, "Project Officer", "Manajerial Senior", "Pria", "chandra.pratama304@ptsmi.co.id", "6287700000304", "Universitas Gadjah Mada", "Bisnis", "2025-06-06", "Karyawan Tetap"),
            (200305, "Galih Lestari Utama", "DPPRO22", "STF221", 200295, "Project Officer", "Manajerial Junior", "Pria", "galih.utama305@ptsmi.co.id", "6287700000305", "Universitas Diponegoro", "Manajemen", "2025-06-05", "Karyawan Tetap"),
            (200306, "Citra Wijaya Kurniawan", "DPPRO22", "STF222", 200295, "Project Coordinator", "Manajerial Madya", "Wanita", "citra.kurniawan306@ptsmi.co.id", "6287700000306", "Universitas Gunadarma", "Teknik Industri", "2025-06-04", "Karyawan Tetap"),
            (200307, "Kartika Kusuma Prasetyo", "DRE22", "KD221", 200307, "Strategy Analyst", "Manajerial Executive", "Wanita", "kartika.prasetyo307@ptsmi.co.id", "6287700000307", "Universitas Sebelas Maret", "Bisnis", "2025-06-03", "Karyawan Tetap"),
            (200308, "Sari Ramadhan Hidayat", "DRE22", "TL222", 200307, "Operation Analyst", "Manajerial Senior", "Wanita", "sari.hidayat308@ptsmi.co.id", "6287700000308", "Universitas Diponegoro", "Bisnis", "2025-06-02", "Karyawan Tetap"),
            (200309, "Aulia Kurniawan Siregar", "DRE22", "TL222", 200307, "Operation Analyst", "Manajerial Senior", "Wanita", "aulia.siregar309@ptsmi.co.id", "6287700000309", "Universitas Brawijaya", "Statistika", "2025-06-01", "Karyawan Tetap"),
            (200310, "Fajar Lestari Susanto", "DRE22", "STF221", 200308, "Operation Analyst", "Manajerial Madya", "Pria", "fajar.susanto310@ptsmi.co.id", "6287700000310", "Universitas Negeri Jakarta", "Manajemen", "2025-05-31", "Karyawan Tetap"),
            (200311, "Lukman Wijaya Wijaya", "DRE22", "STF222", 200308, "Strategy Analyst", "Manajerial Senior", "Pria", "lukman.wijaya311@ptsmi.co.id", "6287700000311", "Universitas Hasanuddin", "Bisnis", "2025-05-30", "Karyawan Tetap"),
            (200312, "Rizky Kusuma Mahendra", "DRE22", "STF223", 200308, "Operation Analyst", "Manajerial Junior", "Pria", "rizky.mahendra312@ptsmi.co.id", "6287700000312", "Universitas Gadjah Mada", "Ekonomi", "2025-05-29", "Karyawan Tetap"),
            (200313, "Zaki Ramadhan Purnama", "DRE22", "STF224", 200308, "Business Analyst", "Manajerial Madya", "Pria", "zaki.purnama313@ptsmi.co.id", "6287700000313", "Universitas Airlangga", "Statistika", "2025-05-28", "Karyawan Tetap"),
            (200314, "Dimas Kurniawan Ananda", "DRE22", "STF221", 200308, "Operation Analyst", "Manajerial Senior", "Pria", "dimas.ananda314@ptsmi.co.id", "6287700000314", "Binus University", "Statistika", "2025-05-27", "Karyawan Tetap"),
            (200315, "Hafiz Lestari Lestari", "DRE22", "STF222", 200308, "Strategy Analyst", "Manajerial Junior", "Pria", "hafiz.lestari315@ptsmi.co.id", "6287700000315", "Universitas Indonesia", "Ekonomi", "2025-05-26", "Karyawan Tetap"),
            (200316, "Gita Wijaya Ramadhan", "DRE22", "STF223", 200308, "Strategy Analyst", "Manajerial Madya", "Wanita", "gita.ramadhan316@ptsmi.co.id", "6287700000316", "Telkom University", "Ekonomi", "2025-05-25", "Karyawan Tetap"),
            (200317, "Maya Kusuma Hartono", "DSDM22", "KD221", 200317, "HR Analyst", "Manajerial Executive", "Wanita", "maya.hartono317@ptsmi.co.id", "6287700000317", "Universitas Hasanuddin", "Hukum", "2025-05-24", "Karyawan Tetap"),
            (200318, "Vina Ramadhan Saputra", "DSDM22", "TL222", 200317, "Recruiter", "Manajerial Senior", "Wanita", "vina.saputra318@ptsmi.co.id", "6287700000318", "Universitas Andalas", "Manajemen SDM", "2025-05-23", "Karyawan Tetap"),
            (200319, "Andi Kurniawan Kusuma", "DSDM22", "TL222", 200317, "Recruiter", "Manajerial Senior", "Pria", "andi.kusuma319@ptsmi.co.id", "6287700000319", "Universitas Mercu Buana", "Psikologi", "2025-05-22", "Karyawan Tetap"),
            (200320, "Hendra Lestari Handoko", "DSDM22", "STF221", 200318, "HR Operations", "Manajerial Madya", "Pria", "hendra.handoko320@ptsmi.co.id", "6287700000320", "Universitas Brawijaya", "Psikologi", "2025-05-21", "Karyawan Tetap"),
            (200321, "Nanda Wijaya Syahputra", "DSDM22", "STF222", 200318, "HR Analyst", "Manajerial Senior", "Pria", "nanda.syahputra321@ptsmi.co.id", "6287700000321", "Universitas Diponegoro", "Psikologi", "2025-05-20", "Karyawan Tetap"),
            (200322, "Taufik Kusuma Nugroho", "DSDM22", "STF223", 200318, "Talent Development", "Manajerial Junior", "Pria", "taufik.nugroho322@ptsmi.co.id", "6287700000322", "Institut Teknologi Bandung", "Psikologi", "2025-05-19", "Karyawan Tetap"),
            (200323, "Bagas Ramadhan Firmansyah", "DSDM22", "STF224", 200318, "Recruiter", "Manajerial Madya", "Pria", "bagas.firmansyah323@ptsmi.co.id", "6287700000323", "Institut Teknologi Bandung", "Manajemen SDM", "2025-05-18", "Karyawan Tetap"),
            (200324, "Farhan Kurniawan Febrianto", "DSDM22", "STF221", 200318, "Recruiter", "Manajerial Senior", "Pria", "farhan.febrianto324@ptsmi.co.id", "6287700000324", "Universitas Diponegoro", "Hukum", "2025-05-17", "Karyawan Tetap"),
            (200325, "Dewi Lestari Putri", "DSDM22", "STF222", 200318, "Recruiter", "Manajerial Junior", "Wanita", "dewi.putri325@ptsmi.co.id", "6287700000325", "Universitas Brawijaya", "Komunikasi", "2025-05-16", "Karyawan Tetap"),
            (200326, "Indah Wijaya Permata", "DSDM22", "STF223", 200318, "Talent Development", "Manajerial Madya", "Wanita", "indah.permata326@ptsmi.co.id", "6287700000326", "Universitas Mercu Buana", "Administrasi Bisnis", "2025-05-15", "Karyawan Tetap"),
            (200327, "Putri Kusuma Gunawan", "DSDM22", "STF224", 200318, "Recruiter", "Manajerial Senior", "Wanita", "putri.gunawan327@ptsmi.co.id", "6287700000327", "Universitas Andalas", "Psikologi", "2025-05-14", "Karyawan Tetap"),
            (200328, "Yuni Ramadhan Wibowo", "DSDM22", "STF221", 200318, "HR Operations", "Manajerial Junior", "Wanita", "yuni.wibowo328@ptsmi.co.id", "6287700000328", "Universitas Gadjah Mada", "Administrasi Bisnis", "2025-05-13", "Karyawan Tetap"),
            (200329, "Budi Kurniawan Pratama", "DSDM22", "STF222", 200318, "HR Operations", "Manajerial Madya", "Pria", "budi.pratama329@ptsmi.co.id", "6287700000329", "Universitas Gunadarma", "Manajemen SDM", "2025-05-12", "Karyawan Tetap"),
            (200330, "Joko Lestari Utama", "DSDM22", "STF223", 200318, "HR Operations", "Manajerial Senior", "Pria", "joko.utama330@ptsmi.co.id", "6287700000330", "Universitas Hasanuddin", "Psikologi", "2025-05-11", "Karyawan Tetap"),
            (200331, "Oka Wijaya Kurniawan", "DSDM22", "STF224", 200318, "HR Operations", "Manajerial Junior", "Pria", "oka.kurniawan331@ptsmi.co.id", "6287700000331", "Universitas Gunadarma", "Administrasi Bisnis", "2025-05-10", "Karyawan Tetap"),
            (200332, "Wahyu Kusuma Prasetyo", "DSDM22", "STF221", 200318, "HR Analyst", "Manajerial Madya", "Pria", "wahyu.prasetyo332@ptsmi.co.id", "6287700000332", "Universitas Mercu Buana", "Komunikasi", "2025-05-09", "Karyawan Tetap"),
            (200333, "Chandra Ramadhan Hidayat", "DSDM22", "STF222", 200318, "HR Analyst", "Manajerial Senior", "Pria", "chandra.hidayat333@ptsmi.co.id", "6287700000333", "Universitas Hasanuddin", "Administrasi Bisnis", "2025-05-08", "Karyawan Tetap"),
            (200334, "Galih Kurniawan Siregar", "DSDM22", "STF223", 200318, "Recruiter", "Manajerial Junior", "Pria", "galih.siregar334@ptsmi.co.id", "6287700000334", "Universitas Sebelas Maret", "Administrasi Bisnis", "2025-05-07", "Karyawan Tetap"),
            (200335, "Citra Lestari Susanto", "DSDM22", "STF224", 200318, "HR Operations", "Manajerial Madya", "Wanita", "citra.susanto335@ptsmi.co.id", "6287700000335", "Institut Teknologi Bandung", "Manajemen SDM", "2025-05-06", "Karyawan Tetap"),
            (200336, "Kartika Wijaya Wijaya", "DSDM22", "STF221", 200318, "Recruiter", "Manajerial Senior", "Wanita", "kartika.wijaya336@ptsmi.co.id", "6287700000336", "Universitas Airlangga", "Administrasi Bisnis", "2025-05-05", "Karyawan Tetap"),
            (200337, "Sari Kusuma Mahendra", "DSDM22", "STF222", 200318, "Recruiter", "Manajerial Junior", "Wanita", "sari.mahendra337@ptsmi.co.id", "6287700000337", "Universitas Airlangga", "Psikologi", "2025-05-04", "Karyawan Tetap"),
            (200338, "Aulia Ramadhan Purnama", "DSDM22", "STF223", 200318, "HR Analyst", "Manajerial Madya", "Wanita", "aulia.purnama338@ptsmi.co.id", "6287700000338", "Universitas Padjadjaran", "Manajemen SDM", "2025-05-03", "Karyawan Tetap"),
            (200339, "Fajar Kurniawan Ananda", "DSDM22", "STF224", 200318, "Talent Development", "Manajerial Senior", "Pria", "fajar.ananda339@ptsmi.co.id", "6287700000339", "Telkom University", "Psikologi", "2025-05-02", "Karyawan Tetap"),
            (200340, "Lukman Lestari Lestari", "DSDM22", "STF221", 200318, "Recruiter", "Manajerial Junior", "Pria", "lukman.lestari340@ptsmi.co.id", "6287700000340", "Universitas Indonesia", "Psikologi", "2025-05-01", "Karyawan Tetap"),
            (200341, "Rizky Wijaya Ramadhan", "DSDM22", "STF222", 200318, "HR Operations", "Manajerial Madya", "Pria", "rizky.ramadhan341@ptsmi.co.id", "6287700000341", "Universitas Padjadjaran", "Psikologi", "2025-04-30", "Karyawan Tetap"),
            (200342, "Zaki Kusuma Hartono", "DSDM22", "STF223", 200318, "HR Analyst", "Manajerial Senior", "Pria", "zaki.hartono342@ptsmi.co.id", "6287700000342", "Universitas Gadjah Mada", "Manajemen SDM", "2025-04-29", "Karyawan Tetap"),
            (200343, "Dimas Ramadhan Saputra", "DSDM22", "STF224", 200318, "HR Operations", "Manajerial Junior", "Pria", "dimas.saputra343@ptsmi.co.id", "6287700000343", "Universitas Andalas", "Manajemen SDM", "2025-04-28", "Karyawan Tetap"),
            (200344, "Hafiz Kurniawan Kusuma", "DSP22", "KD221", 200344, "Operation Analyst", "Manajerial Executive", "Pria", "hafiz.kusuma344@ptsmi.co.id", "6287700000344", "Binus University", "Manajemen", "2025-04-27", "Karyawan Tetap"),
            (200345, "Gita Lestari Handoko", "DSP22", "TL222", 200344, "Operation Analyst", "Manajerial Senior", "Wanita", "gita.handoko345@ptsmi.co.id", "6287700000345", "Universitas Sebelas Maret", "Manajemen", "2025-04-26", "Karyawan Tetap"),
            (200346, "Maya Wijaya Syahputra", "DSP22", "TL222", 200344, "Strategy Analyst", "Manajerial Senior", "Wanita", "maya.syahputra346@ptsmi.co.id", "6287700000346", "Universitas Hasanuddin", "Bisnis", "2025-04-25", "Karyawan Tetap"),
            (200347, "Vina Kusuma Nugroho", "DSP22", "STF221", 200345, "Strategy Analyst", "Manajerial Madya", "Wanita", "vina.nugroho347@ptsmi.co.id", "6287700000347", "Universitas Negeri Jakarta", "Ekonomi", "2025-04-24", "Karyawan Tetap"),
            (200348, "Andi Ramadhan Firmansyah", "DSP22", "STF222", 200345, "Business Analyst", "Manajerial Senior", "Pria", "andi.firmansyah348@ptsmi.co.id", "6287700000348", "Universitas Brawijaya", "Bisnis", "2025-04-23", "Karyawan Tetap"),
            (200349, "Hendra Kurniawan Febrianto", "DSP22", "STF223", 200345, "Business Analyst", "Manajerial Junior", "Pria", "hendra.febrianto349@ptsmi.co.id", "6287700000349", "Universitas Mercu Buana", "Administrasi", "2025-04-22", "Karyawan Tetap"),
            (200350, "Nanda Lestari Putri", "DSP22", "STF224", 200345, "Strategy Analyst", "Manajerial Madya", "Pria", "nanda.putri350@ptsmi.co.id", "6287700000350", "Universitas Sebelas Maret", "Administrasi", "2025-04-21", "Karyawan Tetap"),
            (200351, "Taufik Wijaya Permata", "DSP22", "STF221", 200345, "Operation Analyst", "Manajerial Senior", "Pria", "taufik.permata351@ptsmi.co.id", "6287700000351", "Universitas Brawijaya", "Administrasi", "2025-04-20", "Karyawan Tetap"),
            (200352, "Bagas Kusuma Gunawan", "DSP22", "STF222", 200345, "Strategy Analyst", "Manajerial Junior", "Pria", "bagas.gunawan352@ptsmi.co.id", "6287700000352", "Universitas Indonesia", "Ekonomi", "2025-04-19", "Karyawan Tetap"),
            (200353, "Farhan Ramadhan Wibowo", "DSP22", "STF223", 200345, "Strategy Analyst", "Manajerial Madya", "Pria", "farhan.wibowo353@ptsmi.co.id", "6287700000353", "Telkom University", "Statistika", "2025-04-18", "Karyawan Tetap"),
            (200354, "Dewi Kurniawan Pratama", "DSP22", "STF224", 200345, "Business Analyst", "Manajerial Senior", "Wanita", "dewi.pratama354@ptsmi.co.id", "6287700000354", "Universitas Indonesia", "Manajemen", "2025-04-17", "Karyawan Tetap"),
            (200355, "Indah Lestari Utama", "DSP22", "STF221", 200345, "Operation Analyst", "Manajerial Junior", "Wanita", "indah.utama355@ptsmi.co.id", "6287700000355", "Universitas Hasanuddin", "Administrasi", "2025-04-16", "Karyawan Tetap"),
            (200356, "Putri Wijaya Kurniawan", "DSP22", "STF222", 200345, "Business Analyst", "Manajerial Madya", "Wanita", "putri.kurniawan356@ptsmi.co.id", "6287700000356", "Universitas Mercu Buana", "Statistika", "2025-04-15", "Karyawan Tetap"),
            (200357, "Yuni Kusuma Prasetyo", "DSP22", "STF223", 200345, "Business Analyst", "Manajerial Senior", "Wanita", "yuni.prasetyo357@ptsmi.co.id", "6287700000357", "Universitas Indonesia", "Manajemen", "2025-04-14", "Karyawan Tetap"),
            (200358, "Budi Ramadhan Hidayat", "DSP22", "STF224", 200345, "Strategy Analyst", "Manajerial Junior", "Pria", "budi.hidayat358@ptsmi.co.id", "6287700000358", "Universitas Andalas", "Ekonomi", "2025-04-13", "Karyawan Tetap"),
            (200359, "Joko Kurniawan Siregar", "DSP22", "STF221", 200345, "Operation Analyst", "Manajerial Madya", "Pria", "joko.siregar359@ptsmi.co.id", "6287700000359", "Universitas Indonesia", "Manajemen", "2025-04-12", "Karyawan Tetap"),
            (200360, "Oka Lestari Susanto", "DSP22", "STF222", 200345, "Operation Analyst", "Manajerial Senior", "Pria", "oka.susanto360@ptsmi.co.id", "6287700000360", "Universitas Brawijaya", "Bisnis", "2025-04-11", "Karyawan Tetap"),
            (200361, "Wahyu Wijaya Wijaya", "DSP22", "STF223", 200345, "Strategy Analyst", "Manajerial Junior", "Pria", "wahyu.wijaya361@ptsmi.co.id", "6287700000361", "Universitas Negeri Jakarta", "Statistika", "2025-04-10", "Karyawan Tetap"),
            (200362, "Chandra Kusuma Mahendra", "DSP22", "STF224", 200345, "Business Analyst", "Manajerial Madya", "Pria", "chandra.mahendra362@ptsmi.co.id", "6287700000362", "Universitas Airlangga", "Bisnis", "2025-04-09", "Karyawan Tetap"),
            (200363, "Galih Ramadhan Purnama", "DSP22", "STF221", 200345, "Business Analyst", "Manajerial Senior", "Pria", "galih.purnama363@ptsmi.co.id", "6287700000363", "Universitas Indonesia", "Manajemen", "2025-04-08", "Karyawan Tetap"),
            (200364, "Citra Kurniawan Ananda", "DSP22", "STF222", 200345, "Business Analyst", "Manajerial Junior", "Wanita", "citra.ananda364@ptsmi.co.id", "6287700000364", "Universitas Hasanuddin", "Bisnis", "2025-04-07", "Karyawan Tetap"),
            (200365, "Kartika Lestari Lestari", "DSP22", "STF223", 200345, "Business Analyst", "Manajerial Madya", "Wanita", "kartika.lestari365@ptsmi.co.id", "6287700000365", "Universitas Padjadjaran", "Bisnis", "2025-04-06", "Karyawan Tetap"),
            (200366, "Sari Wijaya Ramadhan", "DSP22", "STF224", 200345, "Business Analyst", "Manajerial Senior", "Wanita", "sari.ramadhan366@ptsmi.co.id", "6287700000366", "Universitas Gunadarma", "Ekonomi", "2025-04-05", "Karyawan Tetap"),
            (200367, "Aulia Kusuma Hartono", "DTI22", "KD221", 200367, "Software Engineer", "Manajerial Executive", "Wanita", "aulia.hartono367@ptsmi.co.id", "6287700000367", "Universitas Negeri Jakarta", "Sistem Informasi", "2025-04-04", "Karyawan Tetap"),
            (200368, "Fajar Ramadhan Saputra", "DTI22", "TL222", 200367, "IT Support", "Manajerial Senior", "Pria", "fajar.saputra368@ptsmi.co.id", "6287700000368", "Universitas Diponegoro", "Teknik Komputer", "2025-04-03", "Karyawan Tetap"),
            (200369, "Lukman Kurniawan Kusuma", "DTI22", "TL222", 200367, "System Analyst", "Manajerial Senior", "Pria", "lukman.kusuma369@ptsmi.co.id", "6287700000369", "Universitas Brawijaya", "Data Science", "2025-04-02", "Karyawan Tetap"),
            (200370, "Rizky Lestari Handoko", "DTI22", "STF221", 200368, "IT Support", "Manajerial Madya", "Pria", "rizky.handoko370@ptsmi.co.id", "6287700000370", "Universitas Sebelas Maret", "Informatika", "2025-04-01", "Karyawan Tetap"),
            (200371, "Zaki Wijaya Syahputra", "DTI22", "STF222", 200368, "Data Engineer", "Manajerial Senior", "Pria", "zaki.syahputra371@ptsmi.co.id", "6287700000371", "Universitas Mercu Buana", "Data Science", "2025-03-31", "Karyawan Tetap"),
            (200372, "Dimas Kusuma Nugroho", "DTI22", "STF223", 200368, "System Analyst", "Manajerial Junior", "Pria", "dimas.nugroho372@ptsmi.co.id", "6287700000372", "Universitas Andalas", "Teknik Komputer", "2025-03-30", "Karyawan Tetap"),
            (200373, "Hafiz Ramadhan Firmansyah", "DTI22", "STF224", 200368, "Data Analyst", "Manajerial Madya", "Pria", "hafiz.firmansyah373@ptsmi.co.id", "6287700000373", "Universitas Gadjah Mada", "Data Science", "2025-03-29", "Karyawan Tetap"),
            (200374, "Gita Kurniawan Febrianto", "DTI22", "STF221", 200368, "Data Analyst", "Manajerial Senior", "Wanita", "gita.febrianto374@ptsmi.co.id", "6287700000374", "Universitas Gunadarma", "Sistem Informasi", "2025-03-28", "Karyawan Tetap"),
            (200375, "Maya Lestari Putri", "DTI22", "STF222", 200368, "IT Support", "Manajerial Junior", "Wanita", "maya.putri375@ptsmi.co.id", "6287700000375", "Institut Teknologi Bandung", "Data Science", "2025-03-27", "Karyawan Tetap"),
            (200376, "Vina Wijaya Permata", "DTI22", "STF223", 200368, "Data Analyst", "Manajerial Madya", "Wanita", "vina.permata376@ptsmi.co.id", "6287700000376", "Universitas Negeri Jakarta", "Teknik Komputer", "2025-03-26", "Karyawan Tetap"),
            (200377, "Andi Kusuma Gunawan", "DTI22", "STF224", 200368, "Software Engineer", "Manajerial Senior", "Pria", "andi.gunawan377@ptsmi.co.id", "6287700000377", "Universitas Negeri Jakarta", "Informatika", "2025-03-25", "Karyawan Tetap"),
            (200378, "Hendra Ramadhan Wibowo", "DTI22", "STF221", 200368, "IT Support", "Manajerial Junior", "Pria", "hendra.wibowo378@ptsmi.co.id", "6287700000378", "Binus University", "AI", "2025-03-24", "Karyawan Tetap"),
            (200379, "Nanda Kurniawan Pratama", "DTI22", "STF222", 200368, "Data Analyst", "Manajerial Madya", "Pria", "nanda.pratama379@ptsmi.co.id", "6287700000379", "Telkom University", "Data Science", "2025-03-23", "Karyawan Tetap"),
            (200380, "Taufik Lestari Utama", "DTI22", "STF223", 200368, "IT Support", "Manajerial Senior", "Pria", "taufik.utama380@ptsmi.co.id", "6287700000380", "Universitas Hasanuddin", "Informatika", "2025-03-22", "Karyawan Tetap"),
            (200381, "Bagas Wijaya Kurniawan", "DTI22", "STF224", 200368, "Data Analyst", "Manajerial Junior", "Pria", "bagas.kurniawan381@ptsmi.co.id", "6287700000381", "Universitas Sebelas Maret", "Sistem Informasi", "2025-03-21", "Karyawan Tetap"),
            (200382, "Farhan Kusuma Prasetyo", "DTI22", "STF221", 200368, "IT Support", "Manajerial Madya", "Pria", "farhan.prasetyo382@ptsmi.co.id", "6287700000382", "Binus University", "AI", "2025-03-20", "Karyawan Tetap"),
            (200383, "Dewi Ramadhan Hidayat", "DTI22", "STF222", 200368, "Software Engineer", "Manajerial Senior", "Wanita", "dewi.hidayat383@ptsmi.co.id", "6287700000383", "Binus University", "Teknik Komputer", "2025-03-19", "Karyawan Tetap"),
            (200384, "Indah Kurniawan Siregar", "DTI22", "STF223", 200368, "IT Support", "Manajerial Junior", "Wanita", "indah.siregar384@ptsmi.co.id", "6287700000384", "Binus University", "Informatika", "2025-03-18", "Karyawan Tetap"),
            (200385, "Putri Lestari Susanto", "DUP22", "KD221", 200385, "Business Analyst", "Manajerial Executive", "Wanita", "putri.susanto385@ptsmi.co.id", "6287700000385", "Universitas Airlangga", "Ekonomi", "2025-03-17", "Karyawan Tetap"),
            (200386, "Yuni Wijaya Wijaya", "DUP22", "TL222", 200385, "Operation Analyst", "Manajerial Senior", "Wanita", "yuni.wijaya386@ptsmi.co.id", "6287700000386", "Universitas Negeri Jakarta", "Statistika", "2025-03-16", "Karyawan Tetap"),
            (200387, "Budi Kusuma Mahendra", "DUP22", "TL222", 200385, "Operation Analyst", "Manajerial Senior", "Pria", "budi.mahendra387@ptsmi.co.id", "6287700000387", "Universitas Padjadjaran", "Ekonomi", "2025-03-15", "Karyawan Tetap"),
            (200388, "Joko Ramadhan Purnama", "DUP22", "STF221", 200386, "Business Analyst", "Manajerial Madya", "Pria", "joko.purnama388@ptsmi.co.id", "6287700000388", "Universitas Sebelas Maret", "Statistika", "2025-03-14", "Karyawan Tetap"),
            (200389, "Oka Kurniawan Ananda", "DUP22", "STF222", 200386, "Strategy Analyst", "Manajerial Senior", "Pria", "oka.ananda389@ptsmi.co.id", "6287700000389", "Universitas Gunadarma", "Statistika", "2025-03-13", "Karyawan Tetap"),
            (200390, "Wahyu Lestari Lestari", "DUP22", "STF223", 200386, "Business Analyst", "Manajerial Junior", "Pria", "wahyu.lestari390@ptsmi.co.id", "6287700000390", "Universitas Gadjah Mada", "Statistika", "2025-03-12", "Karyawan Tetap"),
            (200391, "Chandra Wijaya Ramadhan", "DUP22", "STF224", 200386, "Business Analyst", "Manajerial Madya", "Pria", "chandra.ramadhan391@ptsmi.co.id", "6287700000391", "Universitas Mercu Buana", "Manajemen", "2025-03-11", "Karyawan Tetap"),
            (200392, "Galih Kusuma Hartono", "DUP22", "STF221", 200386, "Business Analyst", "Manajerial Senior", "Pria", "galih.hartono392@ptsmi.co.id", "6287700000392", "Universitas Andalas", "Ekonomi", "2025-03-10", "Karyawan Tetap"),
            (200393, "Citra Ramadhan Saputra", "DUP22", "STF222", 200386, "Strategy Analyst", "Manajerial Junior", "Wanita", "citra.saputra393@ptsmi.co.id", "6287700000393", "Universitas Brawijaya", "Statistika", "2025-03-09", "Karyawan Tetap"),
            (200394, "Kartika Kurniawan Kusuma", "DUP22", "STF223", 200386, "Business Analyst", "Manajerial Madya", "Wanita", "kartika.kusuma394@ptsmi.co.id", "6287700000394", "Universitas Indonesia", "Bisnis", "2025-03-08", "Karyawan Tetap"),
            (200395, "Sari Lestari Handoko", "DUP22", "STF224", 200386, "Operation Analyst", "Manajerial Senior", "Wanita", "sari.handoko395@ptsmi.co.id", "6287700000395", "Universitas Andalas", "Administrasi", "2025-03-07", "Karyawan Tetap"),
            (200396, "Aulia Wijaya Syahputra", "DUP22", "STF221", 200386, "Strategy Analyst", "Manajerial Junior", "Wanita", "aulia.syahputra396@ptsmi.co.id", "6287700000396", "Universitas Negeri Jakarta", "Ekonomi", "2025-03-06", "Karyawan Tetap"),
            (200397, "Fajar Kusuma Nugroho", "DUP22", "STF222", 200386, "Operation Analyst", "Manajerial Madya", "Pria", "fajar.nugroho397@ptsmi.co.id", "6287700000397", "Telkom University", "Administrasi", "2025-03-05", "Karyawan Tetap"),
            (200398, "Lukman Ramadhan Firmansyah", "DUP22", "STF223", 200386, "Strategy Analyst", "Manajerial Senior", "Pria", "lukman.firmansyah398@ptsmi.co.id", "6287700000398", "Universitas Gadjah Mada", "Statistika", "2025-03-04", "Karyawan Tetap"),
            (200399, "Rizky Kurniawan Febrianto", "DUP22", "STF224", 200386, "Operation Analyst", "Manajerial Junior", "Pria", "rizky.febrianto399@ptsmi.co.id", "6287700000399", "Universitas Padjadjaran", "Administrasi", "2025-03-03", "Karyawan Tetap"),
            (200400, "Zaki Lestari Putri", "DUP22", "STF221", 200386, "Operation Analyst", "Manajerial Madya", "Pria", "zaki.putri400@ptsmi.co.id", "6287700000400", "Universitas Gadjah Mada", "Bisnis", "2025-03-02", "Karyawan Tetap"),
            (200401, "Dimas Wijaya Permata", "DUP22", "STF222", 200386, "Operation Analyst", "Manajerial Senior", "Pria", "dimas.permata401@ptsmi.co.id", "6287700000401", "Universitas Airlangga", "Manajemen", "2025-03-01", "Karyawan Tetap"),
            (200402, "Hafiz Kusuma Gunawan", "DUP22", "STF223", 200386, "Strategy Analyst", "Manajerial Junior", "Pria", "hafiz.gunawan402@ptsmi.co.id", "6287700000402", "Universitas Brawijaya", "Manajemen", "2025-02-28", "Karyawan Tetap"),
            (200403, "Gita Ramadhan Wibowo", "DUP22", "STF224", 200386, "Business Analyst", "Manajerial Madya", "Wanita", "gita.wibowo403@ptsmi.co.id", "6287700000403", "Institut Teknologi Bandung", "Bisnis", "2025-02-27", "Karyawan Tetap"),
            (200404, "Maya Kurniawan Pratama", "DUP22", "STF221", 200386, "Strategy Analyst", "Manajerial Senior", "Wanita", "maya.pratama404@ptsmi.co.id", "6287700000404", "Institut Teknologi Bandung", "Administrasi", "2025-02-26", "Karyawan Tetap"),
            (200405, "Vina Lestari Utama", "DUP22", "STF222", 200386, "Business Analyst", "Manajerial Junior", "Wanita", "vina.utama405@ptsmi.co.id", "6287700000405", "Universitas Airlangga", "Manajemen", "2025-02-25", "Karyawan Tetap"),
            (200406, "Andi Wijaya Kurniawan", "DUP22", "STF223", 200386, "Strategy Analyst", "Manajerial Madya", "Pria", "andi.kurniawan406@ptsmi.co.id", "6287700000406", "Universitas Airlangga", "Administrasi", "2025-02-24", "Karyawan Tetap"),
            (200407, "Hendra Kusuma Prasetyo", "DUP22", "STF224", 200386, "Operation Analyst", "Manajerial Senior", "Pria", "hendra.prasetyo407@ptsmi.co.id", "6287700000407", "Universitas Gunadarma", "Statistika", "2025-02-23", "Karyawan Tetap"),
            (200408, "Nanda Ramadhan Hidayat", "DUP22", "STF221", 200386, "Business Analyst", "Manajerial Junior", "Pria", "nanda.hidayat408@ptsmi.co.id", "6287700000408", "Universitas Hasanuddin", "Statistika", "2025-02-22", "Karyawan Tetap"),
            (200409, "Taufik Kurniawan Siregar", "DUP22", "STF222", 200386, "Operation Analyst", "Manajerial Madya", "Pria", "taufik.siregar409@ptsmi.co.id", "6287700000409", "Universitas Indonesia", "Ekonomi", "2025-02-21", "Karyawan Tetap"),
            (200410, "Bagas Lestari Susanto", "DUP22", "STF223", 200386, "Operation Analyst", "Manajerial Senior", "Pria", "bagas.susanto410@ptsmi.co.id", "6287700000410", "Telkom University", "Statistika", "2025-02-20", "Karyawan Tetap"),
            (200411, "Farhan Wijaya Wijaya", "DUS22", "KD221", 200411, "Operation Analyst", "Manajerial Executive", "Pria", "farhan.wijaya411@ptsmi.co.id", "6287700000411", "Universitas Andalas", "Administrasi", "2025-02-19", "Karyawan Tetap"),
            (200412, "Dewi Kusuma Mahendra", "DUS22", "TL222", 200411, "Strategy Analyst", "Manajerial Senior", "Wanita", "dewi.mahendra412@ptsmi.co.id", "6287700000412", "Universitas Andalas", "Ekonomi", "2025-02-18", "Karyawan Tetap"),
            (200413, "Indah Ramadhan Purnama", "DUS22", "TL222", 200411, "Operation Analyst", "Manajerial Senior", "Wanita", "indah.purnama413@ptsmi.co.id", "6287700000413", "Universitas Padjadjaran", "Administrasi", "2025-02-17", "Karyawan Tetap"),
            (200414, "Putri Kurniawan Ananda", "DUS22", "STF221", 200412, "Business Analyst", "Manajerial Madya", "Wanita", "putri.ananda414@ptsmi.co.id", "6287700000414", "Universitas Hasanuddin", "Statistika", "2025-02-16", "Karyawan Tetap"),
            (200415, "Yuni Lestari Lestari", "DUS22", "STF222", 200412, "Business Analyst", "Manajerial Senior", "Wanita", "yuni.lestari415@ptsmi.co.id", "6287700000415", "Telkom University", "Administrasi", "2025-02-15", "Karyawan Tetap"),
            (200416, "Budi Wijaya Ramadhan", "DUS22", "STF223", 200412, "Strategy Analyst", "Manajerial Junior", "Pria", "budi.ramadhan416@ptsmi.co.id", "6287700000416", "Universitas Padjadjaran", "Bisnis", "2025-02-14", "Karyawan Tetap"),
            (200417, "Joko Kusuma Hartono", "DUS22", "STF224", 200412, "Business Analyst", "Manajerial Madya", "Pria", "joko.hartono417@ptsmi.co.id", "6287700000417", "Universitas Gunadarma", "Manajemen", "2025-02-13", "Karyawan Tetap"),
            (200418, "Oka Ramadhan Saputra", "DUS22", "STF221", 200412, "Business Analyst", "Manajerial Senior", "Pria", "oka.saputra418@ptsmi.co.id", "6287700000418", "Universitas Brawijaya", "Bisnis", "2025-02-12", "Karyawan Tetap"),
            (200419, "Wahyu Kurniawan Kusuma", "DUS22", "STF222", 200412, "Strategy Analyst", "Manajerial Junior", "Pria", "wahyu.kusuma419@ptsmi.co.id", "6287700000419", "Telkom University", "Administrasi", "2025-02-11", "Karyawan Tetap"),
            (200420, "Chandra Lestari Handoko", "DUS22", "STF223", 200412, "Operation Analyst", "Manajerial Madya", "Pria", "chandra.handoko420@ptsmi.co.id", "6287700000420", "Universitas Negeri Jakarta", "Ekonomi", "2025-02-10", "Karyawan Tetap"),
            (200421, "Galih Wijaya Syahputra", "DUS22", "STF224", 200412, "Business Analyst", "Manajerial Senior", "Pria", "galih.syahputra421@ptsmi.co.id", "6287700000421", "Universitas Mercu Buana", "Manajemen", "2025-02-09", "Karyawan Tetap"),
            (200422, "Citra Kusuma Nugroho", "DUS22", "STF221", 200412, "Operation Analyst", "Manajerial Junior", "Wanita", "citra.nugroho422@ptsmi.co.id", "6287700000422", "Universitas Sebelas Maret", "Administrasi", "2025-02-08", "Karyawan Tetap"),
            (200423, "Kartika Ramadhan Firmansyah", "DUS22", "STF222", 200412, "Strategy Analyst", "Manajerial Madya", "Wanita", "kartika.firmansyah423@ptsmi.co.id", "6287700000423", "Universitas Hasanuddin", "Statistika", "2025-02-07", "Karyawan Tetap"),
            (200424, "Sari Kurniawan Febrianto", "DUS22", "STF223", 200412, "Operation Analyst", "Manajerial Senior", "Wanita", "sari.febrianto424@ptsmi.co.id", "6287700000424", "Universitas Gunadarma", "Bisnis", "2025-02-06", "Karyawan Tetap"),
            (200425, "Aulia Lestari Putri", "DUS22", "STF224", 200412, "Strategy Analyst", "Manajerial Junior", "Wanita", "aulia.putri425@ptsmi.co.id", "6287700000425", "Universitas Negeri Jakarta", "Manajemen", "2025-02-05", "Karyawan Tetap"),
        ]


        # NIK mapping
        ADMINISTRATOR_NIKS = {200335, 200331, 200329}
        HEAD_OF_DIVISION_NIKS = {
            200001, 200022, 200033, 200053, 200068, 200094, 200106, 200118,
            200135, 200157, 200167, 200178, 200193, 200203, 200214, 200234,
            200253, 200261, 200282, 200294, 200307, 200317, 200344, 200367,
            200385, 200411
        }
        TEAM_LEADER_NIKS = {
            200002, 200003, 200023, 200024, 200034, 200035, 200054, 200055,
            200069, 200070, 200095, 200096, 200107, 200108, 200119, 200120,
            200136, 200137, 200158, 200159, 200168, 200169, 200179, 200180,
            200194, 200195, 200204, 200205, 200215, 200216, 200235, 200236,
            200254, 200255, 200262, 200263, 200283, 200284, 200295, 200296,
            200308, 200309, 200318, 200345, 200346, 200368, 200369,
            200386, 200387, 200412, 200413
        }
        DEAN_NIKS = {200319}

        def get_group_name(nik):
            """Determine the authentication group for a given NIK."""
            if nik in ADMINISTRATOR_NIKS:
                return 'Administrator'
            if nik in HEAD_OF_DIVISION_NIKS:
                return 'Head of Division'
            if nik in DEAN_NIKS:
                return 'Dean'
            if nik in TEAM_LEADER_NIKS:
                return 'Team Leader'
            return 'Employee'

        # Pre-fetch groups
        groups_cache = {}
        for gn in group_names:
            try:
                groups_cache[gn] = Group.objects.get(name=gn)
            except Group.DoesNotExist:
                pass

        # Phase 1: Create all employees without self-referencing supervisor first
        created_count = 0
        skipped_count = 0

        for i, emp_data in enumerate(employees_data, 1):
            nik = emp_data[0]
            if Employee.objects.filter(nik=nik).exists():
                skipped_count += 1
                continue

            position_code = emp_data[3]
            position_name = POSITION_MAP.get(position_code, 'Staff')

            emp = Employee(
                nik=nik,
                full_name=emp_data[1],
                division_id=emp_data[2],
                position_name=position_name,
                direct_supervisor=None,
                special_position=emp_data[5],
                level=emp_data[6],
                gender=emp_data[7],
                email=emp_data[8],
                phone=emp_data[9],
                university=emp_data[10],
                major=emp_data[11],
                entry_date=emp_data[12],
                employment_status=emp_data[13],
            )
            emp.save()
            created_count += 1
            
            if i % 50 == 0:
                self.stdout.write(f'  ... processed {i}/425 employees')

        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created_count} employees, skipped {skipped_count}'))

        # Phase 2: Link supervisors
        self.stdout.write('  Linking supervisors...')
        for emp_data in employees_data:
            nik = emp_data[0]
            supervisor_nik = emp_data[4]
            try:
                emp = Employee.objects.get(nik=nik)
                if emp.direct_supervisor_id != supervisor_nik:
                    emp.direct_supervisor_id = supervisor_nik
                    emp.save(update_fields=['direct_supervisor_id'])
            except Employee.DoesNotExist:
                pass

        self.stdout.write(self.style.SUCCESS('  [OK] Supervisors linked'))

        # Assign auth group to user
        self.stdout.write('\nAssigning authentication groups...')
        group_counts = {}

        for emp_data in employees_data:
            nik = emp_data[0]
            email = emp_data[8]
            target_group_name = get_group_name(nik)

            try:
                user = User.objects.get(username=email)
                user.groups.clear()
                if target_group_name in groups_cache:
                    user.groups.add(groups_cache[target_group_name])
                    group_counts[target_group_name] = group_counts.get(target_group_name, 0) + 1
            except User.DoesNotExist:
                pass

        for gn, count in sorted(group_counts.items()):
            self.stdout.write(self.style.SUCCESS(f'  [OK] {gn}: {count} users'))

       
        self.stdout.write('\nSeeding Hotels...')
        hotels_data = [
            ("H101", "Jakarta", "Hotel Indonesia Kempinski", "0212356789", 2500000.00, 5),
            ("H102", "Jakarta", "Pullman Jakarta Central", "0218765432", 1800000.00, 5),
            ("H103", "Jakarta", "The Ritz-Carlton Jakarta", "0219988776", 2200000.00, 5),
            ("H104", "Jakarta", "Mercure Jakarta Sabang", "0213344556", 1200000.00, 4),
            ("H105", "Bandung", "Grand Mercure Bandung", "022867792", 1300000.00, 5),
            ("H106", "Bandung", "Hilton Bandung", "0223344556", 1500000.00, 5),
            ("H107", "Bandung", "Ibis Bandung Trans Studio", "0229988776", 900000.00, 3),
            ("H108", "Bandung", "The Trans Luxury Hotel", "0225566778", 2000000.00, 5),
            ("H109", "Bali", "The Legian Bali", "0361789876", 3500000.00, 5),
            ("H110", "Bali", "Grand Hyatt Bali", "0361781234", 3200000.00, 5),
            ("H111", "Bali", "Padma Resort Legian", "0361776543", 2800000.00, 5),
            ("H112", "Yogyakarta", "Malioboro Hotel", "0274345678", 900000.00, 3),
            ("H113", "Yogyakarta", "Sheraton Mustika Yogyakarta", "0274348765", 1700000.00, 5),
            ("H114", "Surabaya", "JW Marriott Surabaya", "0315678901", 2000000.00, 5),
            ("H115", "Surabaya", "Hotel Majapahit", "0313344556", 1800000.00, 5),
            ("H116", "Bogor", "Novotel Bogor Golf Resort", "0251789001", 1300000.00, 4),
            ("H117", "Bogor", "The Highland Park Resort", "0251789002", 1100000.00, 4),
            ("H118", "Semarang", "Grand Candi Semarang", "0247654321", 1200000.00, 4),
            ("H119", "Semarang", "Hotel Ciputra Semarang", "0243344556", 1000000.00, 4),
            ("H120", "Semarang", "MG Suites Semarang", "0249988776", 900000.00, 3),
        ]
        h_created = 0
        h_skipped = 0
        for h_id, h_city, h_name, h_phone, h_price, h_star in hotels_data:
            obj, created = Hotel.objects.get_or_create(
                hotel_id=h_id,
                defaults={
                    'hotel_city': h_city,
                    'hotel_name': h_name,
                    'hotel_phone': h_phone,
                    'price_estimation': h_price,
                    'hotel_star': h_star,
                }
            )
            if created:
                h_created += 1
            else:
                h_skipped += 1
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {h_created} hotels, skipped {h_skipped}'))

        self.stdout.write('\nSeeding Course Categories...')
        course_categories_data = [
            ("BD26", "Business Development", "Pengembangan peluang bisnis melalui strategi pertumbuhan yang terukur dan berkelanjutan."),
            ("BK26", "Business Knowledge", "Pemahaman menyeluruh terkait konsep, proses, dan praktik bisnis untuk mendukung pengambilan keputusan."),
            ("CC26", "Core Competency", "Penguatan kompetensi inti sebagai fondasi dalam menjalankan peran dan tanggung jawab pekerjaan."),
            ("CE26", "Credit Excellence", "Peningkatan kualitas analisis kredit melalui pendekatan yang akurat, objektif, dan berbasis risiko."),
            ("CM26", "Client Management", "Pengelolaan hubungan klien secara efektif untuk meningkatkan kepuasan dan loyalitas pelanggan."),
            ("FN26", "Financing", "Pengelolaan strategi pembiayaan untuk mendukung pertumbuhan bisnis secara berkelanjutan."),
            ("FT26", "Finance & Treasury", "Optimalisasi pengelolaan keuangan dan likuiditas organisasi secara efisien dan terkontrol."),
            ("GA26", "General Administration", "Pelaksanaan fungsi administrasi yang sistematis dan terstruktur guna mendukung operasional organisasi."),
            ("GRC26", "Governance, Risk, Compliance", "Penerapan tata kelola, manajemen risiko, dan kepatuhan untuk menjaga integritas organisasi."),
            ("HC26", "Human Capital", "Pengembangan dan pengelolaan sumber daya manusia untuk meningkatkan kinerja dan produktivitas organisasi."),
            ("IT26", "IT & Analytics", "Pemanfaatan teknologi informasi dan analitik data untuk mendukung pengambilan keputusan berbasis data."),
            ("PD26", "Personal Development", "Pengembangan potensi diri melalui peningkatan keterampilan personal dan profesional secara berkelanjutan."),
            ("PM26", "Product Management", "Pengelolaan siklus hidup produk secara strategis untuk menciptakan nilai dan daya saing."),
            ("PRD26", "Project Development", "Transformasi ide strategis melalui pengelolaan siklus hidup proyek yang terstruktur dan berorientasi pada hasil."),
            ("SU26", "Sustainability", "Penerapan prinsip keberlanjutan dalam operasional bisnis untuk menciptakan dampak jangka panjang."),
        ]

        cc_created = 0
        cc_skipped = 0
        for cc_id, cc_name, cc_desc in course_categories_data:
            obj, created = CourseCategory.objects.get_or_create(
                course_category_id=cc_id,
                defaults={
                    'category_name': cc_name,
                    'description': cc_desc,
                }
            )
            if created:
                cc_created += 1
            else:
                cc_skipped += 1
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {cc_created} course categories, skipped {cc_skipped}'))

        self.stdout.write('\nSeeding Courses...')
        courses_data = [
            ("AIHC26", "HC26", "AI Knowledge", "Pemahaman kecerdasan buatan untuk mendukung pengelolaan SDM"),
            ("AIIT26", "IT26", "AI Knowledge", "Pemanfaatan kecerdasan buatan dalam teknologi informasi"),
            ("AIPD26", "PD26", "AI Knowledge", "Pemanfaatan AI untuk pengembangan diri"),
            ("AM26", "CM26", "Account Management", "Pengelolaan hubungan dengan klien untuk meningkatkan loyalitas"),
            ("AN26", "PD26", "Analysing", "Kemampuan analisis dalam pengambilan keputusan"),
            ("APG26", "PD26", "Achieving Personal Work Goals & Objectives", "Pencapaian target kerja individu secara efektif"),
            ("AS26", "CM26", "Advisory Skill", "Kemampuan memberikan saran profesional kepada klien"),
            ("BA26", "BK26", "Business Analysis", "Analisis kebutuhan bisnis untuk meningkatkan efektivitas operasional"),
            ("BAN26", "BK26", "Business Acumen", "Kemampuan memahami kondisi bisnis untuk pengambilan keputusan yang tepat"),
            ("BD26", "BD26", "Business Development", "Pengembangan peluang bisnis untuk meningkatkan pertumbuhan perusahaan secara berkelanjutan"),
            ("BI26", "CM26", "Business Insight", "Kemampuan memahami kebutuhan bisnis klien secara mendalam"),
            ("BK26", "BK26", "Banking Knowledge", "Pemahaman dasar tentang industri perbankan dan operasionalnya"),
            ("BOT26", "PD26", "Building Organizational Talent", "Pengembangan talenta dalam organisasi"),
            ("BPI26", "PD26", "Business Process Improvements", "Peningkatan proses bisnis untuk efisiensi kerja"),
            ("BSD26", "BD26", "Business Strategy", "Perumusan strategi bisnis untuk mencapai keunggulan kompetitif perusahaan"),
            ("BSK26", "BK26", "Business Strategy", "Perencanaan strategi bisnis untuk mencapai tujuan organisasi"),
            ("CA26", "CE26", "Credit Analysis", "Analisis kelayakan kredit untuk meminimalkan risiko"),
            ("CC26", "CC26", "Corporate Culture", "Pemahaman budaya organisasi untuk meningkatkan kinerja"),
            ("CCI26", "BK26", "Corporate Culture Internalization", "Pemahaman dan penerapan budaya perusahaan dalam pekerjaan"),
            ("CF26", "FT26", "Corporate Finance", "Pengelolaan keuangan perusahaan untuk meningkatkan nilai bisnis"),
            ("CFN26", "FN26", "Commercial Financing", "Pengelolaan pembiayaan komersial untuk mendukung kebutuhan bisnis"),
            ("CMK26", "FT26", "Capital Market Knowledge", "Pemahaman pasar modal untuk investasi dan pembiayaan"),
            ("CMO26", "CE26", "Credit Monitoring", "Pemantauan kredit untuk memastikan kualitas portofolio"),
            ("CMPD26", "PD26", "Conflict Management", "Pengelolaan konflik dalam lingkungan kerja"),
            ("CRT26", "PD26", "Critical Thinking", "Kemampuan berpikir kritis untuk pengambilan keputusan"),
            ("CS26", "BK26", "Communication Skill", "Kemampuan komunikasi efektif dalam lingkungan profesional"),
            ("CSGRC26", "GRC26", "Communication Skill", "Kemampuan komunikasi efektif dalam penerapan governance"),
            ("CSPD26", "PD26", "Communication Skill", "Komunikasi efektif dalam pengembangan pribadi"),
            ("CT26", "PD26", "Creative Thinking", "Kemampuan berpikir kreatif dalam menyelesaikan masalah"),
            ("DA26", "IT26", "Data Analytics", "Analisis data untuk menghasilkan insight bisnis yang akurat"),
            ("DM26", "PD26", "Decision Making", "Pengambilan keputusan secara tepat dan efektif"),
            ("DP26", "PD26", "Diplomacy", "Kemampuan diplomasi dalam hubungan profesional"),
            ("DR26", "CM26", "Delivering Results & Meeting Customer Expectations", "Kemampuan memenuhi ekspektasi pelanggan secara optimal"),
            ("DRPD26", "PD26", "Delivering Results & Meeting Customer Expectations", "Pencapaian hasil kerja sesuai ekspektasi"),
            ("DT26", "PD26", "Design Thinking", "Pendekatan inovatif dalam pemecahan masalah"),
            ("EI26", "FT26", "Equity Investment", "Strategi investasi saham untuk optimalisasi keuntungan"),
            ("EMA26", "BK26", "Economic & Market Analysis", "Analisis kondisi ekonomi dan pasar untuk mendukung strategi bisnis"),
            ("ENT26", "PD26", "Entrepreneurship", "Pengembangan jiwa kewirausahaan"),
            ("ESG26", "BK26", "Environment, Social, Governance (ESG)", "Penerapan prinsip ESG dalam aktivitas bisnis perusahaan"),
            ("ESGGRC26", "GRC26", "Environment, Social, Governance (ESG)", "Penerapan prinsip ESG dalam tata kelola perusahaan"),
            ("ESGSU26", "SU26", "Environment, Social, Governance (ESG)", "Penerapan prinsip keberlanjutan dalam bisnis"),
            ("FA26", "FT26", "Financial Accounting", "Pencatatan dan pelaporan keuangan sesuai standar akuntansi"),
            ("FMA26", "FT26", "Financial Modeling & Analysis", "Pembuatan model keuangan untuk analisis bisnis"),
            ("FNF26", "FT26", "Finance for Non-Finance", "Pemahaman dasar keuangan bagi non-financial professional"),
            ("GA26", "GA26", "General Administration", "Pengelolaan administrasi umum untuk mendukung operasional organisasi"),
            ("HCM26", "HC26", "Human Capital Management", "Pengelolaan sumber daya manusia secara strategis"),
            ("IN26", "CC26", "Innovation", "Kemampuan menciptakan inovasi untuk meningkatkan daya saing"),
            ("ITMGA26", "GA26", "IT Management", "Pengelolaan sistem teknologi informasi dalam organisasi"),
            ("ITMITT26", "IT26", "IT Management", "Pengelolaan infrastruktur dan layanan teknologi informasi"),
            ("ITMSU26", "SU26", "IT Management", "Pengelolaan IT untuk mendukung keberlanjutan organisasi"),
            ("ITP26", "IT26", "IT Planning & Organizing", "Perencanaan dan pengorganisasian strategi IT"),
            ("LGN26", "BD26", "Lead Generation & Networking", "Strategi membangun jaringan dan menghasilkan prospek bisnis baru"),
            ("LK26", "BK26", "Legal Knowledge", "Pemahaman aspek hukum dalam kegiatan bisnis"),
            ("LKGRC26", "GRC26", "Legal Knowledge", "Pemahaman hukum untuk memastikan kepatuhan organisasi"),
            ("LO26", "PD26", "Leadership Orientation", "Pengembangan jiwa kepemimpinan"),
            ("ME26", "PD26", "Managing Execution", "Pengelolaan pelaksanaan pekerjaan secara efektif"),
            ("MS26", "BK26", "Marketing Skill", "Kemampuan pemasaran untuk meningkatkan nilai produk dan layanan"),
            ("MSPM26", "PM26", "Marketing Skill", "Kemampuan pemasaran dalam pengelolaan produk"),
            ("MSV26", "CM26", "Marketing Skill", "Kemampuan pemasaran dalam pengelolaan klien"),
            ("NG26", "BD26", "Negotiation", "Kemampuan negosiasi untuk mencapai kesepakatan yang menguntungkan semua pihak"),
            ("PAG26", "PM26", "Product Analytics & Growth", "Analisis produk untuk pertumbuhan bisnis"),
            ("PF26", "BK26", "Public Financing", "Pemahaman pembiayaan publik dalam sektor keuangan"),
            ("PFN26", "FT26", "Project Finance", "Pembiayaan proyek untuk mendukung pengembangan bisnis"),
            ("PFNG26", "FN26", "Public Financing", "Pengelolaan pembiayaan publik untuk proyek dan institusi"),
            ("PFPD26", "PD26", "Performance Focus", "Fokus pada pencapaian kinerja optimal"),
            ("PGO26", "PD26", "Personal Growth Orientation", "Pengembangan diri secara berkelanjutan"),
            ("PI26", "PD26", "Persuading & Influencing", "Kemampuan mempengaruhi dan meyakinkan pihak lain"),
            ("PM26", "BK26", "Product Management", "Pengelolaan produk dari perencanaan hingga evaluasi"),
            ("PMPRD26", "PRD26", "Project Management", "Pengelolaan proyek untuk mencapai target secara efektif"),
            ("PMSU26", "SU26", "Project Management", "Manajemen proyek berbasis keberlanjutan"),
            ("PO26", "PD26", "Planning & Organizing", "Perencanaan dan pengorganisasian pekerjaan"),
            ("PS26", "PD26", "Presentation Skill", "Kemampuan presentasi yang efektif"),
            ("RMGA26", "GA26", "Risk Management", "Identifikasi dan pengelolaan risiko untuk menjaga stabilitas bisnis"),
            ("RMGRC26", "GRC26", "Risk Management", "Pengelolaan risiko untuk memastikan keberlangsungan bisnis"),
            ("RMSU26", "SU26", "Risk Management", "Pengelolaan risiko dalam konteks sustainability"),
            ("RN26", "CM26", "Relating & Networking", "Kemampuan membangun hubungan profesional yang luas"),
            ("RNPD26", "PD26", "Relating & Networking", "Membangun relasi profesional"),
            ("SAM26", "FN26", "Special Asset Management", "Pengelolaan aset khusus untuk meminimalkan risiko kerugian"),
            ("SF26", "FN26", "Sharia Financing", "Pembiayaan berbasis prinsip syariah sesuai regulasi yang berlaku"),
            ("SFGRC26", "GRC26", "Sharia Financing", "Penerapan pembiayaan syariah dalam kerangka compliance"),
            ("SFN26", "FN26", "Sustainable Financing", "Pembiayaan berkelanjutan yang memperhatikan aspek lingkungan dan sosial"),
            ("SFSU26", "SU26", "Sustainable Financing", "Pembiayaan berkelanjutan untuk mendukung ESG"),
            ("SM26", "CM26", "Stakeholder Management", "Pengelolaan hubungan dengan stakeholder secara efektif"),
            ("SMPRD26", "PRD26", "Stakeholder Management", "Pengelolaan stakeholder dalam proyek"),
            ("SOP26", "GRC26", "SOP Writing", "Penyusunan standar operasional prosedur secara sistematis"),
            ("TC26", "PD26", "Teamwork & Cooperation", "Kerja sama tim yang efektif"),
            ("TF26", "FT26", "Trade Finance", "Pengelolaan pembiayaan perdagangan internasional"),
            ("TM26", "FT26", "Treasury Management", "Pengelolaan kas dan likuiditas perusahaan"),
            ("TMPD26", "PD26", "Time Management", "Pengelolaan waktu secara efisien"),
            ("TX26", "FT26", "Taxation", "Pemahaman perpajakan dalam kegiatan bisnis"),
            ("WS26", "PD26", "Writing Skill", "Kemampuan menulis profesional"),
        ]

        c_created = 0
        c_skipped = 0
        for c_id, cc_id, c_name, c_desc in courses_data:
            obj, created = Course.objects.get_or_create(
                course_id=c_id,
                defaults={
                    'course_category_id': cc_id,
                    'course_name': c_name,
                    'description': c_desc,
                }
            )
            if created:
                c_created += 1
            else:
                c_skipped += 1
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {c_created} courses, skipped {c_skipped}'))

       
        # Hotel seeding removed from here and moved earlier.

       
        self.stdout.write('\nSeeding Vendors...')
        vendors_data = [
            ("BDO", "BDO Indonesia", "External", "Dina Lestari", "Audit Consulting", "Jl. Sudirman No.5", "Jakarta Selatan", "DKI Jakarta", "Indonesia", "40123", "6286655778899", "022-556644", "info@bdo.id", "www.bdo.id", True),
            ("BI", "Bank Indonesia", "External", "Riko Saputra", "Bank Central", "Jl. Merdeka No.9", "Jakarta Pusat", "DKI Jakarta", "Indonesia", "41361", "6281122998877", "0267-778899", "info@bi.id", "www.bi.id", True),
            ("BMS", "Brainmatics", "External", "Dewi Lestari", "Information Technology", "Jl. Asia Afrika No.10", "Bandung", "Jawa Barat", "Indonesia", "40111", "6287766554433", "022-556677", "support@brainmatics.id", "www.brainmatics.id", True),
            ("DDI", "Development Dimensions International Indonesia", "External", "Rina Wijaya", "Leadership Consulting", "Jl. Merdeka No.20", "Bandung", "Jawa Barat", "Indonesia", "40115", "6283344556677", "022-334455", "info@ddi.id", "www.ddi.id", True),
            ("DJP", "Direktorat Jenderal Pajak", "External", "Yusuf Ali", "Perpajakan", "Jl. SDM No.4", "Jakarta Timur", "DKI Jakarta", "Indonesia", "13450", "6281122337788", "021-667799", "info@djp.id", "www.djp.id", True),
            ("DTI", "Deloitte Indonesia", "External", "Hendra Gunawan", "Audit Consulting", "Jl. Pendidikan No.3", "Jakarta Pusat", "DKI Jakarta", "Indonesia", "16424", "6285566778899", "021-667788", "support@deloitte.id", "www.deloitte.id", True),
            ("EGC", "EnergyCore", "External", "Putri Ayu", "Energy System", "Jl. Energi No.3", "Balikpapan", "Kalimantan Timur", "Indonesia", "76114", "6283344112299", "0542-667788", "energy@core.id", "www.energycore.id", True),
            ("EGE", "Edugate", "External", "Nina Putri", "Information Technology", "Jl. Diponegoro No.7", "Surabaya", "Jawa Timur", "Indonesia", "60241", "6281122334455", "031-998877", "support@edugate.id", "www.edugate.id", True),
            ("ESQ", "ESQ Masa Persiapan Pensiun", "External", "Joko Riswoyo", "Konusultan Training", "Jl. Gatot Subroto No.5", "Jakarta Pusat", "DKI Jakarta", "Indonesia", "65145", "6282211334455", "0341-556677", "admin@esq.id", "www.esq.id", True),
            ("FAS", "FinAnalytics", "External", "Kevin Wijaya", "Financial Analytics", "Jl. Bursa No.10", "Jakarta Selatan", "DKI Jakarta", "Indonesia", "12150", "6289988772233", "021-778899", "fin@analytics.id", "www.finanalytics.id", True),
            ("GBC", "Green Building Council Indonesia", "External", "Nadia Putri", "Sustainbility", "Jl. Kampus No.8", "Depok", "Jawa Barat", "Indonesia", "16425", "6281122558899", "021-334455", "admin@gbci.id", "www.gbci.id", True),
            ("HLP", "HealthPlus", "External", "Sari Dewi", "Healthcare IT", "Jl. Kesehatan No.9", "Bogor", "Jawa Barat", "Indonesia", "16111", "6287788990011", "0251-223344", "health@plus.id", "www.healthplus.id", True),
            ("IDX", "PT Bursa Efek Indonesia", "External", "Bagus Santoso", "Pasar Modal", "Jl. Gatot Subroto No.1", "Jakarta Pusat", "DKI Jakarta", "Indonesia", "90111", "6288877665544", "0411-223344", "info@idx.id", "www.idx.id", True),
            ("IVT", "Iverson Technology", "External", "Rizkia Amanda", "Information Technology", "Jl. Danau Sunter Utara No.3-4", "Jakarta Utara", "DKI Jakarta", "Indonesia", "14350", "6285167872534", "(62-51) 7082 3257", "admin@inverson.com", "www.inverson.co.id", True),
            ("JTC", "Justitia Training Center", "External", "Lina Kartika", "Konsultan Hukum", "Jl. Pariwisata No.2", "Denpasar", "Bali", "Indonesia", "80227", "6289988771122", "0361-223344", "info@justitita.id", "www.justitita.id", True),
            ("LSP", "LSP Universitas Indonesia", "External", "Maya Sari", "Pendidikan", "Jl. Margonda No.11", "Depok", "Jawa Barat", "Indonesia", "10710", "6284455667788", "021-889900", "admin@lspui.id", "www.lspui.id", True),
            ("MI", "Mercer Indonesia", "External", "Doni Prasetyo", "Human Resources Consulting", "Jl. Merdeka No.14", "Jakarta Pusat", "DKI Jakarta", "Indonesia", "60123", "6285544332211", "031-445566", "support@mercer.id", "www.mercer.id", True),
            ("MPI", "MarkPlus Institute", "External", "Agus Salim", "Konsultasi Pemasaran", "Jl. Ahmad Yani No.15", "Semarang", "Jawa Tengah", "Indonesia", "50241", "6289988112233", "024-445566", "info@markplus.id", "www.markplusins.id", True),
            ("NCSR", "National Center for Corporate Reporting", "External", "Rizal Hadi", "Sustainbility", "Jl. Firewall No.2", "Jakarta Barat", "DKI Jakarta", "Indonesia", "11530", "6289988223344", "021-445566", "info@ncsr.id", "www.ncsr.id", True),
            ("PPM", "PPM Manajemen", "External", "Arif Rahman", "Human Resources Consulting", "Jl. Broadcasting No.6", "Jakarta Selatan", "DKI Jakarta", "Indonesia", "12190", "6286677001122", "021-998800", "admin@ppm.id", "www.ppm.id", True),
            ("PWC", "PWC Indonesia", "External", "Rudi Hartono", "Consulting and Finance Services", "Jl. Malioboro No.1", "Yogyakarta", "DI Yogyakarta", "Indonesia", "55213", "6286677889900", "0274-123456", "info@pwc.co.id", "www.pwc.co.id", True),
            ("RAI", "Robere & Associates Indonesia", "External", "Fajar Nugroho", "Management Consulting Firm", "Jl. Sudirman No.21", "Jakarta Selatan", "DKI Jakarta", "Indonesia", "17530", "6286655443322", "021-776655", "support@robereandassociates.id", "www.robereandassociates.id", True),
            ("SME", "SMI Eksternal", "External", "Siti Rahma", "Financial Institution", "Jl. Sudirman No.8", "Jakarta Pusat", "DKI Jakarta", "Indonesia", "12930", "6282233445566", "021-998877", "contact@smi.id", "www.smi.id", True),
            ("SMI", "SMI Internal", "Internal", "Andi Saputra", "Financial Institution", "Jl. Sudirman No.8", "Jakarta Pusat", "DKI Jakarta", "Indonesia", "12930", "6282233445566", "021-998877", "contact@smi.id", "www.smi.id", True),
            ("TCI", "Trainicate Indonesia", "Exsternal", "Budi Santoso", "Cloud Services", "Jl. Thamrin No.5", "Jakarta Pusat", "DKI Jakarta", "Indonesia", "10350", "6289988776655", "021-112233", "support@trainicate.id", "www.trainicate.id", True),
        ]

        v_created = 0
        v_skipped = 0
        for v_id, v_name, v_type, p_name, spec, addr, city, prov, country, post, phone, fax, email, web, active in vendors_data:
            obj, created = Vendor.objects.get_or_create(
                vendor_id=v_id,
                defaults={
                    'vendor_name': v_name,
                    'provider_type': v_type,
                    'pic_name': p_name,
                    'speciality': spec,
                    'address': addr,
                    'city': city,
                    'province': prov,
                    'country': country,
                    'postcode': post,
                    'phone': phone,
                    'fax': fax,
                    'email': email,
                    'web_address': web,
                    'is_active': active,
                }
            )
            if created:
                v_created += 1
            else:
                v_skipped += 1
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {v_created} vendors, skipped {v_skipped}'))

      
        self.stdout.write('\nSeeding TNA Data...')

        TnaParticipant.objects.all().delete()
        TnaMaster.objects.all().delete()
        TnaPeriod.objects.all().delete()

        period, created = TnaPeriod.objects.get_or_create(
            tna_period_id=1,
            defaults={
                'period_code': "TNA-2026",
                'year': 2026,
                'period_name': "Training Needs Analysis 2026",
                'open_date': "2026-01-01",
                'close_date': "2026-12-31",
                'status': "Open",
            }
        )
        self.stdout.write(self.style.SUCCESS('  [OK] Seeded TNA Period'))

        tna_master_data = [
            ("BD26BD26", 1, "BD26", "BD26", 1, 200335),
            ("BD26BSD26", 1, "BD26", "BSD26", 1, 200335),
            ("BD26LGN26", 1, "BD26", "LGN26", 1, 200331),
            ("BD26NG26", 1, "BD26", "NG26", 1, 200335),
            ("BK26BA26", 1, "BK26", "BA26", 2, 200335),
            ("BK26BAN26", 1, "BK26", "BAN26", 2, 200335),
            ("BK26BK26", 1, "BK26", "BK26", 2, 200331),
            ("BK26BSK26", 1, "BK26", "BSK26", 2, 200331),
            ("BK26CCI26", 1, "BK26", "CCI26", 2, 200329),
            ("BK26CS26", 1, "BK26", "CS26", 2, 200331),
            ("BK26EMA26", 1, "BK26", "EMA26", 2, 200335),
            ("BK26ESG26", 1, "BK26", "ESG26", 2, 200329),
            ("BK26LK26", 1, "BK26", "LK26", 2, 200331),
            ("BK26MS26", 1, "BK26", "MS26", 2, 200331),
            ("BK26PF26", 1, "BK26", "PF26", 2, 200331),
            ("BK26PM26", 1, "BK26", "PM26", 2, 200329),
            ("CC26CC26", 1, "CC26", "CC26", 4, 200335),
            ("CC26IN26", 1, "CC26", "IN26", 4, 200335),
            ("CE26CA26", 1, "CE26", "CA26", 5, 200329),
            ("CE26CMO26", 1, "CE26", "CMO26", 5, 200331),
            ("CM26AM26", 1, "CM26", "AM26", 3, 200329),
            ("CM26AS26", 1, "CM26", "AS26", 3, 200329),
            ("CM26BI26", 1, "CM26", "BI26", 3, 200331),
            ("CM26DR26", 1, "CM26", "DR26", 3, 200329),
            ("CM26MSV26", 1, "CM26", "MSV26", 3, 200335),
            ("CM26RN26", 1, "CM26", "RN26", 3, 200331),
            ("CM26SM26", 1, "CM26", "SM26", 3, 200329),
            ("FN26CFN26", 1, "FN26", "CFN26", 3, 200329),
            ("FN26PFNG26", 1, "FN26", "PFNG26", 3, 200331),
            ("FN26SAM26", 1, "FN26", "SAM26", 3, 200329),
            ("FN26SF26", 1, "FN26", "SF26", 3, 200335),
            ("FN26SFN26", 1, "FN26", "SFN26", 3, 200335),
            ("FT26CF26", 1, "FT26", "CF26", 6, 200331),
            ("FT26CMK26", 1, "FT26", "CMK26", 6, 200335),
            ("FT26EI26", 1, "FT26", "EI26", 6, 200331),
            ("FT26FA26", 1, "FT26", "FA26", 6, 200335),
            ("FT26FMA26", 1, "FT26", "FMA26", 6, 200335),
            ("FT26FNF26", 1, "FT26", "FNF26", 6, 200335),
            ("FT26PFN26", 1, "FT26", "PFN26", 6, 200335),
            ("FT26TF26", 1, "FT26", "TF26", 6, 200331),
            ("FT26TM26", 1, "FT26", "TM26", 6, 200335),
            ("FT26TX26", 1, "FT26", "TX26", 6, 200329),
            ("GA26GA26", 1, "GA26", "GA26", 4, 200331),
            ("GA26ITMGA26", 1, "GA26", "ITMGA26", 4, 200331),
            ("GA26RMGA26", 1, "GA26", "RMGA26", 4, 200329),
            ("GRC26CSGRC26", 1, "GRC26", "CSGRC26", 2, 200329),
            ("GRC26ESGGRC26", 1, "GRC26", "ESGGRC26", 2, 200335),
            ("GRC26LKGRC26", 1, "GRC26", "LKGRC26", 2, 200335),
            ("GRC26RMGRC26", 1, "GRC26", "RMGRC26", 2, 200331),
            ("GRC26SFGRC26", 1, "GRC26", "SFGRC26", 2, 200331),
            ("GRC26SOP26", 1, "GRC26", "SOP26", 2, 200335),
            ("HC26AIHC26", 1, "HC26", "AIHC26", 1, 200329),
            ("HC26HCM26", 1, "HC26", "HCM26", 1, 200335),
            ("IT26AIIT26", 1, "IT26", "AIIT26", 3, 200331),
            ("IT26DA26", 1, "IT26", "DA26", 3, 200331),
            ("IT26ITMITT26", 1, "IT26", "ITMITT26", 3, 200329),
            ("IT26ITP26", 1, "IT26", "ITP26", 3, 200329),
            ("PD26AIPD26", 1, "PD26", "AIPD26", 5, 200329),
            ("PD26AN26", 1, "PD26", "AN26", 5, 200331),
            ("PD26APG26", 1, "PD26", "APG26", 5, 200335),
            ("PD26BOT26", 1, "PD26", "BOT26", 5, 200335),
            ("PD26BPI26", 1, "PD26", "BPI26", 5, 200331),
            ("PD26CMPD26", 1, "PD26", "CMPD26", 5, 200335),
            ("PD26CRT26", 1, "PD26", "CRT26", 5, 200331),
            ("PD26CSPD26", 1, "PD26", "CSPD26", 5, 200331),
            ("PD26CT26", 1, "PD26", "CT26", 5, 200329),
            ("PD26DM26", 1, "PD26", "DM26", 5, 200335),
            ("PD26DP26", 1, "PD26", "DP26", 5, 200331),
            ("PD26DRPD26", 1, "PD26", "DRPD26", 5, 200331),
            ("PD26DT26", 1, "PD26", "DT26", 5, 200335),
            ("PD26ENT26", 1, "PD26", "ENT26", 5, 200335),
            ("PD26LO26", 1, "PD26", "LO26", 5, 200335),
            ("PD26ME26", 1, "PD26", "ME26", 5, 200331),
            ("PD26PFPD26", 1, "PD26", "PFPD26", 5, 200331),
            ("PD26PGO26", 1, "PD26", "PGO26", 5, 200329),
            ("PD26PI26", 1, "PD26", "PI26", 5, 200329),
            ("PD26PO26", 1, "PD26", "PO26", 5, 200329),
            ("PD26PS26", 1, "PD26", "PS26", 5, 200331),
            ("PD26RNPD26", 1, "PD26", "RNPD26", 5, 200329),
            ("PD26TC26", 1, "PD26", "TC26", 5, 200331),
            ("PD26TMPD26", 1, "PD26", "TMPD26", 5, 200331),
            ("PD26WS26", 1, "PD26", "WS26", 5, 200331),
            ("PM26MSPM26", 1, "PM26", "MSPM26", 2, 200329),
            ("PM26PAG26", 1, "PM26", "PAG26", 2, 200335),
            ("PRD26PMPRD26", 1, "PRD26", "PMPRD26", 4, 200331),
            ("PRD26SMPRD26", 1, "PRD26", "SMPRD26", 4, 200335),
            ("SU26ESGSU26", 1, "SU26", "ESGSU26", 6, 200329),
            ("SU26ITMSU26", 1, "SU26", "ITMSU26", 6, 200329),
            ("SU26PMSU26", 1, "SU26", "PMSU26", 6, 200335),
            ("SU26RMSU26", 1, "SU26", "RMSU26", 6, 200335),
            ("SU26SFSU26", 1, "SU26", "SFSU26", 6, 200335),
        ]

        tm_objects = []
        for t_id, p_id, cc_id, c_id, g_name, c_by in tna_master_data:
            tm_objects.append(TnaMaster(
                tna_id=t_id,
                tna_period_id=p_id,
                course_category_id=cc_id,
                course_id=c_id,
                group_name=g_name,
                created_by_id=c_by,
            ))
        TnaMaster.objects.bulk_create(tm_objects)
        self.stdout.write(self.style.SUCCESS(f'  [OK] Seeded {len(tm_objects)} TNA Master records'))

        tna_participant_data = [
            (157, "PM26PAG26", 200001), (158, "PD26LO26", 200022), (159, "PD26LO26", 200033),
            (160, "PM26PAG26", 200053), (161, "PD26LO26", 200068), (162, "PD26LO26", 200094),
            (163, "PM26PAG26", 200106), (164, "PM26PAG26", 200118), (165, "PM26PAG26", 200135),
            (166, "PM26PAG26", 200157), (167, "PD26LO26", 200167), (168, "PD26LO26", 200178),
            (169, "PM26PAG26", 200193), (170, "PM26PAG26", 200203), (171, "PD26LO26", 200214),
            (172, "PD26LO26", 200234), (173, "PM26PAG26", 200253), (174, "PM26PAG26", 200261),
            (175, "PD26LO26", 200282), (176, "PD26LO26", 200294), (177, "PM26PAG26", 200307),
            (178, "PM26PAG26", 200317), (179, "PM26PAG26", 200344), (180, "PD26LO26", 200367),
            (181, "PD26LO26", 200385), (182, "PM26PAG26", 200411), (183, "PM26PAG26", 200002),
            (184, "PD26LO26", 200003), (185, "PM26PAG26", 200023), (186, "PM26PAG26", 200024),
            (187, "PM26PAG26", 200034), (188, "PM26PAG26", 200035), (189, "PM26PAG26", 200054),
            (190, "PM26PAG26", 200055), (191, "PM26PAG26", 200069), (192, "PM26PAG26", 200070),
            (193, "PM26PAG26", 200095), (194, "PD26LO26", 200096), (195, "PD26LO26", 200107),
            (196, "PM26PAG26", 200108), (197, "PD26LO26", 200119), (198, "PM26PAG26", 200120),
            (199, "PM26PAG26", 200136), (200, "PD26LO26", 200137), (201, "PD26LO26", 200158),
            (202, "PD26LO26", 200159), (203, "PM26PAG26", 200168), (204, "PD26LO26", 200169),
            (205, "PM26PAG26", 200179), (206, "PD26LO26", 200180), (207, "PD26LO26", 200194),
            (208, "PD26LO26", 200195), (209, "PM26PAG26", 200204), (210, "PM26PAG26", 200205),
            (211, "PD26LO26", 200215), (212, "PM26PAG26", 200216), (213, "PD26LO26", 200235),
            (214, "PM26PAG26", 200236), (215, "PM26PAG26", 200254), (216, "PM26PAG26", 200255),
            (217, "PD26LO26", 200262), (218, "PD26LO26", 200263), (219, "PD26LO26", 200283),
            (220, "PD26LO26", 200284), (221, "PM26PAG26", 200295), (222, "PD26LO26", 200296),
            (223, "PD26LO26", 200308), (224, "PD26LO26", 200309), (225, "PM26PAG26", 200318),
            (226, "PM26PAG26", 200319), (227, "PD26LO26", 200345), (228, "PM26PAG26", 200346),
            (229, "PD26LO26", 200368), (230, "PM26PAG26", 200369), (231, "PM26PAG26", 200386),
            (232, "PM26PAG26", 200387), (233, "PD26LO26", 200412), (234, "PM26PAG26", 200413),
    
            *[(i, "BD26BD26", nik) for i, nik in enumerate(range(200001, 200426), 235)],
 
            (660, "IT26DA26", 200001), (661, "FN26CFN26", 200002), (662, "FN26CFN26", 200003),
            (663, "FN26CFN26", 200004), (664, "FN26CFN26", 200005), (665, "FN26CFN26", 200006),
            (666, "FN26CFN26", 200007), (667, "FN26CFN26", 200008), (668, "GRC26RMGRC26", 200009),
            (669, "FN26CFN26", 200010), (670, "PD26AN26", 200011), (671, "IT26DA26", 200012),

        ]
        

        extra_participants = [
            (672, "IT26DA26", 200013), (673, "PD26AN26", 200014), (674, "FN26CFN26", 200015),
            (675, "PD26AN26", 200016), (676, "IT26DA26", 200017), (677, "PD26AN26", 200018),
            (678, "GRC26RMGRC26", 200019), (679, "PD26AN26", 200020), (680, "PD26AN26", 200021),
            (681, "IT26DA26", 200022), (682, "PD26AN26", 200023), (683, "PD26AN26", 200024),
            (684, "IT26DA26", 200025), (685, "PD26AN26", 200026), (686, "PD26AN26", 200027),
            (687, "FN26CFN26", 200028), (688, "FN26CFN26", 200029), (689, "GRC26RMGRC26", 200030),
            (690, "FN26CFN26", 200031), (691, "IT26DA26", 200032), (692, "PD26AN26", 200033),
            (693, "PD26AN26", 200034), (694, "IT26DA26", 200035), (695, "FN26CFN26", 200036),
            (696, "FN26CFN26", 200037), (697, "PD26AN26", 200038), (698, "GRC26RMGRC26", 200039),
            (699, "GRC26RMGRC26", 200040), (700, "PD26AN26", 200041), (701, "PD26AN26", 200042),
            (702, "IT26DA26", 200043), (703, "IT26DA26", 200044), (704, "GRC26RMGRC26", 200045),
            (705, "IT26DA26", 200046), (706, "FN26CFN26", 200047), (707, "FN26CFN26", 200048),
            (708, "IT26DA26", 200049), (709, "PD26AN26", 200050), (710, "GRC26RMGRC26", 200051),
            (711, "FN26CFN26", 200052), (712, "FN26CFN26", 200053), (713, "FN26CFN26", 200054),
            (714, "GRC26RMGRC26", 200055), (715, "IT26DA26", 200056), (716, "FN26CFN26", 200057),
            (717, "FN26CFN26", 200058), (718, "PD26AN26", 200059), (719, "PD26AN26", 200060),
            (720, "IT26DA26", 200061), (721, "FN26CFN26", 200062), (722, "PD26AN26", 200063),
            (723, "FN26CFN26", 200064), (724, "FN26CFN26", 200065), (725, "FN26CFN26", 200066),
            (726, "FN26CFN26", 200067), (727, "PD26AN26", 200068), (728, "IT26DA26", 200069),
            (729, "IT26DA26", 200070), (730, "PD26AN26", 200071), (731, "PD26AN26", 200072),
            (732, "FN26CFN26", 200073), (733, "PD26AN26", 200074), (734, "IT26DA26", 200075),
            (735, "IT26DA26", 200076), (736, "GRC26RMGRC26", 200077), (737, "PD26AN26", 200078),
            (738, "FN26CFN26", 200079), (739, "FN26CFN26", 200080), (740, "FN26CFN26", 200081),
            (741, "GRC26RMGRC26", 200082), (742, "FN26CFN26", 200083), (743, "FN26CFN26", 200084),
            (744, "FN26CFN26", 200085), (745, "IT26DA26", 200086), (746, "GRC26RMGRC26", 200087),
            (747, "FN26CFN26", 200088), (748, "GRC26RMGRC26", 200089), (749, "PD26AN26", 200090),
            (750, "IT26DA26", 200091), (751, "GRC26RMGRC26", 200092), (752, "PD26AN26", 200093),
            (753, "GRC26RMGRC26", 200094), (754, "FN26CFN26", 200095), (755, "FN26CFN26", 200096),
            (756, "PD26AN26", 200097), (757, "FN26CFN26", 200098), (758, "PD26AN26", 200099),
            (759, "PD26AN26", 200100), (760, "FN26CFN26", 200101), (761, "FN26CFN26", 200102),
            (762, "IT26DA26", 200103), (763, "FN26CFN26", 200104), (764, "PD26AN26", 200105),
            (765, "FN26CFN26", 200106), (766, "PD26AN26", 200107), (767, "PD26AN26", 200108),
            (768, "FN26CFN26", 200109), (769, "FN26CFN26", 200110), (770, "PD26AN26", 200111),
            (771, "PD26AN26", 200112), (772, "FN26CFN26", 200113), (773, "FN26CFN26", 200114),
            (774, "FN26CFN26", 200115), (775, "IT26DA26", 200116), (776, "GRC26RMGRC26", 200117),
            (777, "FN26CFN26", 200118), (778, "GRC26RMGRC26", 200119), (779, "IT26DA26", 200120),
            (780, "PD26AN26", 200121), (781, "IT26DA26", 200122), (782, "IT26DA26", 200123),
            (783, "FN26CFN26", 200124), (784, "FN26CFN26", 200125), (785, "PD26AN26", 200126),
            (786, "IT26DA26", 200127), (787, "FN26CFN26", 200128), (788, "IT26DA26", 200129),
            (789, "FN26CFN26", 200130), (790, "PD26AN26", 200131), (791, "IT26DA26", 200132),
            (792, "FN26CFN26", 200133), (793, "PD26AN26", 200134), (794, "GRC26RMGRC26", 200135),
            (795, "FN26CFN26", 200136), (796, "FN26CFN26", 200137), (797, "PD26AN26", 200138),
            (798, "PD26AN26", 200139), (799, "FN26CFN26", 200140), (800, "GRC26RMGRC26", 200141),
            (801, "FN26CFN26", 200142), (802, "FN26CFN26", 200143), (803, "GRC26RMGRC26", 200144),
            (804, "FN26CFN26", 200145), (805, "GRC26RMGRC26", 200146), (806, "FN26CFN26", 200147),
            (807, "IT26DA26", 200148), (808, "FN26CFN26", 200149), (809, "IT26DA26", 200150),
            (810, "IT26DA26", 200151), (811, "FN26CFN26", 200152), (812, "FN26CFN26", 200153),
            (813, "FN26CFN26", 200154), (814, "FN26CFN26", 200155), (815, "PD26AN26", 200156),
            (816, "IT26DA26", 200157), (817, "PD26AN26", 200158), (818, "IT26DA26", 200159),
            (819, "IT26DA26", 200160), (820, "FN26CFN26", 200161), (821, "FN26CFN26", 200162),
            (822, "IT26DA26", 200163), (823, "FN26CFN26", 200164), (824, "FN26CFN26", 200165),
            (825, "FN26CFN26", 200166), (826, "PD26AN26", 200167), (827, "IT26DA26", 200168),
            (828, "FN26CFN26", 200169), (829, "GRC26RMGRC26", 200170), (830, "GRC26RMGRC26", 200171),
            (831, "PD26AN26", 200172), (832, "IT26DA26", 200173), (833, "FN26CFN26", 200174),
            (834, "FN26CFN26", 200175), (835, "PD26AN26", 200176), (836, "FN26CFN26", 200177),
            (837, "GRC26RMGRC26", 200178), (838, "PD26AN26", 200179), (839, "FN26CFN26", 200180),
            (840, "FN26CFN26", 200181), (841, "GRC26RMGRC26", 200182), (842, "IT26DA26", 200183),
            (843, "IT26DA26", 200184), (844, "FN26CFN26", 200185), (845, "IT26DA26", 200186),
            (846, "FN26CFN26", 200187), (847, "GRC26RMGRC26", 200188), (848, "PD26AN26", 200189),
            (849, "GRC26RMGRC26", 200190), (850, "PD26AN26", 200191), (851, "IT26DA26", 200192),
            (852, "IT26DA26", 200193), (853, "IT26DA26", 200194), (854, "PD26AN26", 200195),
            (855, "IT26DA26", 200196), (856, "IT26DA26", 200197), (857, "IT26DA26", 200198),
            (858, "FN26CFN26", 200199), (859, "IT26DA26", 200200), (860, "PD26AN26", 200201),
            (861, "FN26CFN26", 200202), (862, "FN26CFN26", 200203), (863, "FN26CFN26", 200204),
            (864, "PD26AN26", 200205), (865, "PD26AN26", 200206), (866, "IT26DA26", 200207),
            (867, "FN26CFN26", 200208), (868, "IT26DA26", 200209), (869, "PD26AN26", 200210),
            (870, "FN26CFN26", 200211), (871, "IT26DA26", 200212), (872, "GRC26RMGRC26", 200213),
            (873, "FN26CFN26", 200214), (874, "PD26AN26", 200215), (875, "PD26AN26", 200216),
            (876, "FN26CFN26", 200217), (877, "IT26DA26", 200218), (878, "PD26AN26", 200219),
            (879, "IT26DA26", 200220), (880, "IT26DA26", 200221), (881, "PD26AN26", 200222),
            (882, "FN26CFN26", 200223), (883, "IT26DA26", 200224), (884, "PD26AN26", 200225),
            (885, "IT26DA26", 200226), (886, "PD26AN26", 200227), (887, "PD26AN26", 200228),
            (888, "IT26DA26", 200229), (889, "IT26DA26", 200230), (890, "IT26DA26", 200231),
            (891, "PD26AN26", 200232), (892, "PD26AN26", 200233), (893, "GRC26RMGRC26", 200234),
            (894, "PD26AN26", 200235), (895, "IT26DA26", 200236), (896, "IT26DA26", 200237),
            (897, "PD26AN26", 200238), (898, "PD26AN26", 200239), (899, "FN26CFN26", 200240),
            (900, "PD26AN26", 200241), (901, "IT26DA26", 200242), (902, "IT26DA26", 200243),
            (903, "FN26CFN26", 200244), (904, "PD26AN26", 200245), (905, "PD26AN26", 200246),
            (906, "PD26AN26", 200247), (907, "FN26CFN26", 200248), (908, "IT26DA26", 200249),
            (909, "FN26CFN26", 200250), (910, "FN26CFN26", 200251), (911, "GRC26RMGRC26", 200252),
            (912, "IT26DA26", 200253), (913, "FN26CFN26", 200254), (914, "IT26DA26", 200255),
            (915, "IT26DA26", 200256), (916, "GRC26RMGRC26", 200257), (917, "GRC26RMGRC26", 200258),
            (918, "IT26DA26", 200259), (919, "FN26CFN26", 200260), (920, "FN26CFN26", 200261),
            (921, "FN26CFN26", 200262), (922, "PD26AN26", 200263), (923, "PD26AN26", 200264),
            (924, "FN26CFN26", 200265), (925, "FN26CFN26", 200266), (926, "IT26DA26", 200267),
            (927, "FN26CFN26", 200268), (928, "FN26CFN26", 200269), (929, "IT26DA26", 200270),
            (930, "PD26AN26", 200271), (931, "FN26CFN26", 200272), (932, "FN26CFN26", 200273),
            (933, "FN26CFN26", 200274), (934, "FN26CFN26", 200275), (935, "FN26CFN26", 200276),
            (936, "FN26CFN26", 200277), (937, "IT26DA26", 200278), (938, "PD26AN26", 200279),
            (939, "IT26DA26", 200280), (940, "PD26AN26", 200281), (941, "GRC26RMGRC26", 200282),
            (942, "FN26CFN26", 200283), (943, "FN26CFN26", 200284), (944, "IT26DA26", 200285),
            (945, "PD26AN26", 200286), (946, "PD26AN26", 200287), (947, "IT26DA26", 200288),
            (948, "IT26DA26", 200289), (949, "FN26CFN26", 200290), (950, "FN26CFN26", 200291),
            (951, "FN26CFN26", 200292), (952, "FN26CFN26", 200293), (953, "FN26CFN26", 200294),
            (954, "IT26DA26", 200295), (955, "IT26DA26", 200296), (956, "FN26CFN26", 200297),
            (957, "IT26DA26", 200298), (958, "GRC26RMGRC26", 200299), (959, "FN26CFN26", 200300),
            (960, "PD26AN26", 200301), (961, "PD26AN26", 200302), (962, "IT26DA26", 200303),
            (963, "FN26CFN26", 200304), (964, "PD26AN26", 200305), (965, "IT26DA26", 200306),
            (966, "GRC26RMGRC26", 200307), (967, "IT26DA26", 200308), (968, "FN26CFN26", 200309),
            (969, "FN26CFN26", 200310), (970, "IT26DA26", 200311), (971, "FN26CFN26", 200312),
            (972, "FN26CFN26", 200313), (973, "FN26CFN26", 200314), (974, "FN26CFN26", 200315),
            (975, "FN26CFN26", 200316), (976, "FN26CFN26", 200317), (977, "IT26DA26", 200318),
            (978, "IT26DA26", 200319), (979, "GRC26RMGRC26", 200320), (980, "PD26AN26", 200321),
            (981, "IT26DA26", 200322), (982, "PD26AN26", 200323), (983, "IT26DA26", 200324),
            (984, "PD26AN26", 200325), (985, "FN26CFN26", 200326), (986, "FN26CFN26", 200327),
            (987, "FN26CFN26", 200328), (988, "IT26DA26", 200329), (989, "FN26CFN26", 200330),
            (990, "PD26AN26", 200331), (991, "IT26DA26", 200332), (992, "FN26CFN26", 200333),
            (993, "PD26AN26", 200334), (994, "PD26AN26", 200335), (995, "PD26AN26", 200336),
            (996, "FN26CFN26", 200337), (997, "IT26DA26", 200338), (998, "FN26CFN26", 200339),
            (999, "PD26AN26", 200340), (1000, "IT26DA26", 200341), (1001, "PD26AN26", 200342),
            (1002, "FN26CFN26", 200343), (1003, "IT26DA26", 200344), (1004, "PD26AN26", 200345),
            (1005, "IT26DA26", 200346), (1006, "FN26CFN26", 200347), (1007, "IT26DA26", 200348),
            (1008, "FN26CFN26", 200349), (1009, "GRC26RMGRC26", 200350), (1010, "IT26DA26", 200351),
            (1011, "IT26DA26", 200352), (1012, "FN26CFN26", 200353), (1013, "IT26DA26", 200354),
            (1014, "FN26CFN26", 200355), (1015, "GRC26RMGRC26", 200356), (1016, "FN26CFN26", 200357),
            (1017, "FN26CFN26", 200358), (1018, "GRC26RMGRC26", 200359), (1019, "GRC26RMGRC26", 200360),
            (1020, "IT26DA26", 200361), (1021, "FN26CFN26", 200362), (1022, "FN26CFN26", 200363),
            (1023, "PD26AN26", 200364), (1024, "PD26AN26", 200365), (1025, "PD26AN26", 200366),
            (1026, "FN26CFN26", 200367), (1027, "PD26AN26", 200368), (1028, "FN26CFN26", 200369),
            (1029, "IT26DA26", 200370), (1030, "FN26CFN26", 200371), (1031, "PD26AN26", 200372),
            (1032, "FN26CFN26", 200373), (1033, "FN26CFN26", 200374), (1034, "FN26CFN26", 200375),
            (1035, "IT26DA26", 200376), (1036, "FN26CFN26", 200377), (1037, "FN26CFN26", 200378),
            (1038, "PD26AN26", 200379), (1039, "FN26CFN26", 200380), (1040, "PD26AN26", 200381),
            (1041, "FN26CFN26", 200382), (1042, "IT26DA26", 200383), (1043, "PD26AN26", 200384),
            (1044, "IT26DA26", 200385), (1045, "FN26CFN26", 200386), (1046, "FN26CFN26", 200387),
            (1047, "IT26DA26", 200388), (1048, "GRC26RMGRC26", 200389), (1049, "PD26AN26", 200390),
            (1050, "PD26AN26", 200391), (1051, "PD26AN26", 200392), (1052, "FN26CFN26", 200393),
            (1053, "PD26AN26", 200394), (1054, "PD26AN26", 200395), (1055, "FN26CFN26", 200396),
            (1056, "GRC26RMGRC26", 200397), (1057, "FN26CFN26", 200398), (1058, "IT26DA26", 200399),
            (1059, "FN26CFN26", 200400), (1060, "IT26DA26", 200401), (1061, "IT26DA26", 200402),
            (1062, "FN26CFN26", 200403), (1063, "IT26DA26", 200404), (1064, "PD26AN26", 200405),
            (1065, "FN26CFN26", 200406), (1066, "FN26CFN26", 200407), (1067, "PD26AN26", 200408),
            (1068, "PD26AN26", 200409), (1069, "IT26DA26", 200410), (1070, "PD26AN26", 200411),
            (1071, "FN26CFN26", 200412), (1072, "PD26AN26", 200413), (1073, "PD26AN26", 200414),
            (1074, "IT26DA26", 200415), (1075, "PD26AN26", 200416), (1076, "GRC26RMGRC26", 200417),
            (1077, "FN26CFN26", 200418), (1078, "FN26CFN26", 200419), (1079, "FN26CFN26", 200420),
            (1080, "PD26AN26", 200421), (1081, "FN26CFN26", 200422), (1082, "FN26CFN26", 200423),
            (1083, "PD26AN26", 200424), (1084, "IT26DA26", 200425), (1085, "SU26ESGSU26", 200002),
            (1086, "IT26ITP26", 200006), (1087, "SU26ESGSU26", 200009), (1088, "SU26ESGSU26", 200019),
            (1089, "IT26ITP26", 200021), (1090, "IT26ITP26", 200023), (1091, "IT26ITP26", 200024),
            (1092, "SU26ESGSU26", 200026), (1093, "IT26ITP26", 200027), (1094, "IT26ITP26", 200030),
            (1095, "IT26ITP26", 200031), (1096, "IT26ITP26", 200033), (1097, "SU26ESGSU26", 200034),
            (1098, "BD26NG26", 200037), (1099, "SU26ESGSU26", 200038), (1100, "BD26NG26", 200043),
            (1101, "BD26NG26", 200044), (1102, "IT26ITP26", 200045), (1103, "IT26ITP26", 200046),
            (1104, "IT26ITP26", 200048), (1105, "SU26ESGSU26", 200051), (1106, "SU26ESGSU26", 200057),
            (1107, "SU26ESGSU26", 200058), (1108, "IT26ITP26", 200059), (1109, "BD26NG26", 200060),
            (1110, "SU26ESGSU26", 200061), (1111, "IT26ITP26", 200064), (1112, "IT26ITP26", 200065),
            (1113, "BD26NG26", 200066), (1114, "SU26ESGSU26", 200069), (1115, "SU26ESGSU26", 200071),
            (1116, "SU26ESGSU26", 200074), (1117, "BD26NG26", 200076), (1118, "SU26ESGSU26", 200077),
            (1119, "BD26NG26", 200078), (1120, "BD26NG26", 200081), (1121, "BD26NG26", 200085),
            (1122, "SU26ESGSU26", 200086), (1123, "IT26ITP26", 200088), (1124, "BD26NG26", 200089),
            (1125, "IT26ITP26", 200092), (1126, "BD26NG26", 200093), (1127, "BD26NG26", 200097),
            (1128, "BD26NG26", 200100), (1129, "SU26ESGSU26", 200102), (1130, "IT26ITP26", 200103),
            (1131, "IT26ITP26", 200107), (1132, "IT26ITP26", 200108), (1133, "SU26ESGSU26", 200111),
            (1134, "IT26ITP26", 200112), (1135, "IT26ITP26", 200114), (1136, "IT26ITP26", 200115),
            (1137, "SU26ESGSU26", 200116), (1138, "BD26NG26", 200122), (1139, "BD26NG26", 200123),
            (1140, "SU26ESGSU26", 200124), (1141, "SU26ESGSU26", 200128), (1142, "SU26ESGSU26", 200133),
            (1143, "BD26NG26", 200134), (1144, "BD26NG26", 200136), (1145, "IT26ITP26", 200138),
            (1146, "SU26ESGSU26", 200139), (1147, "BD26NG26", 200141), (1148, "IT26ITP26", 200142),
            (1149, "IT26ITP26", 200144), (1150, "SU26ESGSU26", 200146), (1151, "SU26ESGSU26", 200149),
            (1152, "IT26ITP26", 200151), (1153, "IT26ITP26", 200155), (1154, "BD26NG26", 200156),
            (1155, "BD26NG26", 200158), (1156, "BD26NG26", 200159),
        ]

        tp_objects = []
        for tp_id, t_id, nik in tna_participant_data:
            tp_objects.append(TnaParticipant(
                tna_participant_id=tp_id,
                tna_id=t_id,
                nik_id=nik
            ))
            

        TnaParticipant.objects.bulk_create(tp_objects)
        self.stdout.write(self.style.SUCCESS(f'  [OK] Seeded {len(tp_objects)} TNA Participant records'))


        self.stdout.write('\nSeeding Training Master...')
        training_master_data = [
            {
                'training_code': 'TM-ESG-001',
                'course_id': 'ESGSU26',
                'course_category_id': 'SU26',
                'training_type': 'Inhouse Training',
                'training_category': 'ESG',
                'training_title': 'Introduction to ESG Fundamentals',
                'training_description': 'Core concepts of ESG for corporate management.',
                'pic_id': 200335, # Admin Hanum
                'vendor_id': 'PWC',
                'estimated_cost': 5000000.00
            },
            {
                'training_code': 'TM-TECH-002',
                'course_id': 'ITP26',
                'course_category_id': 'IT26',
                'training_type': 'Public Training',
                'training_category': 'Hard Skill',
                'training_title': 'Advanced Python for Data Engineering',
                'training_description': 'Deep dive into data processing with Python.',
                'pic_id': 200331,
                'vendor_id': 'BMS',
                'estimated_cost': 12000000.00
            }
        ]

        for tm in training_master_data:
            obj, created = TrainingMaster.objects.get_or_create(
                training_code=tm['training_code'],
                defaults=tm
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  [OK] Created TrainingMaster: {tm['training_code']}"))

 
        self.stdout.write('\nSeeding Training Events...')
        events_data = [
            {
                'training_code': 'TM-ESG-001',
                'topic': 'ESG in Finance 2026',
                'start_date': '2026-06-01',
                'end_date': '2026-06-03'
            },
            {
                'training_code': 'TM-TECH-002',
                'topic': 'Data Engineering Bootcamp',
                'start_date': '2026-07-15',
                'end_date': '2026-07-20'
            }
        ]

        for ev in events_data:
            tm_obj = TrainingMaster.objects.get(training_code=ev['training_code'])
            
            event, created = TrainingEvent.objects.get_or_create(
                training=tm_obj,
                training_topic=ev['topic'],
                defaults={
                    'start_date': ev['start_date'],
                    'end_date': ev['end_date'],
                    'status': 'Draft'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  [OK] Created TrainingEvent: {ev['topic']}"))

             
                EventLocation.objects.create(
                    event=event,
                    city="Jakarta",
                    venue="SMI Learning Center",
                    room="Learning Room 01",
                    address="Jl. Jenderal Sudirman Kav. 8, Jakarta Pusat"
                )

          
                EventSchedule.objects.create(
                    event=event,
                    training_date=ev['start_date'],
                    start_time='09:00:00',
                    end_time='17:00:00',
                    instructor_name='Ananda Dewi'
                )

                # Add some test participants
                for i, nik in enumerate([200335, 200331, 200329], 1):
                    EventParticipant.objects.create(
                        event=event,
                        nik_id=nik,
                        attendance_status="Present" if i % 2 == 0 else "Absent",
                        l1_score=85.50 + i,
                        l2_score=90.00 - i
                    )

                # Add some test costs
                EventCost.objects.create(
                    event=event,
                    cost_center="CC-TDP-2026",
                    currency="IDR",
                    room_cost=2500000.00,
                    training_cost=15000000.00,
                    sppd_cost=5000000.00,
                    cost_type="Estimate Cost",
                    status_cost="Proposed"
                )

                # Add some test documents
                for i, (nik, d_type) in enumerate([
                    (200335, "Invoice"),
                    (200331, "Form IHT"),
                    (200329, "Other")
                ]):
                    EventDocument.objects.create(
                        event=event,
                        document_type=d_type,
                        file_name=f"document_{i+1}.pdf",
                        file_url=f"https://storage.example.com/training/doc_{i+1}.pdf",
                        uploaded_by_id=nik
                    )

        self.stdout.write(self.style.SUCCESS('\n[DONE] Seeding completed successfully!'))
