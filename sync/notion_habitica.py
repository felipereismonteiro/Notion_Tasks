import requests
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from notion_utils import get_tasks, create_one_month_daily_tasks_based_on_today
import dotenv
dotenv.load_dotenv()
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

def fetch_and_print_tasks(database_id, notion_token, filters=None):
    notion_tasks = get_tasks(database_id, notion_token, filters=filters)
    print("Tarefas do notion: ")
    for task in notion_tasks:
        nome = task.get('nome') or task.get('name') or 'N/A'
        deadline = task.get('deadline') or 'N/A'
    return notion_tasks

def sync_tasks(notion_tasks):
    print(f"Sincronizando tarefas do notion com o habitica...")
    synked_daily_tasks = []

    for task in notion_tasks:
        task_name = task['nome']
        task_desc = task['Descricao']
        task_deadline = task['deadline']
        deadline_date = datetime.fromisoformat(task_deadline).date()

        if "Diária" not in task_name:
            if task_name in synked_daily_tasks:
                print(f"  - Tarefa '{task_name}' já sincronizada. Pulando...")
                continue
            print(f"  - Adicionando tarefa '{task_name}' ao Habitica...")
            habitica_task_payload = {
                "type": "todo",
                "text": task_name,
                "notes": task_desc,
                "date": deadline_date.isoformat(),
                "difficulty": "hard"
            }
            habitica_headers = {
                "x-api-user": USER_ID,
                "x-api-key": API_KEY,
                "x-client": f"{USER_ID}-notion-sync",
                "Content-Type": "application/json"
            }

            while True:
                response = requests.post("https://habitica.com/api/v3/tasks/user", json=habitica_task_payload,
                                         headers=habitica_headers)
                if response.status_code == 201:
                    break
                print(f"    ❌ Erro ao adicionar tarefa '{task_name}' ao Habitica: {response.status_code} {response.text}. Tentando novamente em 5s...")
                time.sleep(5)
            if response.status_code == 201:
                print(f"    ✅ Tarefa '{task_name}' adicionada com sucesso ao Habitica.")
                synked_daily_tasks.append(task_name)
            else:
                print(
                    f"    ❌ Erro ao adicionar tarefa '{task_name}' ao Habitica: {response.status_code} {response.text}")
            continue

        if "Diária" in task_name:
            print(f"  - Tarefa '{task_name}' é uma diária. Adicionando tarefa diária ao Habitica...")
            habitica_task_payload = {
                "type": "daily",
                "text": task_name,
                "notes": task_desc,
                "date": deadline_date.isoformat()
            }
            habitica_headers = {
                "x-api-user": USER_ID,
                "x-api-key": API_KEY,
                "x-client": f"{USER_ID}-notion-sync",
                "Content-Type": "application/json"
            }
            response = requests.post("https://habitica.com/api/v3/tasks/user", json=habitica_task_payload,
                                     headers=habitica_headers)
            if response.status_code == 201:
                print(f"    ✅ Tarefa diária '{task_name}' adicionada com sucesso ao Habitica.")
            else:
                print(
                    f"    ❌ Erro ao adicionar tarefa diária '{task_name}' ao Habitica: {response.status_code} {response.text}")
            continue

# notion_tasks = fetch_and_print_tasks(DATABASE_ID, NOTION_TOKEN, filters={
#     "and": [
#         {
#             "property": "✅ Status",
#             "checkbox": {"equals": False}
#         }
# ]})
# print(f"Sincronizando {len(notion_tasks)} tarefas...")
# sync_tasks(notion_tasks)

create_one_month_daily_tasks_based_on_today(NOTION_TOKEN,
                                            "Diária Praticar poses e fotografar rapidamente.",
                                            "",
                                            "29f2d519d27e8020b1dcdd9a1d022f46",
                                            DATABASE_ID)
create_one_month_daily_tasks_based_on_today(NOTION_TOKEN,
                                            "Cuidar da aparência (pele, cabelo, maquiagem).",
                                            "",
                                            "29f2d519d27e8020b1dcdd9a1d022f46",
                                            DATABASE_ID)
create_one_month_daily_tasks_based_on_today(NOTION_TOKEN,
                                            "Pesquisar inspirações rápidas de looks e cosplays.",
                                            "",
                                            "29f2d519d27e8020b1dcdd9a1d022f46",
                                            DATABASE_ID)
create_one_month_daily_tasks_based_on_today(NOTION_TOKEN,
                                            "Registrar pequenos bastidores nos stories.",
                                            "",
                                            "29f2d519d27e8020b1dcdd9a1d022f46",
                                            DATABASE_ID)
create_one_month_daily_tasks_based_on_today(NOTION_TOKEN,
                                            "Praticar edição de imagens com seu preset.",
                                            "",
                                            "29f2d519d27e8020b1dcdd9a1d022f46",
                                            DATABASE_ID)
create_one_month_daily_tasks_based_on_today(NOTION_TOKEN,
                                            "Manter atividade física e postura.",
                                            "",
                                            "29f2d519d27e8020b1dcdd9a1d022f46",
                                            DATABASE_ID)
create_one_month_daily_tasks_based_on_today(NOTION_TOKEN,
                                            "Refletir sobre autenticidade e motivação.",
                                            "",
                                            "29f2d519d27e8020b1dcdd9a1d022f46",
                                            DATABASE_ID)