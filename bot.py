import discord
import asyncio
import time
import requests
import traceback
import json
from random import randint


client = discord.Client()
channel = None
config = {} 

def getCharStatus(accountName):
    try:
        r = requests.post('https://www.pathofexile.com/character-window/get-characters', data = {'accountName':accountName})  
        jsonArray = r.text
        try:
            jsonArray = json.loads(jsonArray)
            return jsonArray
        except:
            print('Except json')
            return json.loads("[]")
    except requests.exceptions.RequestException as e:  
        print(e)
        return json.loads("[]")

    

def getDeathLine():
    switcher = [
        "For those who ascend too quickly the fall is inevitable .",
        "Why are you so in love with death ?",
        "I fight for god, who do you fight for exile?",
        "THE TOUCH OF GOD ! ",
        "Justice is served.",
        "Apparently, this is the ending that you deserve."
    ]
    return switcher[randint(0, len(switcher)-1)]

async def add_new_char(charName,accountName,aliveCharsArray):
    msgNew = 'Welcome to Wraeclast '+ charName + '. Good luck on your journey. (' + accountName + ')'

    embed = discord.Embed(title=':tada: Welcome to Wraeclast :tada:', colour=0xe74c3c) #Red
    embed.add_field(name='Player', value=accountName)
    embed.add_field(name='Character', value=charName)

    print(msgNew)
    await client.send_message(channel,embed=embed)
    
    #write it back to the file
    aliveCharsArray.append(charName)
    write_config()

async def kill_char(account,jsonCharac):
    if 'totalDeaths' in account:
        account['totalDeaths'] += 1
    else:
        account['totalDeaths'] = 1

    msgDead = getDeathLine() + ' ' + jsonCharac['name'] + ' died at level ' + str(jsonCharac['level']) + '. [Death count : ' + str(account['totalDeaths'])+ '] ('+ account['accountName'] + ')' 
    
    embed = discord.Embed(title=':coffin: RIP :coffin: ' + getDeathLine(), colour=0xe74c3c) #Red
    embed.add_field(name='Player', value= account['accountName'])
    embed.add_field(name='Character', value=jsonCharac['name'])
    embed.add_field(name='Level', value= str(jsonCharac['level']))
    embed.add_field(name='Death count', value= str(account['totalDeaths']))
    
    print(msgDead)
    await client.send_message(channel,embed=embed)
    
    #write it back to the file
    account['aliveChars'].remove(jsonCharac['name'])
    write_config()

async def check_accounts():
    global channel
    for account in config['accounts']:
        jsonAccount = getCharStatus(account['accountName'])
        for jsonCharac in jsonAccount:
            #Auto add new char
            if 'league' in jsonCharac:
                if jsonCharac['league'] == config['options']['leagueName'] :
                    if jsonCharac['name'] not in account['aliveChars']:
                        await add_new_char(jsonCharac['name'],account['accountName'],account['aliveChars'])

                for configCharac in account['aliveChars']: 
                    if jsonCharac['name'] == configCharac:
                        if jsonCharac['league'] != config['options']['leagueName']:
                            await kill_char(account,jsonCharac)


def load_config():
    print("/*load_config")
    global config
    with open('config.json', 'r') as f:
        config = json.load(f)
         
    if 'token_key' in config['options']:
        print("load_config*/")
    else:
        print("Corrupted config file")
        quit()

def write_config():
    global config
    with open('config.json', 'w') as f:
        f.write(json.dumps(config,indent=4, separators=(',', ': ')))

@client.event
async def on_ready():
    global channel
    channel = discord.Object(id=config['options']['channel_ID']) #channelID to show messages
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
async def on_error(event, *args, **kwargs):
    embed = discord.Embed(title=':x: Event Error', colour=0xe74c3c) #Red
    embed.add_field(name='Event', value=event)
    #embed.description = '```py\n%s\n```' % traceback.format_exc()
    #embed.timestamp = datetime.datetime.utcnow()
    print("err"+event + " " + traceback.format_exc())
    await client.send_message(channel,embed=embed)

@client.event
async def on_message(message):
    
    global config
    global channel
    exists = False
    if message.content.startswith('?add'):
        
        accountName = message.content.split()
        if len(accountName) == 2:
            for account in config['accounts']:
                if account['accountName'] == accountName[1] :
                    exists = True
                    break
            
            if exists :
                await client.send_message(message.author, 'Account ' + accountName[1] + ' already added! Nice try, effjay -_-')
            else:
                await client.send_message(message.author, 'Account ' + accountName[1] +' added. Happy deaths :)')
                print('New Account: '+accountName[1])
                account = {"accountName" : accountName[1],"aliveChars" : []}
                config['accounts'].append(account)
                write_config()
        else:
            await client.send_message(message.author, 'Usage: ?add <accountname>')
    
    if message.content.startswith('?ping'):
        await client.send_message(channel, 'Yeh, I am here')

    if message.content.startswith('?update'):
        print('Update forced')
        await check_accounts()
        await client.send_message(channel, 'Forcing Update...')    
    
    if message.content.startswith('?list'):
        ToSend = 'Accounts List: '

        for account in config['accounts']:
            ToSend = ToSend + account['accountName'] + ', '
        
        await client.send_message(channel, ToSend)
    
    if message.content.startswith('?league'):
        leagueName = message.content.split()
        name = ""
        if len(leagueName) >= 2:
            for i in range(len(leagueName)):
                if i == 0:
                    continue
                name += leagueName[i]
                if i != len(leagueName) - 1:
                    name += " "
            print('Update league: '+name)
            config['options']['leagueName'] = name
            await client.change_presence(game=discord.Game(name=config['options']['leagueName']))
            write_config()
            
            await client.send_message(channel, 'New league set: '+config['options']['leagueName']+'.')
        else:
            await client.send_message(channel, 'Usage: ?league <leagueName>')

async def my_background_task():

    global config
    global channel
    await asyncio.sleep(5)
    print("Waiting Client") 
    await client.wait_until_ready()  
    print("Client Ready")
    while not client.is_closed:
        if 'accounts' in config:
            await check_accounts()
            await asyncio.sleep(40) # task runs every 60 seconds
        else:
            print("no account")
            quit()
    print("RAGE QUIT")

#write_config()        
load_config()
client.loop.create_task(my_background_task())
print('/*run*/')

if 'token_key' in config['options']:
    try:
        client.run(config['options']['token_key'])
    except:
        print('Except client.run')
else:
    print('Missing Token in config file')
    quit()

print('imhere')
