# Import libraries
import telegram
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import functions

# Main code
def main():

	# Initiate logging module
	logging.basicConfig(
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
		level=logging.INFO
	)

	# Retrieve token from external file, enter the location of token.txt
	# Token.txt should only contain 1 line which is the api token of your bot.
	# NEVER EVER USE ABSOLUTE PATHING!!!!
	# Use relative pathing for ease of deployment across different environments.
	f = open('token.txt', 'r')
	tokenId = f.readline()

	# Create bot object and its corresponding updater, dispatcher and job queue
	bot = telegram.Bot(token=tokenId)
	updater = Updater(token=tokenId)
	dispatcher = updater.dispatcher
	jqueue = updater.job_queue

	# Scheduled jobs
	# Automatically updates the coin DB every 6 hours
	job_updateCoinDB = jqueue.run_repeating(functions.autoUpdateDBWrapper,
											interval=21600,
											first =0
											)
	job_updateCoinDB.enabled = True
	
	# Creating command handlers
	updateDB_handler = CommandHandler('updateDB',
									  functions.manualUpdateDBWrapper
									  )
	coin_handler = CommandHandler('e',
								  functions.coinWrapper,
								  pass_args=True
								  )
	cheapest_handler = CommandHandler('m',
									  functions.cheapestWrapper,
									  pass_args=True
									  )
	exchange_handler = CommandHandler('t',
									  functions.exchangeWrapper,
									  pass_args=True
									  )
	start_handler = CommandHandler('start',
								   functions.startWrapper
								   )


	# Adding the handlers to the dispatcher
	dispatcher.add_handler(updateDB_handler)
	dispatcher.add_handler(coin_handler)
	dispatcher.add_handler(cheapest_handler)
	dispatcher.add_handler(exchange_handler)
	dispatcher.add_handler(start_handler)

	# Disabled the following handlers

	# update_handler = CommandHandler('update',
	# 								functions.updateWrapper,
	# 								pass_args=True)
	# updateCache_handler = CommandHandler('updateCache',
	# 									 functions.updateCacheWrapper)
	# unknown_handler = MessageHandler(Filters.command,
	# 								 functions.unknownWrapper)
	# dispatcher.add_handler(update_handler)
	# dispatcher.add_handler(updateCache_handler)
	# dispatcher.add_handler(unknown_handler)

	# WIP functions
	# analyse_handler = CommandHandler('analyse',
	# 								 functions.analyseWrapper,
	# 								 pass_args=True)
	# dispatcher.add_handler(analyse_handler)

	# Start the bot
	print('starting bot!')
	updater.start_polling(clean=True)


if __name__ == "__main__":
	main()
