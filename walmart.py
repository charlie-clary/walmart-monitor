from discord_webhook import DiscordWebhook, DiscordEmbed
import time
from threading import Thread
import proxyhandler
import requests

headers = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
}

# INSERT HOOK
hook = ""

stocklist = []

with open('walmart.txt', 'r') as reader:
    itemlist = reader.read().splitlines()
reader.close()


def appender(pid):
    itemlist.append(pid)


def get_loaded_prods(pid):
    stock = checkstock(pid)
    stocklist.append(stock)
    print("loaded", pid, stock)


def update_stock(index, stock):
    stocklist[index] = stock


def checkstock(pid):
    global product_json
    s = requests.session()

    headers = {
        'Host': 'www.walmart.com',
        'content-type': 'application/json',
        'accept': '*/*',
        'wm_site_mode': '0',
        'accept-language': 'en-ca',
        'itemid': pid,
        'user-agent': 'Walmart/2005202133 CFNetwork/1126 Darwin/19.5.0',
    }

    data = {
        "variables": {
            "postalAddress": {
                "addressType": "RESIDENTIAL",
                "postalCode": "60201",
                "countryCode": "USA",
                "stateOrProvinceCode": "US",
                "zipLocated": False
            },
            "selected": False,
            "productId": pid
        }
    }

    url_info = 'https://www.walmart.com/terra-firma/graphql?options=timing,nonnull,context&v=2&id=FullProductRoute-ios'

    product_json = s.post(url_info, headers=headers, json=data)
    product_json = product_json.json()

    stock = product_json['data']['productByProductId']['offerList'][0]['productAvailability']['availabilityStatus']
    if stock != "OUT_OF_STOCK":
        return True
    return False


def monitor(pid):
    try:

        index = itemlist.index(pid)

        if index >= len(stocklist):
            get_loaded_prods(pid)

        proxies = proxyhandler.proxy()

        stock = checkstock(pid)

        print(pid, 'checking', stock)

        if stocklist[index] != stock:
            print(pid, "stock change, updating stock")
            update_stock(index, stock)

            if stock:
                print(pid, "has restocked")
                iteminfo = get_item_info(pid)
                title = iteminfo[0]
                price = iteminfo[1]
                img = iteminfo[2]
                post_to_discord(pid, title, price, img)


    except Exception as e:
        print(pid, "error checking stock")
        print(e)
        time.sleep(30)


def get_item_info(pid):
    # INSERT INFO
    iteminfo = []
    try:
        title = product_json['data']['productByProductId']['productAttributes']['productName']
    except:
        title = "Default Title"
    try:
        price = product_json['data']['productByProductId']['offerList'][0]['pricesInfo']['prices']['current']['price']
    except:
        price = "Default Price"

    try:
        img = product_json['data']['productByProductId']['imageList'][0]['imageAssetSizeUrls']['default']
    except:
        img = "https://images-na.ssl-images-amazon.com/images/I/61DJRLNgyWL._AC_SL1500_.jpg"

    iteminfo.append(title)
    iteminfo.append(price)
    iteminfo.append(img)
    return iteminfo


def post_to_discord(pid, title, price, img):
    # UPDATE WEBHOOK
    try:
        webhook = DiscordWebhook(
            url=hook)
        embed = DiscordEmbed(color=16765905, title=title)
        embed.set_footer(text='chuckerz walmart',
                         icon_url='https://cdn.discordapp.com/attachments/698993102697791581/780852023302029342/chuckerz_logo.png')
        embed.set_thumbnail(
            url=img)
        embed.set_timestamp()
        embed.add_embed_field(name='Link',
                              value='[URL]({0})'.format("https://www.walmart.com/ip/chuckerz/{0}".format(pid)),
                              inline=True)

        embed.add_embed_field(name='Price',
                              value=str(price), inline=True)

        webhook.add_embed(embed)
        webhook.execute()
        print("Posted to discord", pid)

    except Exception as e:
        print(pid, "error posting to discord")
        print(e)


def stripBlank():
    with open('walmart.txt', 'r') as reader:
        templist = reader.read().splitlines()

    new_file = open("walmart.txt", "w")
    for item in templist:
        if len(item.strip()) != 0:
            new_file.write(item + '\n')


def updateStockList(newlist):
    stocklist.clear()
    for item in newlist:
        get_loaded_prods(item)


for item in itemlist:
    get_loaded_prods(item)

while True:
    stripBlank()
    with open('walmart.txt', 'r') as reader:
        newlist = reader.read().splitlines()
    reader.close()
    if newlist != itemlist:
        print("CHANGE TO ITEMS: UPDATING")
        updateStockList(newlist)
    else:
        for item in itemlist:
            frontend = Thread(target=monitor, args=(item,))
            frontend.start()

    itemlist = newlist

    time.sleep(5)
