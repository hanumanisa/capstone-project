import json
import time
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from api.ai_tools import (
    current_user_id_var,
    get_user_role_and_division,
    get_my_profile,
    get_training_stats,
    search_trainings,
    get_training_schedules,
    get_tna_status,
    get_employee_tna,
    get_unfulfilled_tna_report,
    get_training_hours_report,
    get_training_analytics,
    get_budget_and_costs,
    get_hotel_and_vendor_data,
    search_employees,
    get_employees_by_travel_history,
    get_evaluation_summaries,
    get_master_data
)

def execute_ai_query(user, message: str, history: list = None) -> tuple:
    """
    Menjalankan kueri AI menggunakan LangGraph React Agent dengan alat yang disesuaikan dengan peran (role) pengguna.
    Mengembalikan tuple (ai_response, tokens_used).
    """
    if history is None:
        history = []

    # 1. Tentukan peran (role) dan informasi divisi pengguna
    role, employee, division_id, division_name = get_user_role_and_division(user.id)

    # Set user ID in ContextVar for thread-safety and security
    token = current_user_id_var.set(user.id)

    try:
        # 2. Pilih alat (tools) secara dinamis sesuai RBAC
        if role in ['superadmin', 'admin']:
            tools = [
                get_my_profile, get_training_stats, search_trainings, get_training_schedules,
                get_tna_status, get_employee_tna, get_unfulfilled_tna_report, get_training_hours_report,
                get_training_analytics, get_budget_and_costs, get_hotel_and_vendor_data,
                search_employees, get_employees_by_travel_history, get_evaluation_summaries, get_master_data
            ]
        elif role == 'dean':
            # Dean memiliki semua akses L&D termasuk data budget/anggaran
            tools = [
                get_my_profile, get_training_stats, search_trainings, get_training_schedules,
                get_tna_status, get_employee_tna, get_unfulfilled_tna_report, get_training_hours_report,
                get_training_analytics, get_budget_and_costs, get_hotel_and_vendor_data,
                search_employees, get_employees_by_travel_history, get_evaluation_summaries, get_master_data
            ]
        elif role in ['head_of_division', 'team_leader']:
            # HoD dan TL tidak memiliki akses budget dan data hotel/vendor
            tools = [
                get_my_profile, get_training_stats, search_trainings, get_training_schedules,
                get_tna_status, get_employee_tna, get_unfulfilled_tna_report, get_training_hours_report,
                get_training_analytics,
                search_employees, get_employees_by_travel_history, get_evaluation_summaries, get_master_data
            ]
        else: # employee
            # Employee hanya memiliki akses ke data sendiri dan data umum
            tools = [
                get_my_profile, get_training_stats, search_trainings, get_training_schedules,
                get_tna_status, get_evaluation_summaries, get_master_data
            ]

        # 3. Tentukan model LLM dan fallbacks
        models_to_chain = []

        # Model Utama (OpenAI)
        if getattr(settings, 'OPENAI_API_KEY', None):
            models_to_chain.append(
                ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=settings.OPENAI_API_KEY,
                    temperature=0.3,
                    max_tokens=8192,
                    timeout=30.0,
                    max_retries=0
                )
            )

        # Fallback (OpenRouter / Gemini)
        if getattr(settings, 'OPENROUTER_API_KEY', None):
            fallback_models_list = [
                "openrouter/free",
                "deepseek/deepseek-v4-flash:free",
                "google/gemma-4-31b-it:free",
                "qwen/qwen3-next-80b-a3b-instruct:free",
                "openai/gpt-4o-mini",
                "google/gemini-2.0-flash-001",
                "openrouter/auto"
            ]
            for model_name in fallback_models_list:
                models_to_chain.append(
                    ChatOpenAI(
                        model=model_name,
                        api_key=settings.OPENROUTER_API_KEY,
                        base_url="https://openrouter.ai/api/v1",
                        temperature=0.3,
                        max_tokens=8192,
                        timeout=90.0,
                        max_retries=0
                    )
                )

        if not models_to_chain:
            raise ValueError("No API keys configured for OpenAI or OpenRouter")

        llm = models_to_chain[0]
        if len(models_to_chain) > 1:
            llm = llm.with_fallbacks(models_to_chain[1:])

        # 4. Buat Instruksi Sistem (Prompt) yang sesuai dengan peran
        base_instruction = (
            "PENTING: Anda adalah SMI Assistant, AI Assistant cerdas untuk sistem manajemen pelatihan perusahaan (L&D). "
            "Anda HANYA diperbolehkan menjawab pertanyaan yang berkaitan dengan sistem manajemen pelatihan (L&D) dan data nyata yang ada di database perusahaan. "
            "CATATAN: Pertanyaan tentang data karyawan, daftar karyawan sedivisi, anggaran (budget), biaya (cost), realisasi, atau uang yang sudah digunakan terkait pelatihan ADALAH bagian dari topik yang valid dan WAJIB Anda layani. "
            "Langkah pertama Anda adalah memeriksa apakah ada Alat (Tool) yang dapat membantu menjawab pertanyaan. Anda WAJIB memanggil Alat tersebut terlebih dahulu untuk mendapatkan data nyata dari database sebelum menyimpulkan bahwa data tidak ditemukan atau menolak menjawab. PENTING: Jika pengguna meminta daftar nama karyawan sedivisi, WAJIB memanggil tool 'search_employees' dengan query kosong. "
            "PENGECUALIAN: Jika data yang diminta benar-benar sudah ada di riwayat percakapan Anda dengan pengguna, Anda boleh langsung menjawab. Namun jika konteksnya berbeda (contoh: sebelumnya membahas TNA, sekarang ditanya Jam Training), ANDA WAJIB MEMANGGIL ALAT (Tool) BARU yang relevan. Jangan pernah menebak-nebak jika belum memanggil Alat. "
            "JIKA pengguna menanyakan tentang anggaran/biaya/keuangan pelatihan tetapi peran/role Anda tidak memiliki Alat (Tool) untuk mengakses data tersebut, Anda wajib menganggap data tersebut tidak ditemukan/tidak ada dan menjawab sesuai aturan data kosong/tidak ditemukan di bawah. "
            "DILARANG KERAS menyertakan data mentah JSON, block code (seperti ```json ... ``` atau tanda petik tiga lainnya), atau kode teknis di dalam jawaban Anda. Selalu terjemahkan data teknis tersebut ke dalam kalimat penjelasan Bahasa Indonesia yang ramah dan mudah dibaca. "
            "DILARANG KERAS MENGARANG DATA (HALUSINASI). JANGAN PERNAH membuat data fiktif, menggunakan nama artis, tokoh terkenal, atau data palsu lainnya. Anda HANYA boleh menjawab menggunakan data nyata yang dikembalikan oleh pemanggilan Alat (Tools). "
            "JIKA pengguna meminta daftar data (karyawan, training, dll) yang belum ada di riwayat, ANDA WAJIB MEMANGGIL ALAT TERLEBIH DAHULU SEBELUM MENJAWAB. JANGAN PERNAH menjawab langsung dengan mengarang data. "
            "Setiap alat yang meminta parameter `user_id` atau `requester_user_id` WAJIB diisi dengan 'User ID' dari Konteks Pengguna Login secara diam-diam. JANGAN PERNAH menyebutkan kata 'user_id', menanyakan user_id kepada pengguna, atau menyuruh pengguna mengecek user_id mereka dalam jawaban Anda. Jika data tidak ditemukan, katakan saja data tidak ditemukan tanpa menyinggung masalah teknis user_id. "
            "JANGAN PERNAH meminta persetujuan (konfirmasi) pengguna untuk memanggil Alat. Jika ada parameter opsional (seperti bulan/tahun) yang tidak disebutkan pengguna, LANGSUNG panggil Alat dengan nilai default (seluruh waktu) tanpa bertanya 'Apakah ini sudah sesuai?'. "
            "PENTING: Jika di riwayat percakapan sebelumnya Anda gagal, menolak menjawab, atau terjadi error, JANGAN jadikan itu alasan untuk menolak di pertanyaan baru. JANGAN berbohong mengatakan ada 'masalah teknis'. Selalu coba panggil Alat (Tool) lagi dengan segar untuk pertanyaan terbaru. "
            "ATURAN FORMAT JAWABAN & DAFTAR (SANGAT PENTING): "
            "Setiap kali Anda menyebutkan lebih dari satu data, memberikan langkah-langkah, atau menampilkan daftar/list apa pun (karyawan, training, TNA, jadwal, atau jawaban lainnya), "
            "ANDA WAJIB MENGGUNAKAN NOMOR URUT (1., 2., 3., dst) agar sangat rapi dan enak dibaca. "
            "Contoh: "
            "1. **Poin Pertama** - Penjelasan/Detail "
            "2. **Poin Kedua** - Penjelasan/Detail "
            "DILARANG KERAS menggunakan simbol bullet point seperti bintang (*), strip (-), hashtag (#), atau titik tengah (•) untuk daftar apa pun. "
            "DILARANG KERAS menampilkan daftar tanpa nomor urut. "
            "DILARANG KERAS menampilkan atau menyebutkan NIK (Nomor Induk Karyawan) di dalam daftar jawaban Anda, karena NIK adalah data pribadi rahasia. Cukup tampilkan nama dan posisinya saja. "
            "Anda DIWAJIBKAN menyusun paragraf dengan jarak baris yang rapi (menggunakan enter/line break) serta menggunakan teks tebal (markdown **tebal**) untuk menyorot informasi penting agar jawaban Anda cantik, rapi, dan mudah dibaca oleh manusia. "
            "PANDUAN DATA PANJANG (SANGAT PENTING): Anda wajib memberikan jawaban yang komplit berdasarkan data dari Alat. Namun, jika jumlah data yang harus ditampilkan sangat banyak, Anda WAJIB menampilkan maksimal 100 data per balasan. JANGAN menuliskannya semua sekaligus jika lebih dari 100 agar tidak terpotong. Setelah menampilkan 100 data, Anda WAJIB menutupnya HANYA dengan pesan peringatan berikut: "
            "'_SMI Assistant saat ini tidak bisa langsung memberikan seluruh data sekaligus karena keterbatasan teks. Ketik **Lanjutkan** atau **Continue** untuk melihat kelengkapan data berikutnya._' "
            "Jika pengguna merespons dengan kata 'lanjutkan' atau 'continue', Anda WAJIB meneruskan nomor urutan dan menampilkan maksimal 100 data berikutnya dari titik terakhir Anda berhenti. Ulangi ini terus sampai semua data habis. JANGAN berhenti di angka yang sedikit (misal 30), Anda HARUS memaksimalkan hingga 100 baris data per balasan. "
            "Jika seluruh data telah selesai ditampilkan ke pengguna (baik pada balasan pertama yang kurang dari 100, maupun pada balasan lanjutan yang terakhir), Anda WAJIB menutupnya dengan kalimat yang sopan, misalnya: '_SMI Assistant telah menampilkan seluruh data dengan lengkap. Jika ada hal lain yang ingin ditanyakan, silakan beri tahu saya!_' "
            "Jika pertanyaan sangat jelas dan sama sekali tidak berkaitan dengan topik HR, Karyawan, atau Pelatihan/L&D (contoh: cuaca, sejarah umum, resep masakan, hal random), Anda wajib menjawab: "
            "'Maaf, SMI Assistant hanya dapat menjawab pertanyaan yang berkaitan dengan sistem manajemen pelatihan (L&D). Silakan ajukan pertanyaan seputar pelatihan.'\n"
            "Jika pengguna HANYA MENYAPA (contoh: 'halo') atau mengetik 'lanjutkan'/'continue', Anda DIWAJIBKAN membalas atau meneruskan daftar Anda."
        )

        if role in ['superadmin', 'admin', 'dean']:
            system_instruction = (
                f"{base_instruction}\n"
                "Anda berbicara dengan pengguna berkedudukan Admin/Superadmin/Dean. "
                "Perhatikan aturan hak akses (RBAC) pada masing-masing alat. "
                "Anda hanya boleh menjawab PERSIS: 'Maaf, SMI Assistant saat ini belum memiliki datanya dan hanya dapat menjawab pertanyaan yang berkaitan dengan sistem manajemen pelatihan (L&D). Jika ada pertanyaan lain, Anda bisa menghubungi Admin melalui whatsapp.' JIKA DAN HANYA JIKA Anda sama sekali tidak memiliki Alat (Tool) untuk menjawab pertanyaan tersebut (KECUALI jika pengguna hanya menyapa atau mengetik lanjutkan)."
            )
        elif role in ['head_of_division', 'team_leader']:
            system_instruction = (
                f"{base_instruction}\n"
                f"Anda berbicara dengan pengguna berkedudukan {role}. "
                "Perhatikan aturan hak akses (RBAC) pada masing-masing alat. "
                "Anda hanya boleh menjawab PERSIS: 'Maaf, SMI Assistant saat ini belum memiliki datanya dan hanya dapat menjawab pertanyaan yang berkaitan dengan sistem manajemen pelatihan (L&D). Jika ada pertanyaan lain, Anda bisa menghubungi Admin melalui whatsapp.' JIKA DAN HANYA JIKA Anda sama sekali tidak memiliki Alat (Tool) untuk menjawab pertanyaan tersebut (KECUALI jika pengguna hanya menyapa atau mengetik lanjutkan)."
            )
        else:
            system_instruction = (
                f"{base_instruction}\n"
                f"Anda berbicara dengan pengguna berkedudukan {role}. "
                "Perhatikan aturan hak akses (RBAC) pada masing-masing alat. "
                "Anda hanya boleh menjawab PERSIS: 'Maaf, SMI Assistant saat ini belum memiliki datanya dan hanya dapat menjawab pertanyaan yang berkaitan dengan sistem manajemen pelatihan (L&D). Jika ada pertanyaan lain, Anda bisa menghubungi Admin melalui whatsapp.' JIKA DAN HANYA JIKA Anda sama sekali tidak memiliki Alat (Tool) untuk menjawab pertanyaan tersebut (KECUALI jika pengguna hanya menyapa atau mengetik lanjutkan)."
            )

        # 5. Bangun LangGraph React Agent
        agent = create_react_agent(llm, tools, prompt=system_instruction)

        # 6. Dapatkan waktu lokal real-time
        now_local = timezone.localtime(timezone.now())
        days_id = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        months_id = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni", 
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        current_time_str = f"{days_id[now_local.weekday()]}, {now_local.day} {months_id[now_local.month - 1]} {now_local.year} pukul {now_local.strftime('%H:%M:%S')}"

        # 7. Siapkan pesan input (history + pesan baru)
        messages = []
        for h in history[-5:]:
            role_val = h.get('role') or ('user' if h.get('is_user') else 'assistant')
            text_val = h.get('content') or h.get('text') or ''
            if text_val:
                if role_val == 'user':
                    messages.append(HumanMessage(content=text_val))
                elif role_val in ['assistant', 'ai']:
                    messages.append(AIMessage(content=text_val))

        user_name = employee.full_name if employee else (user.first_name or user.username)
        div_name_str = division_name if division_name else "Tidak Ada Divisi"
        
        user_content = (
            f"Waktu Lokal Saat Ini (Real-time): {current_time_str}\n"
            f"Konteks Pengguna Login: Nama = {user_name}, Role = {role}, Divisi = {div_name_str}, User ID = {user.id}\n\n"
            f"Pertanyaan: {message}"
        )
        messages.append(HumanMessage(content=user_content))

        # 8. Jalankan Agent
        result = agent.invoke({"messages": messages})

        # 9. Dapatkan respon akhir
        final_message = result["messages"][-1]
        ai_response = final_message.content.strip()

        # Hitung penggunaan token
        tokens_used = 0
        for msg in result["messages"]:
            if isinstance(msg, AIMessage) or msg.__class__.__name__ == 'AIMessage':
                if hasattr(msg, 'response_metadata') and msg.response_metadata:
                    usage = msg.response_metadata.get("token_usage") or {}
                    tokens_used += usage.get("total_tokens") or 0

        return ai_response, tokens_used

    finally:
        # Bersihkan ContextVar
        current_user_id_var.reset(token)
