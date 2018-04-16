import discord
import asyncio
import time
import requests
import json

token_key = '123213213213123'
channel_ID = "123"

client = discord.Client()

def getCharStatus(accountName):
    r = requests.post('https://www.pathofexile.com/character-window/get-characters', data = {'accountName':accountName})
    jsonArray = r.text
    jsonArray = json.loads(jsonArray)
    return jsonArray

async def my_background_task():
    await client.wait_until_ready()
    counter = 0
    channel = discord.Object(id=channel_ID) #channelID to show messages
    while not client.is_closed:
        #print('Time To check')
        for account in config['accounts']:
            jsonAccount = getCharStatus(account['accountName'])
            for jsonCharac in jsonAccount:
                #print(jsonCharac['league'])
                if jsonCharac['league'] == 'Hardcore Bestiary':
                    if jsonCharac['name'] not in account['aliveChars']:

                        msgNew = account['accountName'] + ' gives another try, ha ha lets see how long it lasts MUUAHAHAH!! ' + jsonCharac['name']
                        print(msgNew)
                        await client.send_message(channel,msgNew)
                        account['aliveChars'].append(jsonCharac['name'])
                        with open('config.json', 'w') as f:
                            json.dump(config, f)

                for configCharac in account['aliveChars']: 
                    if jsonCharac['name'] == configCharac:
                        if jsonCharac['league'] != 'Hardcore Bestiary':

                            msgDead = 'HA HA, U DED, LUL NOOB: ' + jsonCharac['name'] + ' died at level ' + str(jsonCharac['level'])
                            await client.send_message(channel,msgDead)
                            print(msgDead)
                            account['aliveChars'].remove(jsonCharac['name'])
                            #write it back to the file
                            with open('config.json', 'w') as f:
                                json.dump(config, f)
        await asyncio.sleep(60) # task runs every 60 seconds

@client.event
async def on_ready():
    print('Bot ON')

@client.event
async def on_message(message):
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

        
    
with open('config.json', 'r') as f:
    config = json.load(f)



client.loop.create_task(my_background_task())
client.run(token_key)
