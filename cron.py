import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
import datetime
from django import shortcuts
from django.utils import simplejson as json
import logging

import clot
from games import Game
from main import hitapi
from players import Player

def go(request):
	logging.info("Starting cron...")
	checkInProgressGames()
	setResultsOfAllFinishedGames()

	#clot.createGames()
	#clot.createGames_RandomMatchup()
	clot.createGames_Swiss()

	clot.setRanks()
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
			loser = findLoser(data)
			logging.info('Identified the loser of game ' + str(g.wlnetGameID) + ' is ' + str(loser))
			g.winner = winner.key().id()
			g.loser = loser.key().id()
			#g.winningTeamName = 'bob' #winner.key().name()
			g.dateEnded = datetime.datetime.now()
			g.save()
		else:
			#It's still going.
			
			#g.winningTeamName = 'bill' #winner.key().name()
			#g.save()
			
			logging.info('Game ' + str(g.wlnetGameID) + ' is not finished, state=' + state + ', numTurns=' + data['numberOfTurns'])

def setResultsOfAllFinishedGames():
	logging.info('')
	logging.info('in setResultsOfAllFinishedGames()')
	
	players = Player.all()
	playersDict = dict([(p.key().id(),p) for p in players])
	
	finished_games = Game.all().filter("winner !=", None)
	for game in finished_games:
		logging.info('finished game: '+str(game))
		game.winningTeamName = str(playersDict[game.winner])
		logging.info('game.winningTeamName = '+str(game.winningTeamName))
		game.save()

	finished_games = Game.all().filter("winner !=", None)
	for game in finished_games:
		logging.info('REPEAT game.winningTeamName = '+str(game.winningTeamName))

	logging.info('leaving setResultsOfAllFinishedGames()')
	logging.info('')

def findWinner(data):
	"""Simple helper function to return the Player who won the game.  This takes json data returned by the GameFeed 
	API.  We just look for a player with the "won" state and then retrieve their Player instance from the database"""
	winnerInviteToken = filter(lambda p: p['state'] == 'Won', data['players'])[0]["id"]
	return Player.all().filter('inviteToken =', winnerInviteToken)[0]

def findLoser(data):
	"""Simple helper function to return the Player who lost the game.  This takes json data returned by the GameFeed 
	API.  We just look for a player with the "won" state and then retrieve their Player instance from the database"""
	loserInviteToken = filter(lambda p: p['state'] != 'Won', data['players'])[0]["id"]
	return Player.all().filter('inviteToken =', loserInviteToken)[0]

