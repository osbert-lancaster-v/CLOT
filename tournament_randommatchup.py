
import logging
import random

import new_utility_functions
import main
import players
import games
import clot



def createGames_RandomMatchup(tourney_id, tourney_clotconfig):
	"""This is called periodically to check for new games that need to be created.  
	You should replace this with your own logic for how games are to be created.
	Right now, this function just randomly pairs up players who aren't in a game."""

	#Retrieve all games that are ongoing
	activeGames = list(games.Game.all().filter("winner =", None).filter("tourney_id =", tourney_id)) ###.run(batch_size=1000))
	activeGameIDs = dict([[g.key().id(), g] for g in activeGames])
	logging.info("Active games: " + str(activeGameIDs))

	#Throw all of the player IDs that are in these ongoing games into a dictionary
	playerIDsInGames = dict([[gp.playerID, gp] for gp in games.GamePlayer.all().filter("tourney_id =", tourney_id) if gp.gameID in activeGameIDs])  ###.run(batch_size=1000)

	#Find all players who aren't in the dictionary (and therefore aren't in any games) and also have not left the CLOT (isParticipating is true)
	allPlayers = players.Player.all().filter("tourney_id =", tourney_id)#.run(batch_size=1000)
	
	all_players_vec = [p for p in allPlayers]
	#logging.info("all_players_vec: ")
	#logging.info(all_players_vec)
	all_players_keys_ids_vec = [p.key().id()  for p in allPlayers]
	#logging.info("all_players_keys_ids_vec: " + str(all_players_keys_ids_vec))
	player_ids_in_games_vec = [p for p in playerIDsInGames]
	#logging.info("player_ids_in_games_vec: " + str(player_ids_in_games_vec))
	
	playersNotInGames = [p for p in allPlayers if p.isParticipating and p.key().id() not in playerIDsInGames]
	#logging.info("Players not in games: ")
	#logging.info(playersNotInGames)

	#Randomize the order
	random.shuffle(playersNotInGames)
	
	#debug
	random.shuffle(playersNotInGames)
	#logging.info("new player order is: ")
	#logging.info(playersNotInGames)
	for pair in clot.pairs(playersNotInGames):
		logging.info(pair)
	random.shuffle(playersNotInGames)
	#logging.info("new player order is: ")
	#logging.info(playersNotInGames)
	for pair in clot.pairs(playersNotInGames):
		logging.info(pair)
	#end of debug

	#The template ID defines the settings used when the game is created.  You can create your own template on warlight.net and enter its ID here
	templateID = main.getTemplateID(tourney_id, tourney_clotconfig)

	#Create a game for everyone not in a game.
	gamesCreated = [games.createGame(pair, templateID, tourney_id) for pair in clot.pairs(playersNotInGames)]
	logging.info("Created games " + str(gamesCreated))
	
	#note that for randommatchup, we never end the tournmey (unlike for eg swiss and for roundrobin). 


