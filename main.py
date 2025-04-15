import requests
from bs4 import BeautifulSoup
import json

# Lista de links do seu JSON original (exemplo)
with open("links_produtos.json", "r", encoding="utf-8") as f:
    links = json.load(f)

produtos = []
erros = []

for i, url in enumerate(links):
    print(f"[{i+1}/{len(links)}] Coletando: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        script_tag = soup.find("script", type="application/ld+json")
        if not script_tag:
            raise ValueError("Script JSON-LD não encontrado")

        try:
            data = json.loads(script_tag.string)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON malformado: {e}")

        # Buscar link da FISPQ
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

        produtos.append(produto_data)

    except Exception as e:
        print(f"Erro ao processar {url}: {e}")
        erros.append(url)

# Salvar os dados coletados
with open("produtos_completos.json", "w", encoding="utf-8") as f:
    json.dump(produtos, f, indent=4, ensure_ascii=False)

# Salvar os links com erro
with open("erros.txt", "w", encoding="utf-8") as f:
    for link in erros:
        f.write(link + "\n")

print(f"\nColeta finalizada! {len(produtos)} produtos salvos. {len(erros)} erros registrados em 'erros.txt'.")
