import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django.utils import simplejson as json
import logging
from django import http
from django import shortcuts

import main
import players
import games


class Game(db.Model):
	"""Represents a game.  This has its own ID local to the CLOT, but it also stores wlnetGameID which is the ID of the game on WarLight.net.
	This also stores a winner field which contains a playerID only if the game is finished.
	The __repr__ function is just used for debugging."""

	winner = db.IntegerProperty()
	loser = db.IntegerProperty()
	#winnerName = db.StringProperty()  #added by unkn 
	wlnetGameID = db.IntegerProperty(required=True)
	name = db.StringProperty()
	dateCreated = db.DateTimeProperty(auto_now_add=True)
	dateEnded = db.DateTimeProperty()
	legitimateGame = db.BooleanProperty(default=True)

	winningTeamName = db.StringProperty(default='not known as of yet')  #added by unkn 


	def __repr__(self):
		return str(self.key().id()) + " wlnetGameID=" + str(self.wlnetGameID)



class GamePlayer(db.Model):
	"""Represents a player in a game.  Each game will have at least two corresponding rows in this table."""
	gameID = db.IntegerProperty(required=True)
	playerID = db.IntegerProperty(required=True)
	state = db.StringProperty()
	def __repr__(self):
		return "gameID=" + str(self.gameID) + ",playerID=" + str(self.playerID) + ",state=" + str(self.state)


def createGame(the_players, templateID):
	"""This calls the WarLight.net API to create a game, and then creates the Game and GamePlayer rows in the local DB"""
	gameName = ' vs '.join([p.name for p in the_players])[:50]  #game names are limited to %) characters by the api

	config = main.getClotConfig()
	apiRetStr = main.postToApi('/API/CreateGame', json.dumps( { 
															 'hostEmail': config.adminEmail, 
															 'hostAPIToken': config.adminApiToken,
															 'templateID': templateID,
															 'gameName': gameName,
															 'personalMessage': 'a game from one of unknwonsoldiers tourneys',
															 'players': [ { 'token': p.inviteToken, 'team': 'None' } for p in the_players]
															 }))
	apiRet = json.loads(apiRetStr)

	gid = int(apiRet.get('gameID', -1))
	if gid == -1:
		raise Exception("CreateGame returned error: " + apiRet.get('error', apiRetStr))

	g = Game(wlnetGameID=gid, name=gameName)
	g.save()

	for p in the_players:
		games.GamePlayer(playerID = p.key().id(), gameID = g.key().id()).save()
		#teams.append()

	logging.info("Created game " + str(g.key().id()) + " '" + gameName + "'")

	return g

