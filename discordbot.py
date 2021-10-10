import discord
import requests
from bs4 import BeautifulSoup as bs

##COPY AND PASTE DISCORD BOT TOKEN HERE
token = ""

client = discord.Client()
headers = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
}

@client.event
async def on_ready():
    print('ready')

@client.event
async def on_message(message):
    if message.content.startswith('.walmart-add'):

        pid = message.content.split(' ')[1]
        r = requests.get('https://www.walmart.com/ip/chuckerz/{0}'.format(pid), headers=headers)
        soup = bs(r.text, 'html.parser')
        title = soup.find('title').get_text()
        with open ('walmart.txt', 'r') as reader:
            itemlist = reader.read().splitlines()


        if "Error Page" not in title:
            if pid not in itemlist:
                with open('walmart.txt', 'a') as writer:
                    writer.write('\n' + pid)
                await message.channel.send("Successfully added PID")
            else:
                await message.channel.send(pid + " is already being monitored")
        else:
            await message.channel.send("Invalid PID: " + pid)

    if message.content.startswith('.walmart-remove'):
        pid = message.content.split(' ')[1]
        with open ('walmart.txt', 'r') as reader:
            itemlist = reader.read().splitlines()

        if pid in itemlist:
            new_file = open("walmart.txt", "w")
            for item in itemlist:
                if item != pid:
                    new_file.write(item + '\n')
            await message.channel.send("Successfully removed " + pid)
        else:
            await message.channel.send("PID not in monitored item list")

    if message.content.startswith('.walmart-list'):
        with open ('walmart.txt', 'r') as reader:
            itemlist = reader.read().splitlines()


        embedVar = discord.Embed(title="Walmart Products", description=itemlist, color=16765905)

        await message.channel.send(embed=embedVar)


client.run(token)
