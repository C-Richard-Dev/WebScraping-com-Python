import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Ler os links que deram erro
with open("erros.txt", "r", encoding="utf-8") as f:
    links = [linha.strip() for linha in f if linha.strip()]

produtos_tratados = []
novos_erros = []

# Configurar navegador headless para Selenium (usado só se necessário)
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

for i, url in enumerate(links):
    print(f"[{i+1}/{len(links)}] Recuperando: {url}")
    
    try:
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        # Nome do produto
        nome_tag = soup.find("h1")
        nome = nome_tag.get_text(strip=True) if nome_tag else "Nome não encontrado"

        # Inicializar variáveis
        descricao = None
        preco = "Preço não encontrado"
        data = {}

        # Tentar pegar descrição via JSON-LD
        for script_tag in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script_tag.string)
                if isinstance(data, dict) and data.get("@type") == "Product":
                    descricao = data.get("description", "").strip() or "Descrição não encontrada"
                    break
            except Exception:
                continue

        # Se a descrição ainda não foi encontrada, tenta pela <meta>
        if not descricao or descricao == "Descrição não encontrada":
            meta_desc = soup.find("meta", attrs={"name": "description"})
            descricao = meta_desc["content"].strip() if meta_desc and meta_desc.has_attr("content") else "Descrição não encontrada"

        # Tentar pegar preço via HTML
        preco_tag = soup.find("strong", class_="price-first-prod")
        if preco_tag:
            preco = preco_tag.get_text(strip=True)
        else:
            # Tenta via JSON-LD (caso HTML falhe)
            preco = data.get("offers", {}).get("price", "Preço não encontrado")

            # Se ainda não achou o preço, tenta via Selenium
            if not preco or preco == "Preço não encontrado":
                try:
                    driver.get(url)
                    time.sleep(3)
                    selenium_soup = BeautifulSoup(driver.page_source, "html.parser")
                    selenium_preco = selenium_soup.find("strong", class_="price-first-prod")
                    if selenium_preco:
                        preco = selenium_preco.get_text(strip=True)
                except Exception as e:
                    print(f"Falha ao usar Selenium para preço em {url}: {e}")

        # Imagem (pega a primeira imagem da página)
        imagem_tag = soup.find("img")
        imagem = imagem_tag["src"] if imagem_tag and "src" in imagem_tag.attrs else None

        # Marca
        marca_tag = soup.find("div", class_="product-brand")
        marca = marca_tag.get_text(strip=True).replace("Marca:", "").strip() if marca_tag else "Marca não encontrada"

        # Link da tabela FISPQ
        fispq_link = None
        for a_tag in soup.find_all("a", href=True):
            input_tag = a_tag.find("input")
            if input_tag and input_tag.get("value", "").lower() == "download tabela fispq":
                fispq_link = a_tag["href"]
                break

        produto_data = {
            "nome": nome,
            "descricao": descricao,
            "preco": preco,
            "imagem": imagem,
            "link": url,
            "marca": marca,
            "fispq": fispq_link
        }

        produtos_tratados.append(produto_data)

    except Exception as e:
        print(f"Erro novamente em {url}: {e}")
        novos_erros.append(url)

driver.quit()

# Salvar os dados recuperados
with open("produtos_recuperados.json", "w", encoding="utf-8") as f:
    json.dump(produtos_tratados, f, indent=4, ensure_ascii=False)

# Salvar os que ainda deram erro
with open("erros_restantes.txt", "w", encoding="utf-8") as f:
    for link in novos_erros:
        f.write(link + "\n")

print(f"\nTratamento concluído. {len(produtos_tratados)} produtos recuperados. {len(novos_erros)} ainda com erro.")




