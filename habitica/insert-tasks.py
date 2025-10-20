import os
import sys
import dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from notion_utils import get_tasks, NOTION_TOKEN, DATABASE_ID
from datetime import date, timezone, datetime, timedelta
from zoneinfo import ZoneInfo
import requests

dotenv.load_dotenv()

API_KEY = os.getenv('API_KEY')
USER_ID = os.getenv('USER_ID')

required = {
    "API_KEY": API_KEY,
    "USER_ID": USER_ID
}

today = datetime.now(ZoneInfo("America/Sao_Paulo")).date().isoformat()

missing = [name for name, value in required.items() if not value]
if missing:
    print("⚠️ Variáveis ausentes:", ", ".join(missing))
else:
    print("✅ Todas as variáveis de ambiente foram carregadas corretamente.")

def sync_daily_tasks():
    filter = {
        "and": [
            {
                "property": "🐈 Sistema",
                "title": {"contains": "(Diáriamente)"}
            },
            {
                "property": "📅 Deadline",
                "date": {"equals": today}
            }
        ]
    }

    tasks = get_tasks(DATABASE_ID,NOTION_TOKEN, filters=filter)

    # gera data de amanhã
    tomorrow = datetime.utcnow() + timedelta(days=1)
    start_date = tomorrow.isoformat() + "Z"

    # lembrete às 06:00 (UTC)
    reminder_time = tomorrow.replace(hour=6, minute=0, second=0, microsecond=0).isoformat() + "Z"

    for task in tasks:
        data = {
            "text": task["nome"],
            "type": "daily",
            "notes": task["Descricao"],
            "priority": 2,  # 1=normal, 1.5=importante, 2=crítico
            "frequency": "daily",
            "startDate": start_date,
            "repeat": {
                "m": True, "t": True, "w": True,
                "th": True, "f": True, "s": True, "su": True
            },
            "reminders": [
                {
                    "time": reminder_time
                }
            ]
        }

        res = requests.post("https://habitica.com/api/v3/tasks/user", headers={
        "x-api-user": USER_ID,
        "x-api-key": API_KEY,
        "x-client": f"{USER_ID}-habitify-notion",
        "Content-Type": "application/json"
    }, json=data)

        if res.status_code == 201:
            print("✅ Diária criada com sucesso!")
            print(res.json())
        else:
            print("⚠️ Erro ao criar diária:", res.status_code, res.text)

def sync_weekly_tasks():
    filter = {
        "and": [
            {
                "property": "🐈 Sistema",
                "title": {"contains": "Semanal"}
            },
            {
                "property": "📅 Deadline",
                "date": {"equals": today}
            }
        ]
    }

    tasks = get_tasks(DATABASE_ID,NOTION_TOKEN, filters=filter)

    # gera data de amanhã
    tomorrow = datetime.utcnow() + timedelta(days=1)
    start_date = tomorrow.isoformat() + "Z"

    # lembrete às 06:00 (UTC)
    reminder_time = tomorrow.replace(hour=6, minute=0, second=0, microsecond=0).isoformat() + "Z"

    for task in tasks:
        data = {
            "text": task["nome"],
            "type": "daily",
            "notes": task["Descricao"],
            "priority": 2,  # 1=normal, 1.5=importante, 2=crítico
            "frequency": "weekly",
            "startDate": start_date,
            "repeat": {
                "m": True
            },
            "reminders": [
                {
                    "time": reminder_time
                }
            ]
        }

        res = requests.post("https://habitica.com/api/v3/tasks/user", headers={
        "x-api-user": USER_ID,
        "x-api-key": API_KEY,
        "x-client": f"{USER_ID}-habitify-notion",
        "Content-Type": "application/json"
    }, json=data)

        if res.status_code == 201:
            print("✅ Diária semanal criada com sucesso!")
            print(res.json())
        else:
            print("⚠️ Erro ao criar diária semanal:", res.status_code, res.text)


def sync_by_meta():
    META_ID = "28a2d519d27e80539db1fbdaf723383b"

    filtro = {
        "and": [
            {
                "property": "Metas",
                "relation": {"contains": META_ID}
            }
        ]
    }

    # busca as tasks da meta no Notion
    tasks = get_tasks(DATABASE_ID, NOTION_TOKEN, filters=filtro)
    print(f"🔎 {len(tasks)} tarefas encontradas para a meta {META_ID}")

    for t in tasks:
        # garante que os campos existam
        nome = t.get("nome", "Tarefa sem nome")
        descricao = t.get("Descricao", "")
        deadline = t.get("deadline")

        print(f"➡️ Criando tarefa '{nome}' no Habitica com deadline '{deadline}'")

        # monta lembrete às 06h (UTC convertido de Brasília)
        reminders = []
        if deadline:
            try:
                local = datetime.fromisoformat(deadline).replace(
                    hour=6, minute=0, second=0, microsecond=0,
                    tzinfo=ZoneInfo("America/Sao_Paulo")
                )
                reminder_utc = local.astimezone(ZoneInfo("UTC")).isoformat().replace("+00:00", "Z")
                reminders = [{"time": reminder_utc}]
            except Exception as e:
                print(f"⚠️ Erro ao converter deadline '{deadline}': {e}")

        payload = {
            "text": nome,
            "type": "todo",
            "notes": descricao,
            "priority": 2,
        }

        # adiciona data e lembrete se houver deadline
        if deadline:
            payload["date"] = f"{deadline}T00:00:00Z"
        if reminders:
            payload["reminders"] = reminders

        res = requests.post(
            "https://habitica.com/api/v3/tasks/user",
            headers={
                "x-api-user": USER_ID,
                "x-api-key": API_KEY,
                "x-client": f"{USER_ID}-habitify-notion",
                "Content-Type": "application/json"
            },
            json=payload
        )

        if res.status_code == 201:
            print(f"✅ '{nome}' criada no Habitica!")
        else:
            print(f"⚠️ Erro ao criar '{nome}':", res.status_code, res.text)


