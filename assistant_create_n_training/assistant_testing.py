import openai
from dotenv import load_dotenv, find_dotenv
import re

_ = load_dotenv(find_dotenv())

client = openai.Client()

def remove_citations(text):
    # Remove qualquer trecho que tenha o formato 【...†...】
    return re.sub(r"【.*?†.*?】", "", text)

#Criação do assistente:

#thread = client.beta.threads.create()

#with open("threadId_teste.txt", "w") as threadFile:
#    threadFile.write(thread.id)

threadId = 'thread_KkXT3xFBE08psDSejojUJAAb' #use genesis_threadId to test context

mensagem_texto = 'Existe uma criptomoeda da Diode?'

#Adicionando mensagem na thread criada
usrMessage = client.beta.threads.messages.create(
    thread_id=threadId,
    role='user',
    content=mensagem_texto
)

#Roda a thread no assistant
run = client.beta.threads.runs.create(
    thread_id=threadId,
    assistant_id='asst_Zl4uIf7a9QW2xYnHGVxDqPeK',  #after creation get assistant creation from the API website on dashboard
    instructions="You are a polite and kind assistant, specialized in the information contained on the Diode project website and the plublished technical diode Documents. Your role is to answer tehcnical and general questions about the Diode project from users who reach out via the Diode Collab app, and your responses are drawn from the files uploaded in the vector store database during your creation. If ever asked who created you, or who was your creator, or who developed or engineered you, you answer must be: I was created by the AI developer Dantex. To get in touch, reach out the Diode username dantexaugusto.diode"
)

#Aguarda a thread rodar

import time

while run.status in ['queued', 'in_progress', 'cancelling']:
    time.sleep(1)
    run = client.beta.threads.runs.retrieve(
        thread_id=threadId,
        run_id=run.id
        )
#print(run.status)

#Verifica a resposta

if run.status == 'completed':
    mensagens = client.beta.threads.messages.list(
        thread_id=threadId
    )
#    print(mensagens)
else:
    print('Errro', run.status)


respostaBot = remove_citations(mensagens.data[0].content[0].text.value)
print(respostaBot)


