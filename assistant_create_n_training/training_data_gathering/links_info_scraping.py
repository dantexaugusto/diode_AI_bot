import requests
from bs4 import BeautifulSoup
import openai
import json
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def scrape_webpage(url):
    """
    Scrapes the content of a webpage and returns the text.
    """
    if not url.startswith(("https://", "http://")):
        url = "https://" + url
    #print(url,"\n")
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        clean_text = text.splitlines()
        clean_text = [element.strip()
                      for element in clean_text if element.strip()]
        clean_text = '\n'.join(clean_text)

        #print(clean_text)

        return clean_text

    else:
        print("Busca do site falhou \n")
        print(response.status_code, "\n")
        return "Failed to retrieve the website content."


def chat_completion_request(model, messages, tools):
    """
    Sends a request to the OpenAI API to generate a chat response.
    """
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools
    )
    return response


def chat_with_tools(model, messages, tools):
    """
    Checks if a responsed called a tool (funtion), apply this tool and return the response.
    """
    try:
        response = chat_completion_request(model, messages, tools)
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls:
            # Assuming there's only one tool call per message for simplicity
            tool_call = tool_calls[0]
            if tool_call.function.name == "scrape_webpage":
                url_to_scrape = json.loads(
                    tool_call.function.arguments)["url"]
                scraping_result = scrape_webpage(url_to_scrape)
                messages.append(
                    {"role": "assistant", "content": f"Scraping result: {scraping_result}"})
                response_with_data = chat_completion_request(
                    model, messages, tools)
                return {"content": response_with_data.choices[0].message.content, "internet_search": True}

        else:
            return {"content": response.choices[0].message.content, "internet_search": False}

    except Exception as e:
        print(f"An error occurred: {e}")


tools = [
    {
        "type": "function",
        "function": {
            "name": "scrape_webpage",
            "description": "Scrape the content of the specified webpage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the webpage to scrape, it can have the http, https protocol or none and just have the domain.",
                    }
                },
                "required": ["url"],
            },
        }
    }
]

#messages = [
#    {"role": "system", "content": "You're an intelligent assistant. \
#     When an URL is mentioned, use the function tool to scrape the content of the webpage."},
#    {"role": "user", "content": "What is this page about: http://diode.io give me summary and list the main information the page is trying to pass."}
#]

model = "gpt-4o-mini"

with open("clean_jsons/clean_diode_DOCS_vaults_sublinks.json", "r") as arquivo:
    dicionario = json.load(arquivo)

#chavesTeste = ["0","1","2","3","4"]  #any dictionay keys for testing purpouses

for x in dicionario:

    link = dicionario[x]

    messages = [
        {"role": "system", "content": "You're an intelligent assistant. \
            When an URL is mentioned, use the function tool to scrape the content of the webpage."},
        {"role": "user", "content": f"What is this page about: {link} give me the main information the page is trying to pass, give me in detail all important technical information regarding links, command line commands, systems instalation and code. Everytime a new links is passed for analysis you start your response with this specifics link page's title."}
    ]

    modelResponse = chat_with_tools(model, messages, tools)
    ai_response = modelResponse["content"]

    
    if ai_response != type(""):
        with open("diode_DOCS_vaults_AI_info.txt", "a") as infos:
            infos.write(str(ai_response))
    
    else:
        with open("diode_DOCS_vaults_AI_info.txt", "a") as infos:
            infos.write(ai_response)

