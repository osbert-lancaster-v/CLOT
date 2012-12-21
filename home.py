import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
import logging
from django import http
from django import shortcuts
from players import Player
from games import Game
from games import GamePlayer
from main import group
from main import ClotConfig
from main import getClotConfig

from new_utility_functions import getHeadToHeadTable


def index(request):
	"""Request / """

	#Check if we need to do first-time setup
	if ClotConfig.all().count() == 0:
		return http.HttpResponseRedirect('/setup')

	#Gather data used by home.html
	players = Player.all()
	playersDict = dict([(p.key().id(),p) for p in players])
	logging.info('playersDict')
	logging.info(playersDict)

	#added by unkn - puts object id into .player_id data member
	for p in players:
#		if p.player_id != str(p.key().id()) #so it has not been set yet.
		p.player_id = str(p.key().id())  
		p.save()

	#arrange players by rank
	players = Player.all()
	players = sorted(players, key=lambda z: z.currentRank)

	gamePlayers = group(GamePlayer.all(), lambda z: z.gameID)

	#arrange games by reverse of created date
	games = Game.all()
	games = sorted(games, key=lambda z: z.dateCreated, reverse=True)
	
	for game in games:
		logging.info('game: '+str(game))
		logging.info('game.winningTeamName = '+str(game.winningTeamName))


	#do the head-to-head table
	biggermat = getHeadToHeadTable()

	return shortcuts.render_to_response('home.html',{'players': players, 'config': getClotConfig(), 'games': games, 
			'biggermat':biggermat})
