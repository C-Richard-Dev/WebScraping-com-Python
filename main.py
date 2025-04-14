import requests
from bs4 import BeautifulSoup
import json

url = "https://www.artwax.com.br/uso-externo/revelax-vonixx-3l"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Nome do produto (pego do <title>)
nome = soup.title.text.strip()

# Descrição via JSON-LD
script_tag = soup.find("script", type="application/ld+json")
if script_tag:
    data = json.loads(script_tag.string)

    # Procurar o link da FISPQ (buscando input com valor específico)
    fispq_link = None
    for a_tag in soup.find_all("a", href=True):
        input_tag = a_tag.find("input")
        if input_tag and input_tag.get("value", "").lower() == "download tabela fispq":
            fispq_link = a_tag["href"]
            break

    produto_data = {
        "nome": data.get("name"),
        "descricao": data.get("description"),
        "preco": data.get("offers", {}).get("price"),
        "imagem": data.get("image"),
        "link": data.get("offers", {}).get("url"),
        "marca": data.get("brand", {}).get("name"),
        "fispq": fispq_link
    }

    # Salvar em JSON
    with open("produto_ldjson.json", "w", encoding="utf-8") as f:
        json.dump([produto_data], f, indent=4, ensure_ascii=False)

    print("Dados salvos com sucesso!")
else:
    print("Script JSON-LD não encontrado.")