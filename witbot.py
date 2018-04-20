from wit import Wit 
from flask import Flask, request
import requests 
from pymessenger import Bot
import os, sys

"""
# ---- CRYPTO BOT ---- # 
Messenger Bot built using Wit.ai 
Returning Cryptocurrency Data & News
"""

# Initialise Flask app 

app = Flask(__name__)

# ---- WIT.AI TOKENS ----- #

# Configure Wit.ai settings, connecting to the NLP classifications trained on Wit.ai.

app_id = '5ad9cab5-b710-4547-ac23-14ae6efb5f97'
server_token = 'W6NZYMAP4HWK4JCSNFNDYBTPPHZTXN4R'
client_token = 'AAKHWPFLLHTCCP2B4HZ72WD3X6LTUYPV'

client = Wit(client_token)

# ---- PAGE ACCESS TOKEN + MESSENGER API ---- # 

# Configure Messenger API settings using the Facebook SDK. 

PAGE_ACCESS_TOKEN = 'EAAV9fLL4UwcBABAJnSeRlXiVqcZC4dimGOziPWH1w4Ecj2jkNeNIWubbpLgbL5YBhfJFKJoDjDZCetBwJU2LsdJOoLJ9aqIRBHQtJ4TcM93ToHPde6C2v3zHeD26FUSBZBrsf9P7PUMwJCEgKceWAdgZB8ZAkuErUIZC5SIX2SiAZDZD'
bot = Bot(PAGE_ACCESS_TOKEN)

# ---- FLASK WEB HOOKS ---- # 

@app.route('/', methods=['GET'])
def verify():
	""" 
	Webhook verification
	"""
	if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
		if not request.args.get("hub.verify_token") == "hello":
			return "Verification Token Mismatch", 403
		return request.args["hub.challenge"], 200
	return "Hello World", 200

@app.route('/', methods=['POST'])
def webhook():
	"""
	Interface to the Messenger bot. 
	"""
	data = request.get_json()
	print(data)
	log(data)
	if data['object'] == 'page':
		messages = data['entry'][0]['messaging']
		if messages:
			message = messages[0]
			sender_id = message['sender']['id']
			recipient_id = message['recipient']['id']
			if 'text' in message['message']:
				msg = message['message']['text']
			elif 'text' not in message['message']:
				msg = 'no message'
			response = client.message(msg=msg, context={'session_id': sender_id})
			send = helper_response(response)
			bot.send_text_message(sender_id, send)
	else: 
		"Received another event"
	return "OK", 200

def log(message):
	"""
	Prints out the message.
	"""
	print(message)
	sys.stdout.flush()


def entity_val(entities, entity):
	""" 
	Searches for and returns the entities within the message. 
	Takes the wit.ai response and tries to find the entities associated with it
	+ the intent.

	Example Client Response from Wit.Ai:
	{'_text': "what's the price of btc", 
	'entities': {'cryptoasset': 
					[{'confidence': 1, 
					'value': 'Bitcoin', 
					'type': 'value'}], 
				'intent': 
					[{'confidence': 0.99314743230657, 
					'value': 'get_price'}]}, 
					'msg_id': '0vRhDxN0fiaNSM8Gb'}
	"""
	if entity not in entities:
		return None
	val = entities[entity][0]['value']
	if not val:
		return None
	return val 

def intent_val(entities, intent):
	""" 
	Returns the intent of the message.
	"""
	if 'intent' not in entities:
		return None
	else:
		val = entities['intent'][0]['value']
		if val == 'get_price':
			return val
		elif val == 'get_marketcondition':
			return val
	return val 

def helper_response(response):
	"""
	This helper response defines the client response.
	"""
	entities = response['entities']
	get_price = intent_val(entities, 'get_price')
	get_marketcondition = intent_val(entities, 'get_marketcondition')
	cryptoasset = entity_val(entities, 'cryptoasset')
	greetings = entity_val(entities, 'greetings')
	if get_price and cryptoasset:
		# We can make some assumptions -- if the 'intent' is to get price and 
		# the user cites a cryptocurrency, we can assume that the user is asking
		# for its price. 
			return getprices(cryptoasset)
	if get_marketcondition:
		return getmarketcondition()
	if greetings: 
		return ("Hey, how can I help you?")
	else: 
		return ('I am not sure how to help you, try again!')

def getprices(currency):
	"""
	Returns the price for a particular cryptoasset.
	"""
	request = requests.get('https://api.coinmarketcap.com/v1/ticker/{}/'.format(currency))
	prices = request.json()
	return 'Here is the current price for {0}: {1}'.format(currency, prices[0]['price_usd'])

def getmarketcondition():
	"""
	Returns the current market condition.
	"""
	request = requests.get('https://api.coinmarketcap.com/v1/global/')
	condition = request.json()
	marketcap = condition['total_market_cap_usd']
	totalvolume = condition['total_24h_volume_usd']
	return 'The market cap is now {0}, and the volume for past 24 hours is {1}'.format(marketcap, totalvolume)

if __name__ == '__main__':
	app.run(debug=True)