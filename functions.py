import requests
import datetime
import math
import re
import time
from bs4 import BeautifulSoup
from random import randint

# Initialize a dictionary of coin_ticker tuple pair.
# tuple has the structure (dict of exchange_name coin pair, time_of_update)
# coin has the structure total_vol, [{trading_pair, vol, price, url}]
# sorted by highest cumulative trade volume 
coin_to_exchanges = dict()

# Initialize a coin_database of ticker url path pair. Updated every 6 hours
coin_database = dict()

# Initialize an exchange_to_coin database of exchange_name tuple pair
# tuple has the structure (exchange_rank, exchange_vol, exchange_url, coin,
# time_of_update)
# coin has the structure total_vol, [{coin_rank, coin_name, trading pair, vol, 
# price, url, time of update}]
# top 10 dict is a dict of coin volume pairs
exchange_to_coin = dict()

# Initialize a list of exchanges and the time of update. Updated every 3 hours.
exchange_database = []

# Scrapes CMC's website to retrieve the URL path of coin based on the ticker
# provided. 
def updateCoinDB(coin_database):

    # Might want to include error handling just in case
    print("Updating coin_database...")
    page = requests.get("https://coinmarketcap.com/all/views/all/")
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get tbody
    table = list(soup.find('table', id='currencies-all').children)  
    tbody = list(table[3].children)

    # Get length
    length = len(tbody)

    # Populating coin_database
    i = 1

    while(i < length):
        entry = list(list(tbody[i].children)[3].children)
        ticker = entry[3].get_text()

        try:
            coin_database[ticker]
        except KeyError:
            suffix = entry[7]['href']
            coin_database[ticker] = suffix
        finally:
            i = i + 2
    print("Update complete!")

# Scrapes CMC's website to retrieve all the exchanges that are listed.
def updateExchangeDB(exchange_database):

    # Might want to include error handling just in case
    print("Updating exchange_database...")
    page = requests.get("https://coinmarketcap.com/exchanges/volume/24-hour/" + 
                        "all/")
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get table
    table = list(soup.find('table',
                           class_='table table-condensed border-top').children)

    # Clear exchange_database
    exchange_database.clear()

    # Get updated exchanges
    i = 0

    while(i < len(table)):

        # Only look at rows with a 'tr' tag and an id that is not None
        if table[i].name == 'tr' and table[i].get('id') != None:
            name, rank = getNameAndRank(table[i].get_text().lower())

            # Append to list of exchanges
            exchange_database.append(name)
        i = i + 1
    print("Update complete!")

# Check if coin ticker exists in coin_to_exchanges dictionary
def checkCoin(coin, coin_to_exchanges):

    try:
        coin_to_exchanges[coin]
    except KeyError:
        print(coin + " not found!")
        return False
    else:
        print(coin + " found!")
        return True

# Check if exchange name exists in exchange_to_coin database
def checkExchange(exchange, exchange_to_coin):

    try:
        exchange_to_coin[exchange]
    except KeyError:
        print(exchange + " not found!")
        return False
    else:
        print(exchange + " found!")
        return True

# Get html source code for the given coin ticker
def getSource(type, *args):
    print("In getSource function")

    if type == 'coin':

        # URL for getting coin details
        url = 'https://coinmarketcap.com' + coin_database[args[0]]
    elif type == 'history':

        # Getting the date today and delta
        today = datetime.datetime.now()
        delta = datetime.timedelta(days=int(args[1]))

        # URL for getting historical data
        url = 'https://coinmarketcap.com' + coin_database[args[0]] +\
        'historical-data/?start=' + (today - delta).strftime('%Y%m%d') +\
        '&end=' + today.strftime('%Y%m%d')
    elif type == 'exchange':

        # URL for getting the exchange details
        url = "http://coinmarketcap.com" + args[0]
    else:
        return False
    page = requests.get(url)

    if page.status_code == 404:
        print("Source code not found")
        return False
    else:
        print("Source code found!")
        return BeautifulSoup(page.content, 'html.parser')

