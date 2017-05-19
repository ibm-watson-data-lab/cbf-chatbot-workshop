import threading
import time
from slackclient import SlackClient

class SlackBotController(threading.Thread):


	def __init__(self, health_bot, slack_token):
		threading.Thread.__init__(self)
		self.health_bot = health_bot
		self.slack_client = SlackClient(slack_token)
		self.running = False

	def run(self):
		self.running = True
		if self.slack_client.rtm_connect():
			print("Slackbot running.")
			while self.running:
				slack_output = self.slack_client.rtm_read()
				message, message_sender, channel = self.parse_slack_output(slack_output)
				if message and channel and channel[0] == 'D':
					reply = self.health_bot.process_message(message_sender, message)
					self.post_to_slack(reply['text'], channel)
				time.sleep(0.1)
		else:
			print("Connection failed. Invalid Slack token?")
	
	def stop(self):
		self.running = False
    
	def parse_slack_output(self, slack_rtm_output):
		output_list = slack_rtm_output
		if output_list and len(output_list) > 0:
			for output in output_list:
				if output and 'text' in output and 'user_profile' not in output and 'bot_id' not in output:
					return output['text'].lower(), output['user'], output['channel']
		return None, None, None

	def post_to_slack(self, response, channel):
		self.slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)