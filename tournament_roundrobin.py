
import logging
from copy import deepcopy
import random

import new_utility_functions
import main
import players
import games
import clot




def createGames_RoundRobin():
	"""This is called periodically to check for new games that need to be created.
	the roundrobin part is that we want everyone to play everyone else.
	so the players not currently in games are just paired up with each other,
	so long as they have not yet played each other.
	"""
	logging.info('')
	logging.info('in createGames_RoundRobin()')

	if main.hasTourneyFinished():
		logging.info('round robin tourney has finished')
		return

	#Retrieve all games that are ongoing
	activeGames = list(games.Game.all().filter("winner =", None))
	activeGameIDs = dict([[g.key().id(), g] for g in activeGames])
	logging.info("Active games: " + str(activeGameIDs))

	#Throw all of the player IDs that are in these ongoing games into a dictionary
	playerIDsInGames = dict([[gp.playerID, gp] for gp in games.GamePlayer.all() if gp.gameID in activeGameIDs])

	#Find all players who aren't in the dictionary (and therefore aren't in any games) and also have not left the CLOT (isParticipating is true)
	allPlayers = players.Player.all()
	
	all_players_vec = [p for p in allPlayers]
	logging.info("all_players_vec: ")
	logging.info(all_players_vec)
	all_players_keys_ids_vec = [p.key().id()  for p in allPlayers]
	logging.info("all_players_keys_ids_vec: " + str(all_players_keys_ids_vec))
	player_ids_in_games_vec = [p for p in playerIDsInGames]
	logging.info("player_ids_in_games_vec: " + str(player_ids_in_games_vec))
	
	playersNotInGames = [p for p in allPlayers if p.isParticipating and p.key().id() not in playerIDsInGames]
	logging.info("Players not in games: ")
	logging.info(playersNotInGames)

	#------------------------
	#now pair up players who are not in games.  IF they have not played each otehr yet.

	#get the head-to-head matrix, so we can see who has played who
	head_to_head_biggermat, head_to_head_2d = new_utility_functions.getHeadToHeadTable()
	##logging.info('head_to_head_2d:')
	##logging.info(head_to_head_2d)

	#
	the_ids = deepcopy(head_to_head_biggermat[0][1:])
	logging.info('the_ids:')
	logging.info(the_ids)

	#Randomize the order
	random.shuffle(playersNotInGames)

	#loop over all possible pairs, and pair IF they have not played each other yet
	paired_yet = [False]*len(playersNotInGames)
	list_for_pairing = []
	for i in range(0,len(playersNotInGames)-1):
		if not paired_yet[i]:
			pi = playersNotInGames[i]
			pi_id = int(pi.player_id)
			pi_index = the_ids.index(pi_id)  #find where in the head-to-head matrix this player is.
			
			logging.info('pi:')
			logging.info(pi)
			logging.info(pi_id)
			logging.info(pi_index)
			
			for j in range(i+1,len(playersNotInGames)):
				if (not paired_yet[j]) and (not paired_yet[i]):
					pj = playersNotInGames[j]
					pj_id = int(pj.player_id)
					pj_index = the_ids.index(pj_id)   #find where in the head-to-head matrix this player is.
					
					logging.info('pj:')
					logging.info(pj)
					logging.info(pj_id)
					logging.info(pj_index)
			
					if (head_to_head_2d[pi_index][pj_index][0]==0) and (head_to_head_2d[pj_index][pi_index][0]==0):  
						#they have not played each other.
						#so match them.
						paired_yet[i] = True
						paired_yet[j] = True
						list_for_pairing.append(pi)
						list_for_pairing.append(pj)
						logging.info('paired '+str(pi)+' '+str(pj))

	##debug
	logging.info("new player order is: ")
	logging.info(list_for_pairing)
	for pair in clot.pairs(list_for_pairing):
		logging.info(pair)
	##end of debug

	#The template ID defines the settings used when the game is created.  You can create your own template on warlight.net and enter its ID here
	templateID = main.getTemplateID()

	#Create a game for everyone not in a game.
	gamesCreated = [games.createGame(pair, templateID) for pair in clot.pairs(list_for_pairing)]
	logging.info("Created games " + str(gamesCreated))
	
	if (len(activeGames)==0) and (len(list_for_pairing)==0):
		if main.isTourneyInPlay():
			#tourney is in play, but no games are going on, and we found no games we could create.
			#so the tourney is over
			main.endTourney()
			logging.info('')
			logging.info('all games have been played, so TOURNAMENT IS OVER !!!!!!!!!!!!!!')
			logging.info('')



