"""
This version runs locally using Wit, without a Messenger dependency.
""" 

from wit import Wit 
import requests

app_id = '5ad9cab5-b710-4547-ac23-14ae6efb5f97'
server_token = 'W6NZYMAP4HWK4JCSNFNDYBTPPHZTXN4R'
client_token = 'AAKHWPFLLHTCCP2B4HZ72WD3X6LTUYPV'

client = Wit(client_token)

def entity_val(entities, entity):
	""" 
	Searches for and returns the entities within the message. 
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
		return None # No intents
	else:
		val = entities['intent'][0]['value']
		if val == 'get_price':
			return val
		elif val == 'get_marketcondition':
			return val
	return val 

def helper_response(message):
	"""
	This helper response defines the class for 
	"""
	response = client.message(message)
	entities = response['entities']
	get_price = intent_val(entities, 'get_price')
	print(get_price)
	get_marketcondition = intent_val(entities, 'get_marketcondition')
	cryptoasset = entity_val(entities, 'cryptoasset')
	greetings = entity_val(entities, 'greetings')
	if get_price and cryptoasset:
		# We can make some assumptions -- if the 'intent' is to get price and 
		# the user cites a cryptocurrency, we can assume that the user is asking
		# for its price. 
			return get_prices(cryptoasset)
	elif get_marketcondition:
		return getmarketcondition()
	else: 
		return ('I am not sure how to help you, try again!')

def get_prices(currency):
	"""
	Returns the price for a particular cryptoasset.
	"""
	request = requests.get('https://api.coinmarketcap.com/v1/ticker/{}/'.format(currency))
	prices = request.json()
	return 'Here is the current price for {0}: {1}'.format(currency, prices[0]['price_usd'])

def getmarketcondition():
	request = requests.get('https://api.coinmarketcap.com/v1/global/')
	condition = request.json()
	marketcap = condition['total_market_cap_usd']
	totalvolume = condition['total_24h_volume_usd']
	return 'The market cap is now {0}, and the volume for past 24 hours is {1}'.format(marketcap, totalvolume)

# ---- TEST CASES ----  
msg = 'Hello, how are the prices of BTC'
msg2 = 'Hey!'
msg3 = 'How are the markets looking'

print(client.message(msg))
print(helper_response(msg))
print(helper_response(msg3))

