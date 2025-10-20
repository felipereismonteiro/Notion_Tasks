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

    url_dailys = "https://habitica.com/api/v3/tasks/user?type=dailys"
    url_todos = "https://habitica.com/api/v3/tasks/user?type=completedTodos"

    response_dailys = requests.get(url_dailys, headers=headers)
    response_todos = requests.get(url_todos, headers=headers)

    if response_dailys.status_code == 200 and response_todos.status_code == 200:
        dailys = response_dailys.json().get("data", [])
        todos = response_todos.json().get("data", [])
        return dailys + todos
    else:
        print(f"Erro ao buscar tarefas:")
        print(f"  Dailys: {response_dailys.status_code} -> {response_dailys.text}")
        print(f"  Todos: {response_todos.status_code} -> {response_todos.text}")
        return []