# Updates exchanges and volume for the specified coin
def updateCoin(coin, coin_to_exchanges):
    print("In updateCoin function")

    # Get source code
    soup = getSource('coin', coin)

    # Process source code to get unique list of exchanges for coin
    if soup:
        table = list(soup.find('table', id='markets-table').children)
        tbody = list(table[3].children)
        i = 1

        # Parse the entire tbody into a namedtuple array, sorted by total vol
        # descending. Only retain the top 15 exchanges.
        exchanges = dict()

        while(i < len(tbody)):
            data = list(tbody[i].children)

            # Get name of exchange
            exchange_name = list(data[3].children)[1].get_text()

            # Get trading pair
            trading_pair = list(data[5].children)[0].get_text()
            
            # Remove $ and commas for volume and convert to int
            vol = int(re.sub("[^\d\.]",
                             "",
                             list(data[7].children)[1].get_text()))

            # Remove $ and commas for price and convert to float
            price = float(re.sub("[^\d\.]",
                                 "",
                                 list(data[9].children)[1].get_text()))

            # Get trading pair url
            url = list(data[5].children)[0]['href']

            try: 
                exchanges[exchange_name]
            except KeyError:
                exchanges[exchange_name] = Coin(trading_pair,
                                                vol,
                                                price,
                                                url)
            else:
                exchanges[exchange_name].add_new_entry(vol)
                exchanges[exchange_name].add_details('trading_pair',
                                                     trading_pair)
                exchanges[exchange_name].add_details('vol', vol)
                exchanges[exchange_name].add_details('price', price)
                exchanges[exchange_name].add_details('url', url)
            i = i + 2

        # Sort exchange based on total volume
        exchanges = sorted(exchanges.items(),
                           key=lambda detail: detail[1].total_vol,
                           reverse=True)

        # Return only the top 10 exchanges
        if len(exchanges) > 10:
            exchanges = exchanges[:10]
        coin_to_exchanges[coin] = (exchanges, time.time())
        print(coin + " updated!")
    else:
        print("Error updating " + coin + "!")
        return False

# Scrapes CMC's website to retrieve the trading pairs with the highest rolling 
# 24 hour trade volume based on the exchange name provided
def updateExchange(exchange, exchange_to_coin):
    print("In updateExchange function")
    page = requests.get("https://coinmarketcap.com/exchanges/volume/24-hour/" + 
                        "all/")
    soup = BeautifulSoup(page.content, 'html.parser')

    # Process source code to get top traded pairs for exchange
    if soup:
        table = soup.find('table', class_='table table-condensed border-top')
        table = list(table.children)

        # Variables used to help navigate table
        i = 0
        found = False
        start_index = 0
        end_index = 0

        while(i < len(table)):

            # Only look at rows with a 'tr' tag and an id that is not None
            if table[i].name == 'tr' and table[i].get('id') != None:

                # Break after you retrieve the end index
                if(found):
                    end_index = i
                    break;

                ex_name, ex_rank = getNameAndRank(table[i].get_text().lower())

                # Find the index of the exchange
                if(exchange == ex_name and not found):
                    start_index = i
                    found = True
            i = i + 1

        # Removing total section
        if table[end_index - 2].get_text()[:5] == 'Total':
            end_index = end_index - 2

        # Removing view more section
        if table[end_index - 2].get_text() == '\nView More\n':
            end_index = end_index - 2

        # Getting the URL and volume of the exchange
        path = table[start_index].find('a')['href']
        soup = getSource('exchange', path)
        ex_url = list(soup.find('ul', class_='list-unstyled').children)
        ex_url = ex_url[1].find('a')['href']
        ex_vol = soup.find('div', class_="col-sm-8 bottom-margin-1x")
        ex_vol = ex_vol.find(class_="h2").get_text()

        # Getting the trading pairs of the exchange
        coins = dict()
        i = start_index + 4

        while(i < end_index):

            # Getting coin details
            entry = list(table[i].children)
            rank = entry[1].get_text()
            name = entry[3].get_text()
            trading_pair = entry[5].get_text()
            url = entry[5].find('a')['href']
            vol = int(re.sub("[^\d\.]", "", entry[7].get_text()))
            price = float(re.sub("[^\d\.]", "", entry[9].get_text()))

            # Updating coins dict
            try: 
                coins[name]
            except KeyError:
                coins[name] = Coin(trading_pair, vol, price, url)
                coins[name].add_details('rank', rank)
            else:
                coins[name].add_new_entry(vol)
                coins[name].add_details('trading_pair', trading_pair)
                coins[name].add_details('vol', vol)
                coins[name].add_details('price', price)
                coins[name].add_details('url', url)
                coins[name].add_details('rank', rank)
            i = i + 2
        coins = coins.items()
        exchange_to_coin[exchange] = (ex_rank,
                                      ex_vol,
                                      ex_url,
                                      coins,
                                      time.time())
        print(exchange + " updated!")
    else:
        print("Error updating " + coin + "!")
        return False

