import discord
import asyncio
import time
import requests
import json
from random import randint


client = discord.Client()

config = {} 

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
    await asyncio.sleep(5)
    await client.wait_until_ready()
    counter = 0
    channel = discord.Object(id=config['options']['channel_ID']) #channelID to show messages
    await client.send_message(channel,"I'm Here!")
    while not client.is_closed:
        if 'accounts' in config:
            for account in config['accounts']:
                jsonAccount = getCharStatus(account['accountName'])
                for jsonCharac in jsonAccount:
                    #print(jsonCharac['league'] + '\n')
                    if jsonCharac['league'] == config['options']['leagueName'] :
                        if jsonCharac['name'] not in account['aliveChars']:
                            msgNew = 'Welcome to Wraeclast '+ jsonCharac['name'] + '. Good luck on your journey. (' + account['accountName'] + ')'
                            print(msgNew)
                            await client.send_message(channel,msgNew)
                            account['aliveChars'].append(jsonCharac['name'])
                            write_config()

                    for configCharac in account['aliveChars']: 
                        if jsonCharac['name'] == configCharac:
                            #Auto add new char
                            if jsonCharac['league'] != config['options']['leagueName']:

                                msgDead = getDeathLine() + ' ' + jsonCharac['name'] + ' died at level ' + str(jsonCharac['level']) + '. (' + account['accountName'] + ')' 
                                await client.send_message(channel,msgDead)
                                print(msgDead)
                                account['aliveChars'].remove(jsonCharac['name'])
                                #write it back to the file
                                write_config()

            await asyncio.sleep(60) # task runs every 60 seconds
        else:
            print("no account")

def load_config():
    print("/*load_config")
    global config
    with open('config.json', 'r') as f:
         config = json.load(f)
         print(config)
    print("load_config*/")

def write_config():
    global config
    with open('config.json', 'w') as f:
        f.write(json.dumps(config,indent=4, separators=(',', ': ')))

@client.event
async def on_ready():
    #load_config()
#    client.change_presence(game=Game(name="with humans"))
    await client.change_presence(game=discord.Game(name=config['options']['leagueName']))
    print('Bot ON')

'''
@client.event
async def wait_until_ready():
    print('/*wait_until_ready')
    load_config()
    print('wait_until_ready*/')
'''    

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
            write_config()
        else:
            await client.send_message(message.author, 'Usage: ?add <accountname>')
    
    if message.content.startswith('?ping'):
        channel = discord.Object(id=config['options']['channel_ID'])
        await client.send_message(channel, 'Yeh, I am here')

#write_config()        
load_config()
client.loop.create_task(my_background_task())
print('/*run*/')
client.run(config['options']['token_key'])
