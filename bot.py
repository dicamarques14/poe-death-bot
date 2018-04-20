import discord
import asyncio
import time
import requests
import json
from random import randint

token_key = '1321654156'
channel_ID = "1231531"

client = discord.Client()
config = {}
config['hello'] = 1

def getCharStatus(accountName):
    r = requests.post('https://www.pathofexile.com/character-window/get-characters', data = {'accountName':accountName})
    jsonArray = r.text
    jsonArray = json.loads(jsonArray)
    return jsonArray

def getDeathLine():
    switcher = [
        "For those who ascend too quickly the fall is inevitable .",
        "Why are you so in love with death ?",
        "I fought for God. What did you fight for exile ?",
        "THE TOUCH OF GOD ! ",
        "Justice is served.",
        "Apparently, this is the ending that you deserve."
    ]
    return switcher[randint(0, len(switcher))]

async def my_background_task():

    global config
    load_config()
    await asyncio.sleep(5)
    await client.wait_until_ready()
    counter = 0
    channel = discord.Object(id=channel_ID) #channelID to show messages
    while not client.is_closed:
        #print('Time To check')
        if 'accounts' in config:
            for account in config['accounts']:
                jsonAccount = getCharStatus(account['accountName'])
                for jsonCharac in jsonAccount:
                    #print(jsonCharac['league'])
                    if jsonCharac['league'] == 'Hardcore Bestiary':
                        if jsonCharac['name'] not in account['aliveChars']:

                            msgNew = 'Welcome to Wraeclast '+ jsonCharac['name'] + '. Good luck on your journey'
                            print(msgNew)
                            await client.send_message(channel,msgNew)
                            account['aliveChars'].append(jsonCharac['name'])
                            with open('config.json', 'w') as f:
                                json.dump(config, f)

                    for configCharac in account['aliveChars']: 
                        if jsonCharac['name'] == configCharac:
                            if jsonCharac['league'] != 'Hardcore Bestiary':

                                msgDead = getDeathLine() + ' ' + jsonCharac['name'] + ' died at level ' + str(jsonCharac['level'])
                                await client.send_message(channel,msgDead)
                                print(msgDead)
                                account['aliveChars'].remove(jsonCharac['name'])
                                #write it back to the file
                                with open('config.json', 'w') as f:
                                    json.dump(config, f)
            await asyncio.sleep(60) # task runs every 60 seconds
        else:
            print("no account")

def load_config():
    global config
    with open('config.json', 'r') as f:
         config = json.load(f)

@client.event
async def on_ready():
    load_config()
    print('Bot ON')

@client.event
async def on_message(message):
    
    global config
    if message.content.startswith('?add'):
        
        accountName = message.content.split()
        if len(accountName) == 2:
            await client.send_message(message.author, 'Account ' + accountName[1] +' added. Happy deaths :)')
            print('New Account: '+accountName[1])
            account = {
                "accountName" : accountName[1],
                "aliveChars" : []
            }
            config['accounts'].append(account)
            with open('config.json', 'w') as f:
                json.dump(config, f)
        else:
            await client.send_message(message.author, 'Usage: ?add <accountname>')

        

client.loop.create_task(my_background_task())
client.run(token_key)
