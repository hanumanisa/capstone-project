import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

print(f"OPENAI_API_KEY exists: {bool(settings.OPENAI_API_KEY)}")
print(f"OPENROUTER_API_KEY exists: {bool(settings.OPENROUTER_API_KEY)}")
if settings.OPENROUTER_API_KEY:
    print(f"OPENROUTER_API_KEY starts with: {settings.OPENROUTER_API_KEY[:10]}...")
