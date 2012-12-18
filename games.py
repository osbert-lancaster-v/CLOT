import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django.utils import simplejson as json
import logging
from django import http
from django import shortcuts
from main import postToApi
from main import hitapi
from main import getClotConfig
from players import Player

class Game(db.Model):
	"""Represents a game.  This has its own ID local to the CLOT, but it also stores wlnetGameID which is the ID of the game on WarLight.net.
	This also stores a winner field which contains a playerID only if the game is finished.
	The __repr__ function is just used for debugging."""

	winner = db.IntegerProperty()
	wlnetGameID = db.IntegerProperty(required=True)
	name = db.StringProperty()
	dateCreated = db.DateTimeProperty(auto_now_add=True)
	dateEnded = db.DateTimeProperty()
	def __repr__(self):
		return str(self.key().id()) + " wlnetGameID=" + str(self.wlnetGameID)


class GamePlayer(db.Model):
	"""Represents a player in a game.  Each game will have at least two corresponding rows in this table."""
	gameID = db.IntegerProperty(required=True)
	playerID = db.IntegerProperty(required=True)
	def __repr__(self):
		return "gameID=" + str(self.gameID) + ",playerID=" + str(self.playerID)


def createGame(players, templateID):
	"""This calls the WarLight.net API to create a game, and then creates the Game and GamePlayer rows in the local DB"""
	gameName = ' vs '.join([p.name for p in players])

	config = getClotConfig()
	apiRetStr = postToApi('/API/CreateGame', json.dumps( { 
															 'hostEmail': config.adminEmail, 
															 'hostAPIToken': config.adminApiToken,
															 'templateID': templateID,
															 'gameName': gameName,
															 'personalMessage': '',
															 'players': [ { 'token': p.inviteToken, 'team': 'None' } for p in players]
															 }))
	apiRet = json.loads(apiRetStr)

	gid = int(apiRet.get('gameID', -1))
	if gid == -1:
		raise Exception("CreateGame returned error: " + apiRet.get('error', apiRetStr))

	g = Game(wlnetGameID=gid, name=gameName)
	g.save()

	for p in players:
		GamePlayer(playerID = p.key().id(), gameID = g.key().id()).save()

	logging.info("Created game " + str(g.key().id()) + " '" + gameName + "'")

	return g
