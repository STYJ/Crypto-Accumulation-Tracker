# Exchange-Bot
### Exchange Bot for cryptocurrencies

Library: [Python-Telegram-Bot](https://github.com/python-telegram-bot/python-telegram-bot)

Goal: To determine which exchange you can buy a coin from.

#### Instructions:

1. Update the token.txt file with the Bot API.
2. Replace the location in line 20 of ExchangeBot.py with the location of your token.txt file.
3. Run Python3 ExchangeBot.py (Make sure you have Requests and BeautifulSoup installed)
4. Once the program is running, it will automatically run the updateDB command which will update the internal database (dictionary) using CoinMarketCap. 
5. To determine the exchanges available and the cumulative rolling 24 hour trade volume of a given ticker, run the exchange command followed by a ticker. 

#### Notes:
- There is a caching functionality included in the bot to help optimize retrieval speeds. 
- The time threshold is set to 1 minute before the bot updates the cache for the specified coin.
- There is also an automatic update of the DB every 6 hours however you may choose to manually update the DB with the updateDB command.
- If CMC decides to change their code / UI, my bot WILL break. Do notify me at @itsmest if it happens and I'll try to fix it ASAP. 

#### Issues to be fixed
- [X] Determine how to handle coins with the same ticker. Soln: Pick the first coin with that ticker.

#### Upcoming Features
- [X] Add description to my commands when typing /command in Telegram
- [X] Sorting exchanges by volume and what the trade volume is for that exchange
- [ ] Determining the difference between the coins listed on 2 exchanges

#### Additional Functionality 
- [ ] Accumulation Tracker (Progress halted indefinitely for now)
