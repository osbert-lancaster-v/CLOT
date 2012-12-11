import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
import datetime
from django import shortcuts
import json
import logging

from clot import createGames
from clot import setRanks
from games import Game
from main import hitapi
from players import Player

def go(request):
	logging.info("Starting cron...")
	checkInProgressGames()
	createGames()
	setRanks()
	logging.info("Cron done")
	return shortcuts.render_to_response('cron.html')

def checkInProgressGames():
	"""This is called periodically to look for games that are finished.  If we find
	a finished game, we record the winner"""

	#Find all games that we think aren't finished
	activeGames = Game.all().filter("winner =", None)

	for g in activeGames:
		#call WarLight's GameFeed API so that it can tell us if it's finished or not
		apiret = hitapi('/API/GameFeed?GameID=' + str(g.wlnetGameID), {})
		data = json.loads(apiret)
		state = data.get('state', 'err')
		if state == 'err': raise Exception("GameFeed API failed.  Message = " + data.get('error', apiret))

		if state == 'Finished':
			#It's finished. Record the winner and save it back.
			winner = findWinner(data)
			logging.info('Identified the winner of game ' + str(g.wlnetGameID) + ' is ' + str(winner))
			g.winner = winner.key().id()
			g.dateEnded = datetime.datetime.now()
			g.save()
		else:
			#It's still going.
			logging.info('Game ' + str(g.wlnetGameID) + ' is not finished, state=' + state + ', numTurns=' + data['numberOfTurns'])

def findWinner(data):
	"""Simple helper function to return the Player who won the game.  This takes json data returned by the GameFeed 
	API.  We just look for a player with the "won" state and then retrieve their Player instance from the database"""
	winnerInviteToken = filter(lambda p: p['state'] == 'Won', data['players'])[0]["id"]
	return Player.all().filter('inviteToken =', winnerInviteToken)[0]

