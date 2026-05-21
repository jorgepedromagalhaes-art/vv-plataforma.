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
    return ["PDDE", "PNAE"]

async def buscar_no_dou():
    palavras = carregar_palavras()
    hoje = datetime.now().strftime('%Y-%m-%d')
    resultados_finais = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for termo in palavras:
            url_busca = f"https://www.in.gov.br/consulta/-/journal_content/56/10119/2111111?q={termo}&max=100"
            try:
                await page.goto(url_busca, timeout=60000)
                await page.wait_for_timeout(3000) 
                conteudo = await page.content()
                soup = BeautifulSoup(conteudo, 'html.parser')
                artigos = soup.find_all('h5', class_='title-search') or soup.find_all('div', class_='search-result-item')
                
                for art in artigos:
                    link_tag = art.find('a') if art.name != 'a' else art
                    if link_tag and link_tag.get('href'):
                        titulo = link_tag.get_text().strip()
                        link_completo = "https://www.in.gov.br" + link_tag.get('href')
                        resultados_finais.append({
                            "data": hoje,
                            "palavra_chave": termo,
                            "titulo": titulo,
                            "link": link_completo,
                            "extrato": "Clique no link para ler o conteúdo oficial."
                        })
            except:
                continue
        await browser.close()

    historico = []
    if os.path.exists('dados.json'):
        with open('dados.json', 'r', encoding='utf-8') as f:
            try: historico = json.load(f)
            except: historico = []

    links_existentes = {item['link'] for item in historico}
    novos_itens = [item for item in resultados_finais if item['link'] not in links_existentes]
    historico.extend(novos_itens)

    with open('dados.json', 'w', encoding='utf-8') as f:
        json.dump(historico, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    asyncio.run(buscar_no_dou())
