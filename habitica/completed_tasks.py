import os
import sys
import dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import json
from datetime import datetime, timedelta
today = datetime.now().date()
dotenv.load_dotenv()

API_KEY = os.getenv('API_KEY')
USER_ID = os.getenv('USER_ID')

required = {
    "API_KEY": API_KEY,
    "USER_ID": USER_ID
}

missing = [name for name, value in required.items() if not value]
if missing:
    print("⚠️ Variáveis ausentes:", ", ".join(missing))
else:
    print("✅ Todas as variáveis de ambiente foram carregadas corretamente.")

def get_completed_habits():
    headers = {
        "x-api-user": USER_ID,
        "x-api-key": API_KEY,
        "x-client": f"{USER_ID}-meuscripts"
    }

    response = requests.get("https://habitica.com/api/v3/tasks/user?type=dailys", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao buscar hábitos: {response.text}")
        return None