# Class to represent the trading pair, volume, price and url details
class Coin:

    def add_new_entry(self, vol):
        self.total_vol = self.total_vol + vol
        self.details.append(dict())

    def add_details(self, key, value):
        self.details[-1][key] = value

    def __init__(self, trading_pair, vol, price, url):
        self.total_vol = 0
        self.details = []
        self.add_new_entry(vol)
        self.add_details('trading_pair', trading_pair)
        self.add_details('vol', vol)
        self.add_details('price', price)
        self.add_details('url', url)

    def get_details(self):
        return self.details

# Function to get trading pairs with the highest rolling 24 hr volume
# for the given exchange
def getCoinsWithCache(exchange, exchange_to_coin):

    # Checks if exchange is in the exchange_to_coin cache
    if checkExchange(exchange, exchange_to_coin):
        print("Exchange found in cache")

        # Checks if more than a minute has passed, if so update exchange cache
        if time.time() - exchange_to_coin[exchange][4] > 60:
            print("updating cache for " + exchange)
            updateExchange(exchange, exchange_to_coin)
    else:

        # If cache doesn't contain exchange, add it in
        print("Exchange not found in cache.")
        print("Processing trading pair volume data for " + exchange)
        updateExchange(exchange, exchange_to_coin)
    try:
        return exchange_to_coin[exchange][3]
    except KeyError:
        return False


# Function to get list of exchanges for the given coin
def getExchangeWithCache(coin, coin_to_exchanges):

    # Checks if coin is in the coin_to_exchanges cache
    if checkCoin(coin, coin_to_exchanges):
        print("Coin found in cache")

        # Checks if more than a minute has passed, if so update cache for coin
        if(time.time() - coin_to_exchanges[coin][1] > 60):
            print("Updating cache for " + coin)
            updateCoin(coin, coin_to_exchanges)
    else:
        
        # If the cache doesn't contain coin, add it in.
        print("Coin not found in cache.")
        print("Processing exchange data for " + coin)
        updateCoin(coin, coin_to_exchanges)

    try:
        return coin_to_exchanges[coin][0]
    except KeyError:
        return False

# Function to concatenate a list of exchanges into multiple strings max
# character length of 4096
def concatExchanges(exchanges):
    return '\n'.join(exchanges)

# Function to analyse if a coin is getting pumped
def analyse(*args):
    print("In analyse function")

    # Get source code
    soup = getSource('history', args[0], args[1])

    if not soup:
        body = list(soup.select(
            'div#historical-data table.table')[0].children)[3]
        rows = list(body.children)
        i = len(rows) - 2
        accumulationFactor = 0

        while(i - 2 > 0):

            # 3 = open, 9 = closed, 11 = volume
            row_a = list(rows[i])
            open_a = int(row_a[3].get_text())
            close_a = int(row_a[9].get_text())
            vol_a = int(row_a[11].get_text().replace(',', ''))

            row_b = list(rows[i-2])
            open_b = int(row_b[3].get_text())
            close_b = int(row_b[9].get_text())
            vol_b = int(row_b[11].get_text().replace(',', ''))

            i = i - 2

        while(i < len(rows)):

            row = list(rows[i])
            vol = int(row[11].get_text().replace(',', ''))
            print(vol)
            sum += vol
            i = i + 2

        print("Sum is " + str(sum))

        print(args[1])
    else:
        print("Analysis failed. Please check that you've entered the correct" +
              " parameters.")

