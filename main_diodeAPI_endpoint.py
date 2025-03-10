import asyncio
import json
import logging
import os
import sys
import websockets
import websockets.exceptions
from jsonrpcclient import request, parse, Ok
import time
import openAi_APImodule as assist

#bearer_token, zone_id, channel_id, device_id must be generated using the Diode Collab app

bearer_token = ""
zone_id = ""
channel_id = ""
device_id = ""
diode_url = f"https://{device_id}.diode.link/api/json_rpc"
diode_wss_uri = f"wss://{device_id}.diode.link/api/json_rpc/ws"
method_send_msg = "send_message"
method_auth = "authenticate"
method_subscribe = "subscribe_channel"
method = method_send_msg


def textProbe(content):
    if type(content) == type({}):
        with open("textProbe.txt", "a") as file:
            json.dump(content, file, indent=4, ensure_ascii=False)
        with open("textProbe.txt", "a") as file:
            file.write("\n \n")

    elif not isinstance(content, str):
        content = str(content)
        with open("textProbe.txt", "a") as file:   
            file.write(content + "\n \n")   
    else:
        with open("textProbe.txt", "a") as file:
            file.write(content + "\n \n")

def json_filter(jsonInput):
    keys = jsonInput.keys()
    subkey01 = jsonInput['result']
    subkey02 = jsonInput['result']['messages']
    subkey03 = subkey02[0]
    zone_id = subkey03['zone_id']
    group_id = subkey03['group_id']
    sender_keys = subkey03['sender'].keys()
    #print(f"Sender keys are:  {sender_keys} ", '\n')
    #print(json.load(jsonInput))


def base_payload():
    return {"jsonrpc": "2.0"}

def handle_exception(e):
    if isinstance(e, websockets.exceptions.WebSocketException):
        print(f"WebSocket error: {e}")
    elif isinstance(e, websockets.exceptions.ConnectionClosedError):
        print(f"Conn closed unexpectedly: {e}")
    elif isinstance(e, json.JSONDecodeError):
        print(f"JSON decoding err: {e}")
    elif isinstance(e, asyncio.TimeoutError):
        print(f"Timed out request: {e}")
    else:
        print(f"An unexpected error occurred: {e}")


async def send_auth(websocket):
    paramsJson = {}
    paramsJson["token"] = bearer_token
    params = paramsJson 
    payload = base_payload()
    payload["method"] = method_auth 
    payload["params"] = params
    payload["id"] = 1
    message = json.dumps(payload)
    await websocket.send(message)
    response = await websocket.recv()
    return json.loads(response)


async def subscribe_channel(websocket):
    paramsJson = {}
    paramsJson["zone_id"] = zone_id
    paramsJson["channel_id"] = channel_id
    payload = base_payload()
    payload["method"] = method_subscribe
    payload["params"] = paramsJson
    payload["id"] = 1
    message = json.dumps(payload)
    await websocket.send(message)
    response = await websocket.recv()
    return json.loads(response)


async def subscribe_all_channels_in_zone(websocket):
    payload = {
        "jsonrpc": "2.0",
        "method": "subscribe_all_channels_in_zone",
        "params": {"zone_id": zone_id},
        "id": 1 
    }

    await websocket.send(json.dumps(payload))
    response = await websocket.recv() 
    return json.loads(response)

async def send_message(incoming_msgJson):

    user_message = incoming_msgJson['result']['messages'][0]['message']
    print(user_message)

    threadId = 'thread_KkXT3xFBE08psDSejojUJAAb' #this is genesis thread for testinag
    
    usr_zone_id = incoming_msgJson['result']['messages'][0]['zone_id']
    group_id = incoming_msgJson['result']['messages'][0]['group_id']
    print('\n', f"zone_id = {usr_zone_id}")
    print('\n', f"zone_id == usr_zone_id => {zone_id == usr_zone_id}")
    print('\n', f"channel_id == group_is => {channel_id == group_id}")
    print('\n', f"group_id = {group_id}")
    
    assistant_answer = assist.user_message_to_assistant(user_message, threadId)

    send_msg_payload = {"jsonrpc":"2.0",
                        "method":"send_message",
                        "params": {"zone_id": usr_zone_id, 
                                   "channel_id": group_id, 
                                   "message_text": assistant_answer 
                                  }, 
                        "id": None}

    return send_msg_payload

# message receiver
async def receive_messages():
    try:
        print(diode_wss_uri)
        async with websockets.connect(diode_wss_uri) as websocket:
            try:
                # initial authentication
                resp = await send_auth(websocket)
                print(resp)

                # subscribe to the diode channel
                resp = await subscribe_channel(websocket)
                print(resp)
                
                # subscribe to all channels to get all users IDs
                resp = await subscribe_all_channels_in_zone(websocket)
                print(resp)


            except Exception as e:
                handle_exception(e)
                sys.exit(1)

            while True:
                message = await websocket.recv()
                message = json.loads(message)
                json_filter(message)
                answer = await send_message(message)
                print(type(answer))
                await websocket.send(json.dumps(answer))
                #await subscribe_all_channels_in_zone(websocket)


    except KeyboardInterrupt:
        print("Program exit. Interrupted by user")
    except Exception as e:
        print(f"An error occurred upon connection attempt: {e}")


# main loop
asyncio.run(receive_messages())

