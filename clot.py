import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django.utils import simplejson as json
import logging
import random

#from games import Game
#from games import GamePlayer
#from games import createGame
#from players import Player
#from main import hitapi
##from main import group

import tournament_swiss
import main
import new_utility_functions
import games
import players

from copy import deepcopy


##from django.utils.encoding import smart_str, smart_unicode   #needed for non-unicode characters


def createGames_RandomMatchup():
	"""This is called periodically to check for new games that need to be created.  
	You should replace this with your own logic for how games are to be created.
	Right now, this function just randomly pairs up players who aren't in a game."""

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

	#Randomize the order
	random.shuffle(playersNotInGames)
	
	#debug
	random.shuffle(playersNotInGames)
	logging.info("new player order is: ")
	logging.info(playersNotInGames)
	for pair in pairs(playersNotInGames):
		logging.info(pair)
	random.shuffle(playersNotInGames)
	logging.info("new player order is: ")
	logging.info(playersNotInGames)
	for pair in pairs(playersNotInGames):
		logging.info(pair)
	#end of debug

	#The template ID defines the settings used when the game is created.  You can create your own template on warlight.net and enter its ID here
	templateID = main.getTemplateID()

	#Create a game for everyone not in a game.
	gamesCreated = [games.createGame(pair, templateID) for pair in pairs(playersNotInGames)]
	logging.info("Created games " + str(gamesCreated))


def createGames_Swiss():
	"""This is called periodically to check if a round has finished.  If so, new games are created."""

	logging.info('')
	logging.info('in createGames_Swiss()')

	if main.hasTourneyFinished():
		logging.info('swiss tourney has finished')
		return

	#Retrieve all games that are ongoing
	activeGames = list(games.Game.all().filter("winner =", None))
	activeGameIDs = dict([[g.key().id(), g] for g in activeGames])
	logging.info("Active games: " + str(activeGameIDs))

	if activeGames:
		logging.info('games still in progress.  cannot start next round until these games finish.')
	else:
		logging.info('no games in progress.  so we move on to the next round.')
		
		if main.getRoundNumber() == main.getNumRounds():
			main.endTourney()
			logging.info('')
			logging.info('all rounds have been played, so TOURNAMENT IS OVER !!!!!!!!!!!!!!')
			logging.info('')
			return

		players_ids_matched_list = tournament_swiss.getMatchedList_Swiss()

		if not players_ids_matched_list:
			main.endTourney()
			logging.info('')
			logging.info('seems everyone has played everyone else, so TOURNAMENT IS OVER !!!!!!!!!!!!!!')
			logging.info('')
			return

		players_ids_names_dict = dict([[gp.player_id, gp] for gp in players.Player.all()])
		logging.info('players_ids_names_dict')
		logging.info(players_ids_names_dict)

		players_names_matched_list = [players_ids_names_dict[i] for i in players_ids_matched_list]

		#The template ID defines the settings used when the game is created.  You can create your own template on warlight.net and enter its ID here
		templateID = main.getTemplateID()

		#Create a game for everyone not in a game.
		gamesCreated = [games.createGame(pair, templateID) for pair in pairs(players_names_matched_list)]
		logging.info("Created games " + str(gamesCreated))
		
		main.incrementRoundNumber()
		logging.info("\n ------------------------------------ \n swiss tourney round " + str(main.getRoundNumber())+ " starting.  \n ---------------------------")
	logging.info('')


def createGames_RoundRobin():
	"""This is called periodically to check for new games that need to be created."""
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
	for pair in pairs(list_for_pairing):
		logging.info(pair)
	##end of debug

	#The template ID defines the settings used when the game is created.  You can create your own template on warlight.net and enter its ID here
	templateID = main.getTemplateID()

	#Create a game for everyone not in a game.
	gamesCreated = [games.createGame(pair, templateID) for pair in pairs(list_for_pairing)]
	logging.info("Created games " + str(gamesCreated))
	
	if (len(activeGames)==0) and (len(list_for_pairing)==0):
		if main.isTourneyInPlay():
			#tourney is in play, but no games are going on, and we found no games we could create.
			#so the tourney is over
			main.endTourney()
			logging.info('')
			logging.info('all games have been played, so TOURNAMENT IS OVER !!!!!!!!!!!!!!')
			logging.info('')


def createGames():
	"""This is called periodically to check for new games that need to be created.  
	You should replace this with your own logic for how games are to be created.
	Right now, this function just randomly pairs up players who aren't in a game."""

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

	#Randomize the order
	random.shuffle(playersNotInGames)
	
	#debug
	random.shuffle(playersNotInGames)
	logging.info("new player order is: ")
	logging.info(playersNotInGames)
	for pair in pairs(playersNotInGames):
		logging.info(pair)
	random.shuffle(playersNotInGames)
	logging.info("new player order is: ")
	logging.info(playersNotInGames)
	for pair in pairs(playersNotInGames):
		logging.info(pair)
	#end of debug


	#The template ID defines the settings used when the game is created.  You can create your own template on warlight.net and enter its ID here
	templateID = main.getTemplateID()

	#Create a game for everyone not in a game.
	gamesCreated = [games.createGame(pair, templateID) for pair in pairs(playersNotInGames)]
	logging.info("Created games " + str(gamesCreated))

