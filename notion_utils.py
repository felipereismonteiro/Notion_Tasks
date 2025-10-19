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

def get_tasks(database_id, notion_token, filters=None, page_size=100):
    """
    Retorna todas as tasks da database do Notion aplicando o filtro fornecido.
    Faz paginação automática até trazer todas as páginas.
    """
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

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
    return [
        {
            "id": t["id"],
            "nome": t["properties"]["🐈 Sistema"]["title"][0]["text"]["content"],
            "Descricao": t["properties"]["🍀 Descrição"]["rich_text"][0]["text"]["content"] if t["properties"]["🍀 Descrição"]["rich_text"] else "",
            "status": t["properties"]["✅ Status"]["checkbox"],
            "deadline": t["properties"]["📅 Deadline"]["date"]["start"] if t["properties"]["📅 Deadline"]["date"] else None
        }
        for t in all_results
    ]

def complete_task(task_id, notion_token):
    """
    Marca a task como completa no Notion.
    """
    url = f"https://api.notion.com/v1/pages/{task_id}"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    payload = {
        "properties": {
            "✅ Status": {
                "checkbox": True
            }
        }
    }
    response = requests.patch(url, headers=headers, json=payload)
    if response.status_code != 200:
        print("Erro ao atualizar tarefa no Notion:", response.status_code, response.text)
        return False
    return True