# Parse cache to retrieve all the trading pairs for a given exchange
def parseExchange(exchanges):
    results = []
    for i in exchanges:
        for j in i[1].get_details():
            results.append((i[0],
                            j['trading_pair'],
                            j['vol'],
                            j['price'],
                            j['url']))
    return sorted(results[:10], key=lambda x: x[3], reverse=False)

# Parse cache to retrieve all trading pairs for a given coin
def parseCoin(coins):
    results = []
    for i in coins:
        for j in i[1].get_details():
            results.append((i[0],
                            j['trading_pair'],
                            j['vol'],
                            j['price'],
                            j['url'],
                            j['rank']))

    # Return the top 10 traded pairs
    return sorted(results, key=lambda x: x[2], reverse=True)

# Refactored this to clean code up
def getNameAndRank(dirty_text):
    # Get name of exchange in lower case
    # Remove all space or new line
    text = re.sub("[\s]", "", dirty_text)

    # Remove the first dot
    try:
        index = text.index('.')
    except ValueError:
        return False
    else:

        # Get rank and name
        exchange_rank = text[:index]
        try:
            exchange_name = text[index + 1:].lower()
        except IndexError:
            return False

    return exchange_name, exchange_rank

##################################
#   Telegram Wrapper Functions   #
##################################\

# Command to update coin_database and exchange_database manually
def autoUpdateDBWrapper(bot, update):
    print("automatically updating DB")
    updateCoinDB(coin_database)
    updateExchangeDB(exchange_database)

# Command to update coin_database and exchange_database manually
def manualUpdateDBWrapper(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text='Updating coin and exchange databases...')
    updateCoinDB(coin_database)
    exchange_database = updateExchangeDB()
    bot.send_message(chat_id=update.message.chat_id, text='Update complete!')

# Command to find the coins with the highest volume for this exchange
def exchangeWrapper(bot, update, args):
    print()

    if len(args) != 1:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Too few / many arguments! Please enter only 1' +
                         ' exchange name.',
                         reply_to_message_id=update.message.message_id)
    else:

        # Getting the id equivalent (full name delimited with '-') of the
        # target exchange
        exchange = args[0].lower()

        # Checks to see if the name provided is a valid exchange name
        if exchange in exchange_database:

            # If so, then get the trading pairs with the highest rolling 24 hour
            # trade volume
            coins = getCoinsWithCache(exchange, exchange_to_coin)
            exchange_rank = exchange_to_coin[exchange][0]
            exchange_vol = exchange_to_coin[exchange][1]
            exchange_url = exchange_to_coin[exchange][2]
            results = parseCoin(coins)

            list_of_trading_pairs = ["Name: [" + args[0] + "](" + 
                                     exchange_url + ")", "Rank: " + 
                                     exchange_rank, "Volume: " + exchange_vol,
                                     "", "Coin | Trading Pair | Vol | Price"]

            if results:
                print("Printing trading pairs with the highest rolling 24" + \
                " hour trade volume")

                # list_of_exchanges is a list of concatenated exchanges into
                # strings with a maximum length of 4096 characters, see
                # comments in the concatExchange Function as to why this isn't
                # necessary for now.

                for i in results:
                    name = i[0]
                    trading_pair = i[1]
                    vol = '${:,}'.format(i[2])
                    price = '${:,}'.format(i[3])
                    url = i[4]

                    list_of_trading_pairs.append(name + " | " + "[" + 
                                                 trading_pair + "](" + url +
                                                  ") | " + vol + " | " + price)

                bot.send_message(chat_id=update.message.chat_id,
                                 text=concatExchanges(list_of_trading_pairs),
                                 disable_web_page_preview=True,
                                 parse_mode='Markdown',
                                 reply_to_message_id=update.message.message_id)

        else:
            print(args[0] + " not found!")
            bot.send_message(chat_id=update.message.chat_id,
                             text=args[0] + " cannot be found in DB, please" +
                             " check that you've entered a valid exchange" + 
                             " name or run the updateDB command. Note that" +
                             " coinmarketcap is the data source i.e. your" +
                             " name has to be listed on CMC before the bot" +
                             " can pull its data.",
                             reply_to_message_id=update.message.message_id)

