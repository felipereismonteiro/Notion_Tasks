from notion_utils import get_tasks, complete_task
from habitica.completed_tasks import get_completed_habits
import os
from datetime import date, datetime

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

API_KEY = os.getenv('API_KEY')
USER_ID = os.getenv('USER_ID')

required = {
    "API_KEY": API_KEY,
    "USER_ID": USER_ID,
    "NOTION_TOKEN": NOTION_TOKEN,
    "DATABASE_ID": DATABASE_ID
}

missing = [name for name, value in required.items() if not value]
if missing:
    print("⚠️ Variáveis ausentes:", ", ".join(missing))
else:
    print("✅ Todas as variáveis de ambiente foram carregadas corretamente.")

tasks = get_tasks(DATABASE_ID, NOTION_TOKEN)
print("----------------------------------------")
print("Tarefas pendentes no Notion para hoje:")
for task in tasks:
    print(f"- {task['nome']} (ID: {task['id']})")
completed_tasks = get_completed_habits().get("data")
print("----------------------------------------")

print("Sincronizando tarefas completadas do Habitica com o Notion...")

for task in completed_tasks:
    if len(task.get("history")) < 1:
        continue

    if task["text"] == "Limpo":
        for notion_task in tasks:
            if 'pornografia' in notion_task.get('nome', '').lower():
                complete_task(notion_task['id'], NOTION_TOKEN)
                print(f"Tarefa '{notion_task['nome']}' marcada como completa no Notion ✅")

    if (datetime.utcfromtimestamp(task["history"][-1]["date"]/1000).date() == date.today()
            and task["completed"] == True):
        for notion_task in tasks:
            if notion_task['nome'] == task.get('text'):
                complete_task(notion_task['id'], NOTION_TOKEN)
                print(f"Tarefa '{notion_task['nome']}' marcada como completa no Notion ✅")

print("Sincronização concluída.")