import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin
import time

def get_all_links(url):

    try:
        # Faz uma requisição HTTP para a URL
        response = requests.get(url)
        response.raise_for_status()  # Verifica se houve erros na requisição

        # Processa o HTML com BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encontra todas as tags <a> e extrai os atributos href
        #links = [a['href'] for a in soup.find_all('a', href=True)]
        links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]

        return links
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return []
    except Exception as e:
        print(f"Erro ao processar a página: {e}")
        return []

# Exemplo de uso
url = "https://vaults.docs.diode.io/" #main url all links drive from
links = get_all_links(url)
links_unicos = []
linksDict = {}

#retirando links repetidos
for link in links:
    if link not in links_unicos:
        links_unicos.append(link)

ind = 0

for i in links_unicos:
    linksDict[ind] = str(i)
    ind += 1

with open("diode_DOCS_vaults_sublinks.json", "w", encoding="utf-8") as jsonFile: #file destination to the links
    json.dump(linksDict, jsonFile, indent=4)


