import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from notion_utils import get_tasks
import dotenv
dotenv.load_dotenv()
from habitica.completed_tasks import get_completed_habits
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

tasks = get_tasks(DATABASE_ID, NOTION_TOKEN,
    filters={
        "and": [
            {
                "property": "✅ Status",
                "checkbox": {"equals": False}
            }
        ]
    }
)
print("Tarefas do notion: ")
for task in tasks:
    print(f"- {task['nome']} (ID: {task['id']})")