## Client that sends status messages to statechecker server.
## Use object.start() to begin.

# Make this client work on its own Thread.
from threading import Thread
# To make Thread sleep.
import time
# For making POST / GET requests.
import requests
# For file operations with operating system.
import os
# For getting config.
import json
# For detecting, if config is array.
import collections.abc
# Api for sending telgram bot messages.
import telebot

config_file_pathAndName = os.path.join(os.path.dirname(__file__), "config.txt")
config_file = open(config_file_pathAndName)
config_array = json.load(config_file)

# Initialize bots.
botToken = config_array["telegram"]["botToken"]
bot = telebot.TeleBot(botToken, parse_mode="HTML")
errorChatID = config_array["telegram"]["errorChatID"]
infoChatID = config_array["telegram"]["infoChatID"]

class StateCheckerClient(Thread):

	def __init__(self, multipleConfigArrayIdentifier = 0):
		Thread.__init__(self)
		self.daemon = True
		self.running = True
		self.sentApiIsDownMessage = False
		self.url = "https://statechecker.felicitas-wisdom.com/v1/statecheck"

		# Does config support multiple instantiations?
		if isinstance(config_array["toolsToCheck"], collections.abc.Sequence):
			self.postContent = {
				"name": config_array["toolsToCheck"][multipleConfigArrayIdentifier]["name"],
				"description": config_array["toolsToCheck"][multipleConfigArrayIdentifier]["description"],
				"token": config_array["toolsToCheck"][multipleConfigArrayIdentifier]["token"],
				"stateCheckFrequency_inMinutes": config_array["toolsToCheck"][multipleConfigArrayIdentifier]["stateCheckFrequency_inMinutes"]
			}
			self.name = config_array["toolsToCheck"][multipleConfigArrayIdentifier]["name"]
			# Ensure state is sent often enough and amount minutes is positive.
			contactApiEveryXMinutes = int(config_array["toolsToCheck"][multipleConfigArrayIdentifier]["stateCheckFrequency_inMinutes"]) - 1
			if contactApiEveryXMinutes < 1:
				contactApiEveryXMinutes = 1
			self.contactApiEveryXSeconds = contactApiEveryXMinutes * 60
		else:
			self.postContent = {
				"name": config_array["toolsToCheck"]["name"],
				"description": config_array["toolsToCheck"]["description"],
				"token": config_array["toolsToCheck"]["token"],
				"stateCheckFrequency_inMinutes": config_array["toolsToCheck"]["stateCheckFrequency_inMinutes"]
			}
			self.name = config_array["toolsToCheck"]["name"]
			# Ensure state is sent often enough and amount minutes is positive.
			contactApiEveryXMinutes = int(config_array["toolsToCheck"]["stateCheckFrequency_inMinutes"]) - 1
			if contactApiEveryXMinutes < 1:
				contactApiEveryXMinutes = 1
			self.contactApiEveryXSeconds = contactApiEveryXMinutes * 60


	def run(self):
		while self.running:
			self.pingApi()
			time.sleep(self.contactApiEveryXSeconds)

	def stop(self):
		self.running = False


	def pingApi(self):
		x = requests.post(self.url, json = self.postContent)
		# Did contacting the API work?
		if x.status_code == 200:
			self.sendApiIsUpAgainMessage()
		else:
			self.sendApiIsDownMessage()


	def sendApiIsDownMessage(self):
		if self.sentApiIsDownMessage == False:
			# Send Api is down message.
			msg = "API is <b>DOWN!</b>\n\n"
			msg += "Tool <b>" + self.name + "</b> cannot contact api at " + self.url
			bot.send_message(errorChatID, msg)
			self.sentApiIsDownMessage = True


	def sendApiIsUpAgainMessage(self):
		if self.sentApiIsDownMessage == True:
			# Send Api is up again message.
			msg = "API is <b>UP AGAIN!</b>\n\n"
			msg += "Tool <b>" + self.name + "</b> can contact api again at " + self.url
			bot.send_message(errorChatID, msg)
			self.sentApiIsDownMessage = False

