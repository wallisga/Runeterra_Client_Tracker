from time import sleep
from secrets import token_hex
from api_vault import hb, encode_deck, decode_deck, get_puuid, get_match_history, get_match
from cache import check_cache, read, write, get_username, get_card_info


class App_Memory:
	#NOTE PLEASE READ! The expedition state of viewing a deck or playing a game does not exist so both viewing ladder decks vs expedition decks,
	#or playing ladder games vs expedition games will seem the same.
	#The solution for this will likely involve encoding and decoding deck with a function. Make this clean for performance reasons.

	###############################################################
	###						APP MEMORY 							###
	###############################################################

	'''The role of the App_Memory class is to gather, store, and load the various memory LOR_VAULT has. It is effectively the engine.
	It does this by utilizing the api_vault module to access data from the various REST APIs, loading that data into numpy, 
	displaying the data through the window module as an interfacable GUI, and then storing that data with the cache module. 
	These modules can be in the current working memory of this file and will be store in the LocalApp cache.

	The primary function in App Memory that is looped by __main__ is the state_check function. 
	This function will send a hb to the game client api to access various data. Once a state change is detected in the gathered data,
	the state_change function will determine what type of change occurred.
	Then, the trigger function will determine what action needs to be taken based on the change.

	These actions are notated as notification functions and perform logic to present data to the user or to store newly gathered data in the cache.
	
	NOTIFICATIONS
	1. game_notification:  Game Start -> Decode deck and add to deck collection if it is a new deck.
	2. game_notification:  None -> Nothing happens.
	3. game_notification:  Game End -> Gets last match data and stores it in cache.
	4. expedition_notification:  TBD......


	The __main__ loop continues until the user exits the program.

	FUTURE IMPLEMENTATIONS
	----------------------
	
	#Working on this currently!
	Tkinter GUI module to pull up data for the user to view. This will start with a small window by default on bottom right that has the following:
	1. Current username and a small active display that has tabs to cycle through different content.
	2. Ability to expand up one of the tab windows that includes additional features and display table to list elements out with a hover-text.
		ex) Match History with both player names, deck factions, deck cards, etc.
		ex) Expedition History with previous attempts, match data, most common cards picked, etc.
	3. Ability to view create decks and copy deckid with ease to share with others.'''



	#Initializes the App Memory data from client api and riot api if necessary. Then checks in with local memory in LocalAppData. Reads/writes appropriately.
	def __init__(self):
		#0=Loading; 1=Menu-No Expedition; 2=Menu+Expedition; 3=General game; 4=Expedition game
		self.state = 0			
		self.loading_notification('Initializing...')
		self.change_counter = 0
		self.heartbeat = hb()
		self.game_state = self.heartbeat.card_positions['GameState']
		self.cached_game_state = self.game_state
		self.active_deck = self.heartbeat.active_deck['DeckCode']

		memory_exist = check_cache()

		if memory_exist:
			self.loading_notification('Reading save...')
			memory = read()
			self.username = memory['username']
			self.puuid = memory['puuid']
			self.matches = memory['matches']
			self.decks = memory['decks']
			self.expedition = Expedition(memory['expedition']['data'])
			self.expeditions = [self.expedition]
			self.cached_expedition_data = self.expedition.data
		else:
			self.loading_notification('Writing new save...')
			self.username = get_username()
			self.puuid = get_puuid(self.username)['puuid']
			match_history = get_match_history(self.puuid)
			self.matches = []
			self.decks = []
			self.expedition = Expedition(self.heartbeat.expedition_state)
			self.expeditions = [self.expedition]			
			self.cached_expedition_data = self.expedition.data
			self.loading_notification('Getting match data...')
			for match in match_history:
				data = get_match(match)
				self.matches.append(data)
				for player in data['info']['players']:
					if player['puuid'] == self.puuid and player['deck_code'] not in self.decks:
						self.decks.append((player['deck_code']))
			write({'username': self.username, 'puuid': self.puuid, 'matches': self.matches, 'decks': self.decks, 'expedition': {'id': self.expedition.id, 'data': self.expedition.data, 'deck_code': self.expedition.deck_code}})
		self.loading_notification('Ready!')


	#
	def state_check(self):
		self.heartbeat = hb()
		self.state_calc()
		if self.game_state != self.heartbeat.card_positions['GameState']:
			self.game_state = self.heartbeat.card_positions['GameState']
			self.change_counter += 1

			return self.trigger(self.state_change())			

		if self.expedition.data['State'] != self.heartbeat.expedition_state['State']:		
			self.expedition.update(self.heartbeat.expedition_state)
			self.change_counter += 1
			return self.trigger(self.state_change())
		return self.state


	#Goes through cached_data and finds the keys that were changed as the diff. This is sent to the trigger() function to trigger the appropriate notification type.
	def state_change(self):
		changed = {}
		if self.cached_expedition_data != self.expedition.data:
			exp_diff = {k: self.cached_expedition_data[k] for k in self.cached_expedition_data if k in self.expedition.data and self.cached_expedition_data[k] != self.expedition.data[k]}
			changed['expedition_data'] = exp_diff
			self.cached_expedition_data = self.expedition.data
		elif self.cached_game_state != self.game_state:
			game_diff = {'State': self.cached_game_state}
			changed['game_state'] = game_diff
			self.cached_game_state = self.game_state
		return changed
		
	#	
	def state_calc(self):
		if self.active_deck and self.expedition.deck_code:
			self.state = 4
		elif self.active_deck:
			self.state = 3
		elif self.expedition.deck_code:
			self.state = 2
		else:
			self.state = 1

	#Six state changes found so far
	##### 1. expedition_data['IsActive'] from False to True and vice versa (once an expedition has been loaded into the Game Client or once when expedition has been lost)
	##### 2. expedition_data['State'] from Other to Offscreen and vice versa (going from Expedition menu to General menus and vice versa)
	##### 3. expedition_data['State'] from Other to Picking and vice versa (going from Expedition menu to Picking menu and vice versa)
	##### 4. expedition_data['Record'] and expedition_data['Games'] and expedition_data['Wins'] and expedition_data['Losses'] changes (after an expedition game has been completed)
	##### 5. expedition_data['State'] from Other to Swapping (once an expedition has been lost)
	##### 6. game_state['State'] from Menus to None to InProgress and vice versa (when a game starts and a game ends)
	

	#
	def trigger(self,last_state):		
		print('\nTriggering change #: '+str(self.change_counter)+'\n')
		print(last_state)
		for key in last_state.keys():
			if key == 'expedition_data':
				return self.expedition_notification(last_state[key])
			else:
				return self.game_notification(last_state[key])
	

	#				
	def game_notification(self, states):
		if self.cached_game_state == 'InProgress':
			print('A game has started. Please report to GUI with deck data here.\n')
			self.active_deck = self.heartbeat.active_deck['DeckCode']

		if self.cached_game_state == 'Menus':
			print('A game has ended. Match data will be stored locally.\n')
			data = get_match(get_match_history(self.puuid)[0])
			self.matches.append(data)
			for player in data['info']['players']:
				if player['puuid'] == self.puuid and player['deck_code'] not in self.decks:
					self.decks.append((player['deck_code']))
			write({'username': self.username, 'puuid': self.puuid, 'matches': self.matches, 'decks': self.decks, 'expedition': {'id': self.expedition.id, 'data': self.expedition.data, 'deck_code': self.expedition.deck_code}})			
			self.active_deck = self.heartbeat.active_deck['DeckCode']
		return self.state


	#
	def expedition_notification(self, states):
		if 'IsActive' in states:
			if self.expedition.deck_code:
				self.expedition = Expedition(self.heartbeat.expedition_state)
				self.expeditions.append(self.expedition)
				write({'username': self.username, 'puuid': self.puuid, 'matches': self.matches, 'decks': self.decks, 'expedition': {'id': self.expedition.id, 'data': self.expedition.data, 'deck_code': self.expedition.deck_code}})			
			self.expedition_update()
			return self.state
		#This occurs whenever an expedition game ends. This event should trigger an update to the win-loss record for this expedition		
		if 'Wins' in states or 'Losses' in states:
			self.active_deck = self.heartbeat.active_deck['DeckCode']
			self.expedition_update()
		#This occurs whenever a pick is made for the current expedition. This should update the expedition_deck_code in App_Memory			
		if 'DraftPicks' or 'Swapping' in states:
			self.expedition_update()
		return self.state

	def expedition_update(self):
		self.expedition.update(self.heartbeat.expedition_state)	
		write({'username': self.username, 'puuid': self.puuid, 'matches': self.matches, 'decks': self.decks, 'expedition': {'id': self.expedition.id, 'data': self.expedition.data, 'deck_code': self.expedition.deck_code}})			


	#
	def loading_notification(self, msg):
		return msg+'\n'


class Expedition:

	def __init__(self, data):
		self.id = token_hex(5)
		self.data = data
		self.deck_code = None
		self.card_data = []
		self.champions_index = {}
		self.record = self.data['Record']
		if self.data['Deck']:
			self.deck_code = encode_deck(self.data['Deck'])
			for card in self.data['Deck']:
				x = get_card_info(card)
				if x not in self.card_data:
					self.card_data.append(x)
					if x.rarity == 'Champion':
						self.champions_index[x.cardCode]=len(self.card_data)


	def update(self, data):
		self.data = data
		self.record = self.data['Record']
		if self.data['Deck']:
			self.deck_code = encode_deck(self.data['Deck'])