from threading import *
import logging

from api_vault import decode_deck, get_card_data, get_match_history, get_match
import cache

class User:
	
	def __init__(self, username, puuid, matches, decks):

		self.username = username
		self.puuid = puuid
		self.deck_codes = decks
		self.matches = []
		self.decks = []
		for m in matches:
			match = get_match(m)
			self.matches.append(match)		
		for d in decks:
			t1 = Thread(target=self.deck_worker, args=[d,self.matches])
			t1.start()


	def new_match(self):
		match = get_match(get_match_history(self.puuid)[0])
		if match in self.matches:
			print('Match Exists')
			return False
		self.matches.append(match)
		deck_code = match['info']['players'][match['index']]['deck_code']
		for deck in self.decks:
			if deck.deck_code == deck_code:
				deck.append_match(self.puuid,match)
				return True
		self.decks.append(Deck(deck_code))
		return True

	def deck_worker(self,deck_code,matches):
		deck = Deck(deck_code)
		for match in matches:
			print(match['info']['players'][match['index']]['deck_code'])
			print(deck.deck_code)
			if match['info']['players'][match['index']]['deck_code'] == deck.deck_code:
				deck.append_match(match)
		self.decks.append(deck)


class Deck:

	def __init__(self,deck_code):

		self.deck_code = deck_code
		self.cards = get_card_data(decode_deck(deck_code))
		self.matches = []

	def append_match(self,match):
		self.matches.append(match)

	def get_record(self):
		record = []
		for match in self.matches:
			record.append({match['metadata']['match_id']: {'game_mode': match['info']['game_mode'], 'game_type': match['info']['game_type'], 'outcome': match['info']['players'][match['index']]['game_outcome']}})
		return record

logging.basicConfig(format='%(asctime)s %(levelname)-4s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename='data\\logs\\treasure.log', filemode='w', level=logging.INFO)
logging.info('Session logging started')
cache = cache.read()
user = User(cache.username, cache.puuid, cache.matches, cache.decks)
print(user.__dict__)
user.new_match()