# Command to find all exchanges that trades this coin
def coinWrapper(bot, update, args):
    print()

    if len(args) != 1:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Too few / many arguments! Please enter only 1' +
                         ' ticker.',
                         reply_to_message_id=update.message.message_id)
    else:

        # Getting the id equivalent (full name delimited with '-') of the
        # target coin
        coin = args[0].upper()

        try:
            coin_database[coin]
        except KeyError:
            print(args[0] + " not found!")
            bot.send_message(chat_id=update.message.chat_id,
                             text=args[0] + " cannot be found in DB, please" +
                             " check that you've entered a valid ticker or" +
                             " run the updateDB command. Note that" +
                             " coinmarketcap is the data source i.e. your" +
                             " coin has to be listed on CMC before the bot" +
                             " can pull its data.",
                             reply_to_message_id=update.message.message_id)
        else:
            exchanges = getExchangeWithCache(coin, coin_to_exchanges)

            if exchanges:
                print("Printing exchanges...")

                # list_of_exchanges is a list of concatenated exchanges into
                # strings with a maximum length of 4096 characters, see
                # comments in the concatExchange Function as to why this isn't
                # necessary for now.
                list_of_exchanges = ["Exchange | Volume"]

                for exchange in exchanges:
                    name = exchange[0]
                    vol = '${:,}'.format(exchange[1].total_vol)
                    url = exchange[1].get_details()[0]['url']
                    list_of_exchanges.append(
                        "[" + name + "](" + url + ") | " + vol)

                bot.send_message(chat_id=update.message.chat_id,
                                 text=concatExchanges(list_of_exchanges),
                                 disable_web_page_preview=True,
                                 parse_mode='Markdown',
                                 reply_to_message_id=update.message.message_id)
                # for i in list_of_exchanges:
                # bot.send_message(chat_id=update.message.chat_id, text=i,
                # reply_to_message_id=update.message.message_id)

# Find the cheapest trading pair from the top 10 exchanges that trades this coin
def cheapestWrapper(bot, update, args):
    print()

    if len(args) != 1:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Too few / many arguments! Please enter only 1' +
                         ' ticker.',
                         reply_to_message_id=update.message.message_id)
    else:

        # Getting the id equivalent (full name delimited with '-') of the
        # target coin
        coin = args[0].upper()

        try:
            coin_database[coin]
        except KeyError:
            print(args[0] + " not found!")
            bot.send_message(chat_id=update.message.chat_id,
                             text=args[0] + " cannot be found in DB, please" +
                             " check that you've entered a valid ticker or" +
                             " run the updateDB command. Note that" +
                             " coinmarketcap is the data source i.e. your" +
                             " coin has to be listed on CMC before the bot" +
                             " can pull its data.",
                             reply_to_message_id=update.message.message_id)
        else:
            exchanges = getExchangeWithCache(coin, coin_to_exchanges)
            results = parseExchange(exchanges)

            if results:
                print("Printing trading pairs...")

                # list_of_exchanges is a list of concatenated exchanges into
                # strings with a maximum length of 4096 characters, see
                # comments in the concatExchange Function as to why this isn't
                # necessary for now.
                trading_pairs = ["Exchange | Trading Pair | Volume | Price"]

                for i in results:
                    name = i[0]
                    trading_pair = i[1]
                    vol = '${:,}'.format(i[2])
                    price = '${:,}'.format(i[3])
                    url = i[4]

                    trading_pairs.append( 
                        name + " | " + "[" + trading_pair + "](" + url + ") | "
                        + vol + " | " + price)

                bot.send_message(chat_id=update.message.chat_id,
                                 text=concatExchanges(trading_pairs),
                                 disable_web_page_preview=True,
                                 parse_mode='Markdown',
                                 reply_to_message_id=update.message.message_id)

