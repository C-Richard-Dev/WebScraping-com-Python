import requests
from bs4 import BeautifulSoup
import json

# Lista de links do seu JSON original
with open("link_teste.json", "r", encoding="utf-8") as f:
    links = json.load(f)

produtos = []
erros = []

for i, url in enumerate(links):
    print(f"[{i+1}/{len(links)}] Coletando: {url}")
    
    try:
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        script_tag = soup.find("script", type="application/ld+json")
        if not script_tag:
            raise ValueError("Script JSON-LD não encontrado")

        try:
            data = json.loads(script_tag.string)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON ERRO: {e}")

        # Buscar link da tabela fispq
        fispq_link = None
        for a_tag in soup.find_all("a", href=True):
            input_tag = a_tag.find("input")
            if input_tag and input_tag.get("value", "").lower() == "download tabela fispq":
                fispq_link = a_tag["href"]
                break


        

        # Configurando para que a descrição seja capturada na tag div do Html da pagina
        descricao_tag = soup.find("div", class_="tab rte description-ab active")
        descricao_completa = descricao_tag.get_text(separator="\n", strip=True) if descricao_tag else data.get('description')

        produto_data = {
            "nome": data.get("name"),
            "descricao": descricao_completa,
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
with open("produtos_teste.json", "w", encoding="utf-8") as f:
    json.dump(produtos, f, indent=4, ensure_ascii=False)

# Salvar os links com erro
with open("erros_teste.txt", "w", encoding="utf-8") as f:
    for link in erros:
        f.write(link + "\n")

print(f"\nColeta finalizada! {len(produtos)} produtos salvos. {len(erros)} erros registrados em 'erros.txt'.")
