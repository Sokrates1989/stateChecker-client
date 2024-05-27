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

class StateCheckerClient(Thread):

	def __init__(self, multiple_tools_tool_identifier = 0):
		Thread.__init__(self)
		self.daemon = True
		self._running = True
		self._multiple_tools_tool_identifier = multiple_tools_tool_identifier
		self._sentApiIsDownMessage = False

		# Config file.
		self._is_config_available = True
		try:
			self._config_file_pathAndName = os.path.join(os.path.dirname(__file__), "config.txt")
			self._config_file = open(self._config_file_pathAndName)
			self._config_array = json.load(self._config_file)
		except Exception:
			self._is_config_available = False

		# Initialize telegram specific values.
		if self._is_config_available:
			self._botToken = os.getenv("STATECHECKER_TELEGRAM_BOT_TOKEN") or self._config_array["telegram"]["botToken"]
			self._bot = telebot.TeleBot(self._botToken, parse_mode="HTML")
			self._errorChatID = os.getenv("STATECHECKER_TELEGRAM_ERROR_CHAT_ID") or self._config_array["telegram"]["errorChatID"]
			self._infoChatID = os.getenv("STATECHECKER_TELEGRAM_INFO_CHAT_ID") or self._config_array["telegram"]["infoChatID"]
		else:
			self._botToken = os.getenv("STATECHECKER_TELEGRAM_BOT_TOKEN")
			self._bot = telebot.TeleBot(self._botToken, parse_mode="HTML")
			self._errorChatID = os.getenv("STATECHECKER_TELEGRAM_ERROR_CHAT_ID")
			self._infoChatID = os.getenv("STATECHECKER_TELEGRAM_INFO_CHAT_ID")

		# Initialize Server connection.
		if self._is_config_available:
			self._server_state_check_url = os.getenv("STATECHECKER_SERVER_STATE_CHECK_URL") or self._config_array["server"]["stateCheckUrl"]
			self._server_backup_check_url = os.getenv("STATECHECKER_SERVER_BACKUP_CHECK_URL") or self._config_array["server"]["backupcheckUrl"]
			self._url = self._server_state_check_url
		else:
			self._server_state_check_url = os.getenv("STATECHECKER_SERVER_STATE_CHECK_URL")
			self._server_backup_check_url = os.getenv("STATECHECKER_SERVER_BACKUP_CHECK_URL")
			self._url = self._server_state_check_url

		# Are there multiple environemnt var tools to check?
		self._are_there_multiple_environment_tools_to_check = False
		if os.getenv("STATECHECKER_TOOL_NAME_1"):
				self._are_there_multiple_environment_tools_to_check = True

		# Get the environment var name for the indicated tool to check.
		is_first_tool = True
		if self._are_there_multiple_environment_tools_to_check:
			if self._multiple_tools_tool_identifier > 0:
				is_first_tool = False
				ENV_VAR_IS_BACKUP_FILE_CHECK = f"STATECHECKER_IS_BACKUP_FILE_CHECK_{self._multiple_tools_tool_identifier}"
				ENV_VAR_TOOL_NAME = f"STATECHECKER_TOOL_NAME_{self._multiple_tools_tool_identifier}"
				ENV_VAR_TOOL_DESCRIPTION = f"STATECHECKER_TOOL_DESCRIPTION_{self._multiple_tools_tool_identifier}"
				ENV_VAR_TOOL_TOKEN = f"STATECHECKER_TOOL_TOKEN_{self._multiple_tools_tool_identifier}"
				ENV_VAR_TOOL_FREQUENCY_IN_MINUTES = f"STATECHECKER_TOOL_FREQUENCY_IN_MINUTES_{self._multiple_tools_tool_identifier}"
		if is_first_tool:
			ENV_VAR_IS_BACKUP_FILE_CHECK = "STATECHECKER_IS_BACKUP_FILE_CHECK"
			ENV_VAR_TOOL_NAME = "STATECHECKER_TOOL_NAME"
			ENV_VAR_TOOL_DESCRIPTION = "STATECHECKER_TOOL_DESCRIPTION"
			ENV_VAR_TOOL_TOKEN = "STATECHECKER_TOOL_TOKEN"
			ENV_VAR_TOOL_FREQUENCY_IN_MINUTES = "STATECHECKER_TOOL_FREQUENCY_IN_MINUTES"

		# Get settings of environment vars.
		tool_is_set_from_env = False
		if os.getenv(ENV_VAR_IS_BACKUP_FILE_CHECK) and os.getenv(ENV_VAR_TOOL_NAME) and os.getenv(ENV_VAR_TOOL_DESCRIPTION) and os.getenv(ENV_VAR_TOOL_TOKEN) and os.getenv(ENV_VAR_TOOL_FREQUENCY_IN_MINUTES):
			tool_is_set_from_env = True
			self._is_backup_file_check = str(os.getenv(ENV_VAR_IS_BACKUP_FILE_CHECK)).lower() == "true"
			self._tool_name = str(os.getenv(ENV_VAR_TOOL_NAME))
			self._tool_description = str(os.getenv(ENV_VAR_TOOL_DESCRIPTION))
			self._tool_token = str(os.getenv(ENV_VAR_TOOL_TOKEN))
			self._tool_check_frequency_in_minutes = int(os.getenv(ENV_VAR_TOOL_FREQUENCY_IN_MINUTES))


		# If tool could not be set from env vars use config.
		if not tool_is_set_from_env:

			# Are there multiple config tools to check?
			self._are_there_multiple_config_tools_to_check = False
			if self._is_config_available:
				if isinstance(self._config_array["toolsToCheck"], collections.abc.Sequence):
					self._are_there_multiple_config_tools_to_check = True

			# Get settings of config.
			self._is_backup_file_check = False
			self._tool_name = "Unknown"
			self._tool_description = "Unknown"
			self._tool_token = "Unknown"
			self._tool_check_frequency_in_minutes = "Unknown"
			if self._is_config_available:
				if self._are_there_multiple_config_tools_to_check:
					# Set values for multiple tools config.
					if "isBackupFileCheck" in self._config_array["toolsToCheck"][self._multiple_tools_tool_identifier]:
						if str(self._config_array["toolsToCheck"][self._multiple_tools_tool_identifier]["isBackupFileCheck"]).lower() == "true":
							self._is_backup_file_check = True
					self._tool_name = self._config_array["toolsToCheck"][self._multiple_tools_tool_identifier]["name"]
					self._tool_description = self._config_array["toolsToCheck"][self._multiple_tools_tool_identifier]["description"]
					self._tool_token = self._config_array["toolsToCheck"][self._multiple_tools_tool_identifier]["token"]
					self._tool_check_frequency_in_minutes = int(self._config_array["toolsToCheck"][self._multiple_tools_tool_identifier]["stateCheckFrequency_inMinutes"])
				else:
					# Set values for single tool config.
					if "isBackupFileCheck" in self._config_array["toolsToCheck"]:
						if str(self._config_array["toolsToCheck"]["isBackupFileCheck"]).lower() == "true":
							self._is_backup_file_check = True
					self._tool_name = self._config_array["toolsToCheck"]["name"]
					self._tool_description = self._config_array["toolsToCheck"]["description"]
					self._tool_token = self._config_array["toolsToCheck"]["token"]
					self._tool_check_frequency_in_minutes = self._config_array["toolsToCheck"]["stateCheckFrequency_inMinutes"]

		# Adjustments for backup file check.
		if self._is_backup_file_check:
			self._url = self._server_backup_check_url
			self._running = False

		# Create body for post api call.
		self._postContent = {
			"name": self._tool_name,
			"description": self._tool_description,
			"token": self._tool_token,
			"stateCheckFrequency_inMinutes": self._tool_check_frequency_in_minutes
		}

		# How often to contact api in seconds.
		if self._tool_check_frequency_in_minutes < 1:
			self._tool_check_frequency_in_minutes = 1
		self._contactApiEveryXSeconds = self._tool_check_frequency_in_minutes * 60



	def run(self):
		while self._running:
			self.pingApi()
			time.sleep(self._contactApiEveryXSeconds)

	def stop(self):
		self._running = False


	def pingApi(self):
		response = requests.post(self._url, json = self._postContent)
		# Did contacting the API work?
		if response.status_code == 200:
			self._sendApiIsUpAgainMessage()
		else:
			self._sendApiIsDownMessage(response)


	def indicate_tool_is_up_once(self):
		self._running = False
		self.pingApi()



	def _sendApiIsDownMessage(self, response):
		if self._sentApiIsDownMessage == False:
			# Send Api is down message.
			msg = "API is <b>DOWN!</b>\n\n"
			msg += "Tool <b>" + self._tool_name + "</b> cannot contact api at " + self._url
			msg += "\n" + str(response.status_code) + " " + str(response.reason)
			self._bot.send_message(self._errorChatID, msg)
			self._sentApiIsDownMessage = True


	def _sendApiIsUpAgainMessage(self):
		if self._sentApiIsDownMessage == True:
			# Send Api is up again message.
			msg = "API is <b>UP AGAIN!</b>\n\n"
			msg += "Tool <b>" + self._tool_name + "</b> can contact api again at " + self._url
			self._bot.send_message(self._errorChatID, msg)
			self._sentApiIsDownMessage = False



	def updateBackupFile(self, backupFileHash, backupFileCreationTimestamp):

		self._postContent = {
			"name": self._tool_name,
			"description": self._tool_description,
			"token": self._tool_token,
			"stateCheckFrequency_inMinutes": self._tool_check_frequency_in_minutes,
			"mostRecentBackupFile_creationDate": str(backupFileCreationTimestamp),
			"mostRecentBackupFile_hash": str(backupFileHash)
		}

		response = requests.post(self._url, json = self._postContent)
		
		# Did contacting the API work?
		if response.status_code == 200:
			self._sendApiIsUpAgainMessage()
		else:
			self._sendApiIsDownMessage(response)


	def _sendNoBackupFileMessage(self):
		# Send Api is down message.
		msg = "There is no backup file\n\n"
		msg += "Tool <b>" + self._tool_name + "</b> could not find any backup file"
		self._bot.send_message(self._errorChatID, msg)