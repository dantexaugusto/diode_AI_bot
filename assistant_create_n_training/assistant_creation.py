import openai
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

client = openai.Client()

#Criação do assistente:

vector_store = client.beta.vector_stores.create(name = "Diode Main Website Info and diode Docs info.")

files = ['training_data_gathering/clean_data2vectorDB/diode_main_site_AI_info.txt',
         'training_data_gathering/clean_data2vectorDB/diode_DOCS_app_AI_info.txt',
         'training_data_gathering/clean_data2vectorDB/diode_DOCS_cli_AI_info.txt',
         'training_data_gathering/clean_data2vectorDB/diode_DOCS_network_AI_info.txt',
         'training_data_gathering/clean_data2vectorDB/diode_DOCS_vaults_AI_info.txt'
         ]

file_stream = [open(f, 'rb') for f in files]

file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id,
    files=file_stream
)

#print(file_batch.status)
#print(file_batch.file_counts)

assitant = client.beta.assistants.create(
    name="Diode AI Assistant 2.0",
    instructions="You are a polite and kind assistant, specialized in the information contained on the Diode project website and the plublished technical diode Documents. Your role is to answer tehcnical and general questions about the Diode project from users who reach out via the Diode Collab app, and your responses are drawn from the files uploaded in the vector store database during your creation. If ever asked who created you, or who was your creator, or who developed or engineered you, you answer must be: I was created by the AI developer Dantex. To get in touch, reach out the Diode username dantexaugusto.diode",
    tools=[{'type': 'file_search'}],
    tool_resources={'file_search': {'vector_store_ids': [vector_store.id]}},
    model='gpt-3.5-turbo-0125'
)

#Criando uma thread

thread = client.beta.threads.create()
genesis_threadId = thread.id

with open("assistant_genesis_threadId.txt", "w") as threadFile:
    threadFile.write(genesis_threadId)

mensagem_texto = 'Diode é um sistem de VPN?'
#mensagem_texto = 'Segundo o documento fornecido, Quais são o produtos de vocês?'

#Adicionando mensagem na thread criada
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role='user',
    content=mensagem_texto
)

#Roda a thread no assistant
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assitant.id,
    instructions="The user can be anyone approaching the assistant via the Diode Collab app, interested in general or specific information about the Diode Network project."
)


#Aguarda a thread rodar

import time

while run.status in ['queued', 'in_progress', 'cancelling']:
    time.sleep(1)
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
#print(run.status)

#Verifica a resposta

if run.status == 'completed':
    mensagens = client.beta.threads.messages.list(
        thread_id=thread.id
    )
#    print(mensagens)
else:
    print('Errro', run.status)


print(mensagens.data[0].content[0].text.value)
print('\n \n')
print(message.content[0].text.value)




