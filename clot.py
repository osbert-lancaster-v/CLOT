import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django.utils import simplejson as json
import logging
import random

from games import Game
from games import GamePlayer
from games import createGame
from players import Player
from main import hitapi
from main import group

import tournament_swiss


##from django.utils.encoding import smart_str, smart_unicode   #needed for non-unicode characters


def createGames_RandomMatchup():
	"""This is called periodically to check for new games that need to be created.  
	You should replace this with your own logic for how games are to be created.
	Right now, this function just randomly pairs up players who aren't in a game."""

	#Retrieve all games that are ongoing
	activeGames = list(Game.all().filter("winner =", None))
	activeGameIDs = dict([[g.key().id(), g] for g in activeGames])
	logging.info("Active games: " + str(activeGameIDs))

	#Throw all of the player IDs that are in these ongoing games into a dictionary
	playerIDsInGames = dict([[gp.playerID, gp] for gp in GamePlayer.all() if gp.gameID in activeGameIDs])

	#Find all players who aren't in the dictionary (and therefore aren't in any games) and also have not left the CLOT (isParticipating is true)
	allPlayers = Player.all()
	
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
	templateID = 251301

	#Create a game for everyone not in a game.
	gamesCreated = [createGame(pair, templateID) for pair in pairs(playersNotInGames)]
	logging.info("Created games " + str(gamesCreated))


def createGames_Swiss():
	"""This is called periodically to check for new games that need to be created.  
	You should replace this with your own logic for how games are to be created.
	Right now, this function just randomly pairs up players who aren't in a game."""
	logging.info('')
	logging.info('in createGames_Swiss()')

	#Retrieve all games that are ongoing
	activeGames = list(Game.all().filter("winner =", None))
	activeGameIDs = dict([[g.key().id(), g] for g in activeGames])
	logging.info("Active games: " + str(activeGameIDs))

	if activeGames:
		logging.info('games still in progress.  cannot start next round until these games finish.')
	else:
		logging.info('no games in progress.  so we move on to the next round.')

		players_ids_matched_list = tournament_swiss.getMatchedList()

		if not players_ids_matched_list:
			logging.info('')
			logging.info('seems everyone has played everyone else, so TOURNAMENT IS OVER !!!!!!!!!!!!!!')
			logging.info('')
			return

		players_ids_names_dict = dict([[gp.player_id, gp] for gp in Player.all()])
		logging.info('players_ids_names_dict')
		logging.info(players_ids_names_dict)

		players_names_matched_list = [players_ids_names_dict[i] for i in players_ids_matched_list]

		#The template ID defines the settings used when the game is created.  You can create your own template on warlight.net and enter its ID here
		templateID = 251301

		#Create a game for everyone not in a game.
		gamesCreated = [createGame(pair, templateID) for pair in pairs(players_names_matched_list)]
		logging.info("Created games " + str(gamesCreated))
	logging.info('')


def createGames():
	"""This is called periodically to check for new games that need to be created.  
	You should replace this with your own logic for how games are to be created.
	Right now, this function just randomly pairs up players who aren't in a game."""

	#Retrieve all games that are ongoing
	activeGames = list(Game.all().filter("winner =", None))
	activeGameIDs = dict([[g.key().id(), g] for g in activeGames])
	logging.info("Active games: " + str(activeGameIDs))

	#Throw all of the player IDs that are in these ongoing games into a dictionary
	playerIDsInGames = dict([[gp.playerID, gp] for gp in GamePlayer.all() if gp.gameID in activeGameIDs])

	#Find all players who aren't in the dictionary (and therefore aren't in any games) and also have not left the CLOT (isParticipating is true)
	allPlayers = Player.all()
	
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
	templateID = 251301

	#Create a game for everyone not in a game.
	gamesCreated = [createGame(pair, templateID) for pair in pairs(playersNotInGames)]
	logging.info("Created games " + str(gamesCreated))

def pairs(lst):
	"""Simple helper function that groups a list into pairs.  For example, [1,2,3,4,5] would return [1,2],[3,4]"""
	for i in range(1, len(lst), 2):
		yield lst[i-1], lst[i]

def setRanks():
	"""This looks at what games everyone has won and sets their currentRank field.
	The current algorithm is very simple - just award ranks based on number of games won.
	You should replace this with your own ranking logic."""
	
	logging.info('in setRanks()')
	##gamesge = Game.objects.all()
	##logging.info(gamesge)

	#Load all finished games
	finishedGames = Game.all().filter("winner !=", None)
	logging.info("finishedGames:")
	logging.info(finishedGames)

	players_id_name_dict = getPlayersIDNameDict()
	logging.info('players_id_name_dict')
	logging.info(players_id_name_dict)

	#Group them by who won
	finishedGamesGroupedByWinner = group(finishedGames, lambda g: g.winner)
	logging.info("finishedGamesGroupedByWinner:")
	logging.info(finishedGamesGroupedByWinner)
	for game in Game.all():
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
	winCounts = dict(map(lambda (playerID,games): (playerID, len(games)), finishedGamesGroupedByWinner.items())) 

	#Map this from Player.all() to ensure we have an entry for every player, even those with no wins
	playersMappedToNumWins = [(p, winCounts.get(p.key().id(), 0)) for p in Player.all()] 

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


def getFinishedGames():
	return Game.all().filter("winner !=", None)

def getPlayersIDNameDict():
	return dict([[p.key().id() , p] for p in Player.all()])


