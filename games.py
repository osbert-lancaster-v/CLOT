import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django import http
from django import shortcuts
import json
import logging
from main import postToApi
from main import getClotConfig

class Game(db.Model):
	"""Represents a game.  This has its own ID local to the CLOT, but it also stores wlnetGameID which is the ID of the game on WarLight.net.
	This also stores a winner field which contains a playerID only if the game is finished.
	The __repr__ function is just used for debugging."""

	winner = db.IntegerProperty()
	wlnetGameID = db.IntegerProperty(required=True)
	def __repr__(self):
		return str(self.key().id()) + " wlnetGameID=" + str(self.wlnetGameID)

class GamePlayer(db.Model):
	"""Represents a player in a game.  Each game will have at least two corresponding rows in this table."""
	gameID = db.IntegerProperty(required=True)
	playerID = db.IntegerProperty(required=True)

def createGame(players):
	"""This calls the WarLight.net API to create a game, and then creates the Game and GamePlayer rows in the local DB"""
	gameName = ' vs '.join([p.name for p in players])

	config = getClotConfig()
	apiRetStr = postToApi('/API/CreateGame', json.dumps( { 
															 'hostEmail': config.adminEmail, 
															 'hostAPIToken': config.adminApiToken,
															 'templateID': config.templateID,
															 'gameName': gameName,
															 'personalMessage': '',
															 'players': [ { 'token': p.inviteToken, 'team': 'None' } for p in players]
															 }))
	apiRet = json.loads(apiRetStr)

	gid = int(apiRet.get('gameID', -1))
	if gid == -1:
		raise Exception("CreateGame returned error: " + apiRet.get('error', apiRetStr))

	g = Game(wlnetGameID=gid)
	g.save()

	for p in players:
		GamePlayer(playerID = p.key().id(), gameID = g.key().id()).save()

	logging.info("Created game " + str(g.key().id()) + " '" + gameName + "'")

	return g

def checkCreateGames():
	"""This is called peridocally to check for new games that need to be created.  
	This is where CLOT developers should enter their logic for how games are to be created.
	Right now, this function just pairs up players who aren't in a game randomly."""

	#Get all Game IDs that are ongoing
	activeGames = list(Game.all().filter("winner =", None))
	activeGameIDs = dict([[g.key().id(), g] for g in activeGames])
	logging.info("Found active games: " + str(activeGameIDs))

	#Throw all of the player IDs that are in these ongoing games into a dictionary
	playerIDsInGames = dict([[gp.playerID, gp] for gp in GamePlayer.all() if gp.gameID in activeGameIDs])

	#Find all players who aren't in the dictionary (and therefore aren't in any games) and also have not left the CLOT (isParticipating is true)
	allPlayers = Player.all()
	playersNotInGames = [p for p in allPlayers if p.isParticipating and p.key().id() not in playerIDsInGames]
	logging.info("Players not in games: " + str(playersNotInGames))

	#Randomize the order
	random.shuffle(playersNotInGames)

	#Create a game for everyone not in a game.
	gamesCreated = [createGame(pair) for pair in pairs(playersNotInGames)]

	return shortcuts.render_to_response('test.html', {'testdata': 'foo'})

def pairs(lst):
	"""Simple helper function that groups a list into pairs.  For example, [1,2,3,4,5] would return [1,2],[3,4]"""
	for i in range(1, len(lst), 2):
		yield lst[i-1], lst[i]
