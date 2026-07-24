import re

def fix_ai_prompt(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the block and replace it
    pattern = r"\"Jika pertanyaan sangat jelas dan sama sekali tidak berkaitan dengan topik HR.*?\"Jika pengguna HANYA MENYAPA.*?\""
    
    replacement = (
        "\"Jika pengguna HANYA MENYAPA (contoh: 'halo', 'selamat pagi', 'hai') Anda DIWAJIBKAN membalas sapaan tersebut dengan ramah dan menanyakan apa yang bisa dibantu. JANGAN PERNAH memberikan pesan penolakan jika pengguna hanya menyapa. \"\n"
        "            \"SEBALIKNYA, jika pertanyaan sangat jelas dan sama sekali tidak berkaitan dengan topik HR, Karyawan, atau Pelatihan/L&D (contoh: cuaca, sejarah, masakan, hal random), barulah Anda wajib menjawab: \"\n"
        "            \"'Maaf, SMI Assistant hanya dapat menjawab pertanyaan yang berkaitan dengan sistem manajemen pelatihan (L&D). Silakan ajukan pertanyaan seputar pelatihan.'\\n\"\n"
        "            \"Jika pengguna mengetik 'lanjutkan'/'continue', Anda DIWAJIBKAN meneruskan daftar Anda.\""
    )

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

fix_ai_prompt("c:/xampp/htdocs/capstone-project/backend/api/ai_agent.py")
print("Done fixing AI Prompt")
