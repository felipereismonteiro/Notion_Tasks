from notion_utils import get_tasks, complete_task
from habitica.completed_tasks import get_completed_habits
import os
from datetime import date, datetime
from zoneinfo import ZoneInfo

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
print("Tarefas pendentes no Notion para hoje:")
for task in tasks:
    print(f"- {task['nome']} (ID: {task['id']})")
completed_tasks = get_completed_habits()
print(F"COMPLETED TASKS {completed_tasks}")
print(F"QUANTIDADE {len(completed_tasks)}")
print("----------------------------------------")

print("Sincronizando tarefas completadas do Habitica com o Notion...")

for task in completed_tasks:
    if task.get('type') == 'todo' and task.get('completed'):
        task_founded = get_tasks(DATABASE_ID, NOTION_TOKEN,
                filters = {
                "property": "🐈 Sistema",
                "title": {"contains": task.get("text")}
            }
        )
        response = complete_task(sorted(task_founded, key=lambda t: t["deadline"] or "", reverse=True)[0]["id"], NOTION_TOKEN)
        if response:
            print(f"Tarefa '{task.get('text')}' marcada como completa no Notion ✅")
        else :
            print(f"Tarefa '{task.get('text')}' não encontrada no Notion ❌")
            print(f"Resposta do Notion: {response}")

        continue

    if len(task.get("history")) < 1:
        continue

    if task["text"] == "Limpo":
        for notion_task in tasks:
            if 'Dia' in notion_task.get('nome', '').lower() and 'sem' in notion_task.get('nome', '').lower():
                complete_task(notion_task['id'], NOTION_TOKEN)
                print(f"Tarefa '{notion_task['nome']}' marcada como completa no Notion ✅")

    habitica_date = (
        datetime.utcfromtimestamp(task["history"][-1]["date"] / 1000)
        .astimezone(ZoneInfo("America/Sao_Paulo"))
        .date()
    )
    today_brt = datetime.now(ZoneInfo("America/Sao_Paulo")).date()

    if habitica_date == today_brt and task.get("completed") is True:
        for notion_task in tasks:
            if notion_task.get("nome") == task.get("text"):
                complete_task(notion_task["id"], NOTION_TOKEN)
                print(f"Tarefa '{notion_task['nome']}' marcada como completa no Notion ✅")

print("Sincronização concluída.")