import sqlite3
try:
    conn = sqlite3.connect('c:\\Users\\hanum\\capscoba\\backend\\db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in SQLite:", [t[0] for t in tables])
    
    if ('tna_participants',) in tables:
        cursor.execute("SELECT count(*) FROM tna_participants;")
        print("Count in SQLite:", cursor.fetchone()[0])
        
        # Check top counts
        cursor.execute("SELECT nik, count(*) as c FROM tna_participants GROUP BY nik ORDER BY c DESC LIMIT 10;")
        print("Top counts in SQLite:", cursor.fetchall())
except Exception as e:
    print("Error:", e)
