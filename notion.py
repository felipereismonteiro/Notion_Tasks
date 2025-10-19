import os
import dotenv
import requests
from datetime import timezone
from datetime import datetime
dotenv.load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

required = {
    "NOTION_TOKEN": NOTION_TOKEN,
    "DATABASE_ID": DATABASE_ID
}

missing = [name for name, value in required.items() if not value]
if missing:
    print("⚠️ Variáveis ausentes:", ", ".join(missing))
else:
    print("✅ Todas as variáveis de ambiente foram carregadas corretamente.")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_tasks(database_id, filters=None, page_size=100, headers=None):
    """
    Retorna todas as tasks da database do Notion aplicando o filtro fornecido.
    Faz paginação automática até trazer todas as páginas.
    """
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    all_results = []
    payload = {"page_size": page_size}

    if filters is None:
        today = datetime.now(timezone.utc).date().isoformat()
        filters = {
            "and": [
                {
                    "property": "✅ Status",
                    "checkbox": {"equals": False}
                },
                {
                    "property": "📅 Deadline",
                    "date": {"equals": today}
                }
            ]
        }

    if filters:
        payload["filter"] = filters

    headers_to_use = headers or {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    has_more = True
    next_cursor = None

    while has_more:
        if next_cursor:
            payload["start_cursor"] = next_cursor

        print(f"Consultando Tarefas do Notion")

        response = requests.post(url, headers=headers_to_use, json=payload)
        if response.status_code != 200:
            print("Erro ao consultar Notion:", response.status_code, response.text)
            break

        data = response.json()
        all_results.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")

    print(f"Total de tasks encontradas: {len(all_results)}")
    return all_results