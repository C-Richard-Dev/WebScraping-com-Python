import requests
from bs4 import BeautifulSoup
import json
import re 

# Lista de links do seu JSON original
with open("links_produtos.json", "r", encoding="utf-8") as f:
    links = json.load(f)

produtos = []
erros = []

for i, url in enumerate(links):
    print(f"[{i+1}/{len(links)}] Coletando: {url}")
    
    try:
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        script_tag = soup.find("script", type="application/ld+json")
        try:
            data = json.loads(script_tag.string) if script_tag else {}
        except json.JSONDecodeError:
            data = {}

        # Buscar link da tabela fispq
        fispq_link = None
        for a_tag in soup.find_all("a", href=True):
            input_tag = a_tag.find("input")
            if input_tag and input_tag.get("value", "").lower() == "download tabela fispq":
                fispq_link = a_tag["href"]
                break

        # Capturando o nome pelo html
        nome_tag = soup.find("h1", class_="product-name")
        nome_completo = nome_tag.get_text(separator="\n", strip=True) if nome_tag else data.get('product-name') 

        # Configurando para que a descrição seja capturada na tag div do Html da pagina
        descricao_tag = soup.find("div", class_="tab rte description-ab active")
        descricao_completa = descricao_tag.get_text(separator="\n", strip=True) if descricao_tag else data.get('description')

        # Capturando o preço pelo html
        preco_tag = soup.find("span", id="info_preco")
        preco_completo = preco_tag.get_text(separator="", strip=True) if preco_tag else None
        preco_formatado = None # Formatando o preco para que capture apenas o valor monetário do produto 
        if preco_completo:
            match = re.search(r'R\$[\d.,]+', preco_completo)
            if match:
                preco_formatado = match.group(0)

        # Capturando a imagem pelo html
        imagem_tag = soup.find("img", class_="swiper-lazy")
        if imagem_tag:
            imagem_completa = imagem_tag.get("src") or imagem_tag.get("data-src")
        else:
            imagem_completa = None

        # Capturando a marca pelo html
        marca_tag = soup.find("div", class_="product-brand")
        marca_completo = marca_tag.get_text(strip=True) if marca_tag else data.get('product-brand')

        produto_data = {
            "nome":  nome_completo,
            "descricao": descricao_completa,
            "preco": preco_formatado,
            "imagem": imagem_completa,
            "link": url,
            "marca": marca_completo,
            "fispq": fispq_link
        }

        produtos.append(produto_data)

    except Exception as e:
        print(f"Erro ao processar {url}: {e}")
        erros.append(url)

# Salvar os dados coletados
with open("produtos.json", "w", encoding="utf-8") as f:
    json.dump(produtos, f, indent=4, ensure_ascii=False)

# Salvar os links com erro
with open("erros.txt", "w", encoding="utf-8") as f:
    for link in erros:
        f.write(link + "\n")

print(f"\nColeta finalizada! {len(produtos)} produtos salvos. {len(erros)} erros registrados em 'erros.txt'.")
