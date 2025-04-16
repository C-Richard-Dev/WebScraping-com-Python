from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json

# Configurar o navegador headless sem abrir janela
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

links_produtos = []

# Loop pelas páginas
for pagina in range(1, 75):
    url = f"https://www.artwax.com.br/loja/busca.php?loja=606785&palavra_busca=produtos&pg={pagina}"
    driver.get(url)
    time.sleep(2)

    try:
        elementos_links = driver.find_elements(By.CSS_SELECTOR, "a.product-info")
        for elem in elementos_links:
            link = elem.get_attribute("href")
            if link and link not in links_produtos:
                links_produtos.append(link)
    except Exception as e:
        print(f"Erro ao coletar links na página {pagina}: {e}")

# Salva os links num arquivo json
with open("links_produtos.json", "w", encoding="utf-8") as f:
    json.dump(links_produtos, f, indent=4, ensure_ascii=False)

driver.quit()
print("Coleta de links finalizada com sucesso!")

