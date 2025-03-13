import os

# Read token from ~/.token file
TOKEN_PATH = os.path.expanduser("~/.user_service.token")
with open(TOKEN_PATH, "r") as f:
    API_TOKEN = f.read().strip()

# Neon Postgres credentials
PGHOST = os.getenv("PGHOST")
PGDATABASE = os.getenv("PGDATABASE")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")

