# pega todos os habitos completos do meu habitify
import requests
import json
from datetime import datetime, timedelta
today = datetime.now().date()

API_KEY = "565e9b1d-21b7-4bd9-8fb7-ab443e6fa413"
USER_ID = "0b55adee-4127-480e-b5a8-55ebea1e9e82"

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

tasks = get_completed_habits().get("data")

for task in tasks:
    history = task.get("history", [])
    task_name = task.get("text")
    task_description = task.get("notes", "")
    print(f"Hábito: {task_name} - {task_description} - {history}")
    for entry in history:
        date_timestamp = entry.get("date")
        date = datetime.fromtimestamp(date_timestamp / 1000).date()
        if date == today:
            print(f"  - Completado em: {date}")