def pairs(lst):
	"""Simple helper function that groups a list into pairs.  For example, [1,2,3,4,5] would return [1,2],[3,4]"""
	for i in range(1, len(lst), 2):
		yield lst[i-1], lst[i]

def setRanks_ByNumWinsOnly():
	"""This looks at what games everyone has won and sets their currentRank field.
	The current algorithm is very simple - just award ranks based on number of games won.
	You should replace this with your own ranking logic."""
	
	logging.info('in setRanks()')
	##gamesge = Game.objects.all()
	##logging.info(gamesge)

	#Load all finished games
	finishedGames = games.Game.all().filter("winner !=", None)
	logging.info("finishedGames:")
	logging.info(finishedGames)

	players_id_name_dict = getPlayersIDNameDict()
	logging.info('players_id_name_dict')
	logging.info(players_id_name_dict)

	#Group them by who won
	finishedGamesGroupedByWinner = main.group(finishedGames, lambda g: g.winner)
	logging.info("finishedGamesGroupedByWinner:")
	logging.info(finishedGamesGroupedByWinner)
	for game in games.Game.all():
		logging.info('game:')
		logging.info(game)
		
		
		if game.winner != None:
			pass
			#logging.info("---")
			#logging.info(game)
			#winner = game.winner
			#logging.info(winner)
			#logging.info(players_id_name_dict[winner])
			###game.winningTeamName = 'abc'         ##  str(players_id_name_dict[winner])
			#logging.info(game.winningTeamName)
			#logging.info(game)
			###game.save()


	#Get rid of the game data, and replace it with the number of games each player won
	winCounts = dict(map(lambda (playerID,the_games): (playerID, len(the_games)), finishedGamesGroupedByWinner.items())) 

	#Map this from Player.all() to ensure we have an entry for every player, even those with no wins
	playersMappedToNumWins = [(p, winCounts.get(p.key().id(), 0)) for p in players.Player.all()] 

	#sort by the number of wins each player has.
	playersMappedToNumWins.sort(key=lambda (player,numWins): numWins, reverse=True)

	#Now that it's sorted, we can just loop through each player and set their currentRank
	for index,(player,numWins) in enumerate(playersMappedToNumWins):
		player.currentRank = index + 1 #index is 0-based, and we want our top player to be ranked #1, so we add one.
		player.numWins = numWins #added by unkn
		player.save()
		logging.info('player:')
		logging.info(player)


	logging.info('setRanks finished')

def setRanks():
	setRanks_WithTiebreaks()

def setRanks_WithTiebreaks():
	"""this function ranks players by number of wins.  
	then, players who tie on number of wins are separated 
	by how many wins their beaten opponets have.  
	i.e. beating someone who won lots of games is better 
	for your ranking than beating someone with few wins. """
	
	logging.info('in setRanks_WithTiebreaks()')
	
	head_to_head_biggermat, head_to_head_2d = new_utility_functions.getHeadToHeadTable()
	
	the_ids = deepcopy(head_to_head_biggermat[0][1:])
	logging.info('the_ids:')
	logging.info(the_ids)
	
	the_players = players.Player.all()
	num_players = len(list(the_players))
	assert(num_players==len(the_ids))
	
	num_wins = [0]*num_players
	for i in range(0,num_players):
		logging.info(i)
		for j in range(0,num_players):
			num_wins[i] += head_to_head_2d[i][j][0]
	
	sum_of_wins_of_players_you_beat = [0]*num_players
	for i in range(0,num_players):
		logging.info(i)
		for j in range(0,num_players):
			sum_of_wins_of_players_you_beat[j] = head_to_head_2d[i][j][0]*num_wins[j]
	
	points_and_playerid=[]
	for i in range(0,num_players):
		points_and_playerid.append(
				[ num_wins[i] +0.000001*sum_of_wins_of_players_you_beat[i] , the_ids[i] ]
				)
	logging.info(points_and_playerid)
	
	points_and_playerid.sort()
	
	logging.info(points_and_playerid)
	
	for p in the_players:
		player_id = int(p.player_id)
		rank = -1
		for i in range(0,len(points_and_playerid)):
			if points_and_playerid[i][1]==player_id:
				rank = i+1
		p.currentRank = rank
	
	logging.info('leaving setRanks_WithTiebreaks()')





def getFinishedGames():
	return games.Game.all().filter("winner !=", None)

def getPlayersIDNameDict():
	return dict([[p.key().id() , p] for p in players.Player.all()])


