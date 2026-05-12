import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cursor.fetchall()
    print("Tables in DB:")
    for t in tables:
        print(f" - {t[0]}")

    for target in ['evaluation_answers', 'evaluation_results']:
        cursor.execute(f"SELECT COUNT(*) FROM {target}")
        count = cursor.fetchone()[0]
        print(f"Table {target} count: {count}")
