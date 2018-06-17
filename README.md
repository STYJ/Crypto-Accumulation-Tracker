# Exchange-Bot
### Exchange Bot for cryptocurrencies

Library: [Python-Telegram-Bot](https://github.com/python-telegram-bot/python-telegram-bot)

Goals: 
1. Given a coin ticker, to determine the exchanges where you can buy the coin from.
2. Given a coin ticker, to determine the cheapest exchange and its corresponding trading pair.
3. Given an exchange name, to determine the volume of a given exchange and its top 10 trading pairs.

#### Instructions:

1. Update the token.txt file with the Bot API.
2. Replace the location in line 20 of ExchangeBot.py with the location of your token.txt file.
3. Run Python3 ExchangeBot.py (Make sure you have Requests and BeautifulSoup installed)
4. Once the program is running, it will automatically run the updateDB command which will update the internal database (dictionary) using CoinMarketCap. 
5. To determine the exchanges available and the cumulative 24 hour rolling trade volume for a given ticker, run the c command followed by a ticker.
6. To determine the cheapest exchange and its corresponding trading pair for a given ticker, run the min command followed by a ticker
6. To determine the 24 hour rolling trade volume of a given exchange, its rank and the top 10 trading pairs, run the e command followed by the name of the exchange.

#### Notes:
- There is a caching functionality included in the bot to help optimize retrieval speeds. 
- The time threshold is set to 1 minute before the bot updates the cache for the specified coin / exchange.
- There is also an automatic update of the DB every 6 hours however you may choose to manually update the DB with the updateDB command.
- If CMC decides to change their code / UI, my bot WILL break. Do notify me at @itsmest if it happens and I'll try to fix it ASAP. 

#### Issues to be fixed
- [X] Determine how to handle coins with the same ticker. Soln: Pick the first coin with that ticker.

#### Upcoming Features
- [X] Update description to my commands when typing /command in Telegram
- [X] Sorting exchanges by volume and what the trade volume is for that exchange
- [X] Cheapest exchange to buy a given coin (from the top 10 most liquid exchange for the given coin) (requested by a user feedback)
- [X] 24 hour rolling trade volume, its rank and the top 10 trading pairs of a given exchange (requested by a friend)
- [ ] Determining the difference between the coins listed on 2 exchanges

#### Additional Functionality 
- [ ] Accumulation Tracker (Progress halted indefinitely for now)