# Command to introduce the bot to the users
def startWrapper(bot, update):

    bot.send_message(chat_id=update.message.chat_id,
                     text="Hi and welcome to the exchange explorer bot! The 3" +
                     " main commands that are supported by this bot are:\n\n" +
                     " 1. /c ticker - To determine the top 10 exchanges that" + 
                     " this coin is traded on and its cumulative 24 hour" +
                     " rolling trade volume.\n2. /min ticker - To determine" + 
                     " the top 10 cheapest trading pairs for this coin from" +
                     " the most liquid exchanges that this coin trades on." + 
                     "\n3. /e exchange_name - To determine the 24" +
                     " hour rolling trade volume and the top traded pairs" +
                     " for the specified exchange.\n\nThis bot is created by" +
                     " @itsmest. If you have any feedback or suggestions," +
                     " feel free to drop me a message!."
                     )

# Command to update list of exchanges that trades this coin
# def updateWrapper(bot, update, args):
#     print()
#     if len(args) != 1:
#         bot.send_message(chat_id=update.message.chat_id,
#                          text='Too few / many arguments! Please enter only 1'+
#                          ' ticker.',
#                          reply_to_message_id=update.message.message_id)
#     else:
#         # Getting the id equivalent (full name delimited with '-') of the
#         # target coin
#         coin = args[0].upper()
#         try:
#             coin_database[coin]

#         except KeyError:
#             print(args[0] + " not found!")
#             bot.send_message(chat_id=update.message.chat_id,
#                              text=args[0] + " cannot be found in DB, please" +
#                              " check that you've entered a valid ticker or" +
#                              " run the updateCoinDB command. Note that" +
#                              " coinmarketcap is the data source i.e. your" +
#                              " coin has to be listed on CMC before the bot" +
#                              " can pull its data.",
#                              reply_to_message_id=update.message.message_id)
#         else:

#             id = coin_database[coin].get('id')

#             print("Updating exchange data for " + coin)
#             print(id)
#             # Not the most efficient but it works.
#             updateCoin(id, coin_to_exchanges)

#             bot.send_message(chat_id=update.message.chat_id,
#                              text="Exchanges and 24h rolling trade volume" +
#                              " for " + args[0] + " are updated!",
#                              reply_to_message_id=update.message.message_id)

# Command to update all coins in cache
# def updateCacheWrapper(bot, update):
#     print("updating cache")
#     for coin in coin_to_exchanges:
#         updateCoin(coin, coin_to_exchanges)

#     print("cached coins updated")

# Command to handle unregistered commands
# def unknownWrapper(bot, update):
#     replies = ["Stop trolling my bot Brian!",
#                "Jon! Do you not understand the meaning of stop?!",
#                "Invalid command...",
#                "Please try again later even though it'll probably still not" +
#                " work lol.",
#                "404 Error: Command not found!"]
#     bot.send_message(chat_id=update.message.chat_id, text=replies[randint(
#         0, 4)], reply_to_message_id=update.message.message_id)

# Command to analyse if a coin is getting pumped
# def analyseWrapper(bot, update, args):
#     print()
#     if len(args) != 2:
#         bot.send_message(chat_id=update.message.chat_id,
#                          text='Too few / many arguments! Please enter 1' +
#                          'ticker followed by number of days e.g. /analyse' +
#                          ' CND 7',
#                          reply_to_message_id=update.message.message_id)
#     else:
#         # Getting the id equivalent (full name delimited with '-') of the
#         # target coin
#         coin = args[0].upper()
#         day = round(float(args[1]))
#         if (coin in coin_database) and day > 0:
#             id = coin_database[coin].get('id')
#             accumulationFactor = analyse(id, day)
#             bot.send_message(chat_id=update.message.chat_id,
#                              text=accumulationFactor,
#                              reply_to_message_id=update.message.message_id)

#         else:
#             print("Invalid parameters or updateCoinDB not run!")
#             bot.send_message(chat_id=update.message.chat_id,
#                              text=args[0] + " cannot be found in DB, please" +
#                              " run the updateCoinDB command or check that you've"+
#                              " entered valid parameters.",
#                              reply_to_message_id=update.message.message_id)
