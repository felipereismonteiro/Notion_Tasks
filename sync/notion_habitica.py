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

def clean_all_habitica():
    print("Limpando todas as tarefas do Habitica...")
    habitica_headers = {
        "x-api-user": USER_ID,
        "x-api-key": API_KEY,
        "x-client": f"{USER_ID}-notion-sync",
        "Content-Type": "application/json"
    }
    response = requests.get("https://habitica.com/api/v3/tasks/user", headers=habitica_headers)
    if response.status_code != 200:
        print(f"    ❌ Erro ao buscar tarefas do Habitica: {response.status_code} {response.text}")
        return
    tasks = response.json().get("data", [])
    for task in tasks:
        task_id = task["id"]
        del_response = requests.delete(f"https://habitica.com/api/v3/tasks/{task_id}", headers=habitica_headers)
        if del_response.status_code == 200:
            print(f"    ✅ Tarefa '{task['text']}' removida com sucesso do Habitica.")
        else:
            print(f"    ❌ Erro ao remover tarefa '{task['text']}' do Habitica: {del_response.status_code} {del_response.text}")

clean_all_habitica()
notion_tasks = fetch_and_print_tasks(DATABASE_ID, NOTION_TOKEN, filters={
    "and": [
        {
            "property": "✅ Status",
            "checkbox": {"equals": False}
        }
]})
print(f"Sincronizando {len(notion_tasks)} tarefas...")
sync_tasks(notion_tasks)

# create_one_month_daily_tasks_based_on_today(NOTION_TOKEN,
#                                             "Diária Praticar poses e fotografar rapidamente.",
#                                             "Reserve alguns minutos para testar poses diferentes diante do espelho ou da câmera, tirando fotos rápidas para treinar expressões corporais e avaliar ângulos que funcionam melhor para você.",
#                                             "29f2d519d27e8020b1dcdd9a1d022f46",
#                                             DATABASE_ID,
#                                             2, 9)
#
# create_one_month_daily_tasks_based_on_today(NOTION_TOKEN,
#                                             "Diária Cuidar da aparência (pele, cabelo, maquiagem).",
#                                             "Mantenha uma rotina de autocuidado: hidrate a pele, arrume o cabelo e, se desejar, pratique técnicas de maquiagem compatíveis com o estilo alternativo que você busca transmitir.",
#                                             "29f2d519d27e8020b1dcdd9a1d022f46",
#                                             DATABASE_ID,
#                                             2, 9)
#
# create_one_month_daily_tasks_based_on_today(NOTION_TOKEN,
#                                             "Diária Pesquisar inspirações rápidas de looks e cosplays.",
#                                             "Dedique um tempo para pesquisar referências de roupas e cosplays em redes sociais e blogs, salvando imagens que possam servir como inspiração para futuros posts e ensaios.",
#                                             "29f2d519d27e8020b1dcdd9a1d022f46",
#                                             DATABASE_ID,
#                                             2, 9)
#
# create_one_month_daily_tasks_based_on_today(NOTION_TOKEN,
#                                             "Diária Registrar pequenos bastidores nos stories.",
#                                             "Compartilhe momentos do seu dia a dia e bastidores do seu processo criativo nos stories, mostrando autenticidade e fortalecendo a conexão com quem acompanha seu perfil.",
#                                             "29f2d519d27e8020b1dcdd9a1d022f46",
#                                             DATABASE_ID,
#                                             2, 9)
#
# create_one_month_daily_tasks_based_on_today(NOTION_TOKEN,
#                                             "Diária Praticar edição de imagens com seu preset.",
#                                             "Aplique seus presets ou ajustes de edição em fotos recentes para treinar e garantir consistência na estética do feed, ajustando cor, contraste e outros parâmetros.",
#                                             "29f2d519d27e8020b1dcdd9a1d022f46",
#                                             DATABASE_ID,
#                                             2, 9)
#
# create_one_month_daily_tasks_based_on_today(NOTION_TOKEN,
#                                             "Diária Manter atividade física e postura.",
#                                             "Inclua exercícios e alongamentos simples na rotina para melhorar sua postura e condicionamento, aspectos que contribuem para uma presença mais confiante nas fotos.",
#                                             "29f2d519d27e8020b1dcdd9a1d022f46",
#                                             DATABASE_ID,
#                                             2, 9)
#
# create_one_month_daily_tasks_based_on_today(NOTION_TOKEN,
#                                             "Diária Refletir sobre autenticidade e motivação.",
#                                             "Reserve um momento diário para pensar se o conteúdo produzido reflete quem você é e se está alinhado com seus objetivos; use essa reflexão para ajustar seu percurso quando necessário.",
#                                             "29f2d519d27e8020b1dcdd9a1d022f46",
#                                             DATABASE_ID,
#                                             2, 9)
