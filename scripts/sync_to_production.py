""" 
Synchroniseert Printful-data naar de PRODUCTIEDATABASE op Render.
Gebruik: python scripts/sync_to_production.py "<EXTERNAL_DATABASE_URL>"

Haal de External Database URL op uit:
  Render Dashboard -> jouw PostgreSQL database -> Connection -> External Database URL
"""
import sys
import os
import subprocess

if len(sys.argv) < 2:
    print("Gebruik: python scripts/sync_to_production.py \"<EXTERNAL_DATABASE_URL>\"")
    print("\nVoorbeeld:")
    print('  python scripts/sync_to_production.py "postgresql://user:pass@dpg-xxx.oregon-postgres.render.com/dbname"')
    sys.exit(1)

db_url = sys.argv[1]
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

print(f"Verbinden met productiedatabase: {db_url[:70]}...")
print("Starten van sync_printful_data.py...\n")

# Stel DATABASE_URL in als environment variable voor het subprocess
env = os.environ.copy()
env['DATABASE_URL'] = db_url

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
venv_python = os.path.join(project_root, 'venv', 'Scripts', 'python.exe')
if not os.path.exists(venv_python):
    venv_python = sys.executable  # fallback to current python

result = subprocess.run(
    [venv_python, os.path.join(script_dir, 'sync_printful_data.py')],
    env=env,
    cwd=project_root
)

if result.returncode == 0:
    print("\nSync naar productiedatabase voltooid!")
else:
    print(f"\nSync mislukt met exit code {result.returncode}")
    sys.exit(result.returncode)

