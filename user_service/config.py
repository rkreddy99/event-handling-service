import os

# Read token from ~/.token file
TOKEN_PATH = os.path.expanduser("~/.user_service.token")
with open(TOKEN_PATH, "r") as f:
    API_TOKEN = f.read().strip()


