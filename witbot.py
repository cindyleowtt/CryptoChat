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
	log(data)
	if data['object'] == 'page':
		for entry in data['entry']:
			for event in entry['messaging']:
				sender_id = event['sender']['id']
				recipient_id = event['recipient']['id']
				if event.get('message'):
					if 'text' in event['message']:
						text = event['message']['text']
					else:
						text = 'No Text'
					response = None
					entity, value = wit_response(text)
					if entity == 'cryptoasset': 
						response = 'hey, the price of {0} today is USD {1}'.format(value, get_prices(value))
					if response == None: 
						response = "Sorry, can you try again?"
					bot.send_text_message(recipient_id, response)
	return "OK", 200

def log(message):
	print(message)
	sys.stdout.flush()

def get_entities(message):
	"""
	Takes the wit.ai response and tries to find the entities associated with it
	+ the intent.
	"""
	resp = client.message(message)

def helper_response(message, entities, value):
	entities = response['entities']
	greetings = wit_response(message)[0]


def wit_response(message):
	resp = client.message(message)
	entity = list(resp['entities'])[0]
	value = resp['entities'][entity][0]['value']
	return entity, value

def get_prices(currency):
	"""
	Returns the current price for a particular cryptoasset.
	Retrieves from coinmarketcap.com's public API. 
	"""
	try:
		request = requests.get('https://api.coinmarketcap.com/v1/ticker/{}/'.format(currency))
		prices = request.json()
		price = prices[0]['price_usd']
	except KeyError: 
		return 'Sorry, what currency is that?'
	return price

def get_time_change(currency, time):
	"""
	Returns the change in price. 
	"""
	pass

def get_marketstate():
	pass

if __name__ == '__main__':
	app.run(debug=True)

