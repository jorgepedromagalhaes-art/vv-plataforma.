
              import os
import json
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

def carregar_palavras():
    if os.path.exists('palavras_chave.txt'):
        with open('palavras_chave.txt', 'r', encoding='utf-8') as f:
            return [linha.strip() for linha in f if linha.strip()]
    return ["MINISTÉRIO"]

async def buscar_no_dou():
    palavras = carregar_palavras()
    hoje = datetime.now().strftime('%Y-%m-%d')
    resultados_finais = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        page = await browser.new_page()

        for termo in palavras:

            url_busca = f"https://www.in.gov.br/consulta/-/buscar/dou?q={termo}"

            try:
                print(f"Buscando: {termo}")

                await page.goto(url_busca, timeout=60000)

                await page.wait_for_load_state("networkidle")

                await page.wait_for_timeout(5000)

                conteudo = await page.content()

                with open("debug.html", "w", encoding="utf-8") as f:
                    f.write(conteudo)

                soup = BeautifulSoup(conteudo, 'html.parser')

                links = soup.find_all('a')

                encontrados = 0

                for link in links:

                    href = link.get('href')
                    titulo = link.get_text(strip=True)

                    if href and "/web/dou/" in href and len(titulo) > 10:

                        link_completo = "https://www.in.gov.br" + href

                        resultados_finais.append({
                            "data": hoje,
                            "palavra_chave": termo,
                            "titulo": titulo,
                            "link": link_completo,
                            "extrato": "Clique no link para ler o conteúdo oficial."
                        })

                        encontrados += 1

                print(f"Encontrados: {encontrados}")

            except Exception as e:
                print(f"ERRO: {e}")

        await browser.close()

    links_unicos = {}

    for item in resultados_finais:
        links_unicos[item['link']] = item

    lista_final = list(links_unicos.values())

    with open('dados.json', 'w', encoding='utf-8') as f:
        json.dump(lista_final, f, ensure_ascii=False, indent=4)

    print(f"Total salvo: {len(lista_final)}")

if __name__ == "__main__":
    asyncio.run(buscar_no_dou())
