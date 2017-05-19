import json
import time
from slackclient import SlackClient

class WebSocketBotController():


	def __init__(self, health_bot):
		self.health_bot = health_bot
		
	def start(self):
		self.running = True
		print('WebSocketBotServer running')
	
	def stop(self):
		self.running = False
    
	def process_message(self, ws, msg_str):
		if msg_str is None:
			return
		msg = json.loads(msg_str)
		if (msg['type'] == 'ping'):
			ws.send(json.dumps({'type': 'ping'}))
		else:
			message_sender = msg['userId']
			message = msg['text']
			reply = self.health_bot.process_message(message_sender, message)
			replyMsg = {
				'type': 'msg',
				'text': reply['text'],
				'watsonData': reply['conversation_response']
			}
			ws.send(json.dumps(replyMsg))