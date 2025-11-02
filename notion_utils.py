from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import requests
import dotenv
dotenv.load_dotenv()

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
        today = datetime.now(ZoneInfo("America/Sao_Paulo")).date().isoformat()
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
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    has_more = True
    next_cursor = None

    while has_more:
        if next_cursor:
            payload["start_cursor"] = next_cursor

        response = requests.post(url, headers=headers_to_use, json=payload)
        if response.status_code != 200:
            print("Erro ao consultar Notion:", response.status_code, response.text)
            break

        data = response.json()
        all_results.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")

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

def create_clean_tasks(notion_token):
    """
    Insere 30 novas tasks de limpeza no Notion.
    """
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    descriptions = [
        "Melhora a concentração e o foco nas tarefas diárias.",
        "Aumenta a autoestima e a confiança pessoal.",
        "Promove relacionamentos mais saudáveis e reais.",
        "Reduz a ansiedade e o estresse relacionados ao vício.",
        "Melhora a qualidade do sono e o descanso.",
        "Aumenta a energia e a motivação para atividades produtivas.",
        "Desenvolve maior autocontrole e disciplina.",
        "Melhora a saúde mental e emocional.",
        "Aumenta a produtividade no trabalho ou estudos.",
        "Promove uma visão mais positiva da sexualidade.",
        "Reduz sentimentos de culpa e vergonha.",
        "Melhora a capacidade de lidar com emoções difíceis.",
        "Aumenta o tempo disponível para hobbies e interesses pessoais.",
        "Promove uma vida social mais ativa e satisfatória.",
        "Reduz o risco de desenvolver problemas de saúde relacionados ao vício.",
        "Melhora a clareza mental e a tomada de decisões.",
        "Aumenta a sensação de realização pessoal.",
        "Promove hábitos de vida mais saudáveis em geral.",
        "Reduz a dependência de estímulos artificiais para prazer.",
        "Melhora a conexão consigo mesmo e com os outros.",
        "Aumenta a resiliência emocional diante de desafios.",
        "Promove uma atitude mais positiva em relação à vida.",
        "Reduz o tempo gasto em atividades improdutivas.",
        "Melhora a capacidade de concentração em tarefas importantes.",
        "Aumenta a sensação de controle sobre a própria vida.",
        "Promove uma maior apreciação pelas experiências reais.",
        "Reduz o impacto negativo do vício na vida cotidiana.",
        "Melhora a saúde física geral através de melhores hábitos de vida.",
        "Aumenta a autocompaixão e o cuidado pessoal.",
        "Promove um senso renovado de propósito e direção na vida."
    ]

    base_date = datetime.now(ZoneInfo("America/Sao_Paulo")).date()

    for index, desc in enumerate(descriptions, start=1):
        today_deadline = (base_date + timedelta(days=index - 1)).isoformat()

        payload = {
            "parent": {"database_id": "28a2d519d27e800a9497c0ac949bd784"},
            "icon": {
                "type": "emoji",
                "emoji": "🚫"
            },
            "properties": {
                "🐈 Sistema": {
                    "title": [
                        {"text": {"content": f" Dia {index} sem Pornografia"}}
                    ]
                },
                "🍀 Descrição": {
                    "rich_text": [
                        {"text": {"content": desc}}
                    ]
                },
                "✅ Status": {"checkbox": False},
                "📅 Deadline": {"date": {"start": today_deadline}},
                "Metas": {
                    "relation": [{"id": "28a2d519d27e804194b9f5283a4f950a"}]
                }
            }
        }

        res = requests.post(url, headers=headers, json=payload)
        if res.status_code != 200:
            print(f"Erro no dia {index}: {res.status_code} -> {res.text}")
        else:
            print(f"Tarefa do dia {index} criada com sucesso.")

def create_one_month_daily_tasks_based_on_today(notion_token, taskname, description, meta_relation_id, database_id, inic, fim):
    """
    Insere 30 novas tasks diárias no Notion com base na data de hoje.
    """
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    base_date = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    for index in range(inic, fim):
        today_deadline = (base_date + timedelta(days=index - 1)).isoformat()

        payload = {
            "parent": {"database_id": database_id},
            "icon": {
                "type": "emoji",
                "emoji": "📅"
            },
            "properties": {
                "🐈 Sistema": {
                    "title": [
                        {"text": {"content": f"{taskname}"}}
                    ]
                },
                "🍀 Descrição": {
                    "rich_text": [
                        {"text": {"content": description}}
                    ]
                },
                "✅ Status": {"checkbox": False},
                "📅 Deadline": {"date": {"start": today_deadline}},
                "Metas": {
                    "relation": [{"id": meta_relation_id}]
                }
            }
        }

        res = requests.post(url, headers=headers, json=payload)
        if res.status_code != 200:
            print(f"Erro no dia {index}: {res.status_code} -> {res.text}")
        else:
            print(f"Tarefa diária do dia {index} criada com sucesso.")
