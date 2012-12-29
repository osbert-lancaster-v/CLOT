import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
import logging
from django import http
from django import shortcuts
#from players import Player
#from games import Game
#from games import GamePlayer
#from main import group
#from main import ClotConfig
#from main import getClotConfig

from new_utility_functions import getHeadToHeadTable
import tournament_swiss
import main
import games
import players

from copy import deepcopy


def index(request):
	"""Request / """

	#Check if we need to do first-time setup
	if main.ClotConfig.all().count() == 0:
		return http.HttpResponseRedirect('/setup')

	#Gather data used by home.html
	the_players = players.Player.all()
	playersDict = dict([(p.key().id(),p) for p in the_players])
	logging.info('playersDict')
	logging.info(playersDict)

	#added by unkn - puts object id into .player_id data member
	for p in the_players:
#		if p.player_id != str(p.key().id()) #so it has not been set yet.
		p.player_id = str(p.key().id())  
		p.save()

	#arrange players by rank
	the_players = players.Player.all()
	the_players = sorted(the_players, key=lambda z: z.currentRank)

	gamePlayers = main.group(games.GamePlayer.all(), lambda z: z.gameID)

	#arrange games by reverse of created date
	the_games = games.Game.all()
	the_games = sorted(the_games, key=lambda z: z.dateCreated, reverse=True)
	
	for game in the_games:
		logging.info('game: '+str(game))
		logging.info('game.winningTeamName = '+str(game.winningTeamName))


	#do the head-to-head table
	biggermat, head_to_head_2d = getHeadToHeadTable()
	biggermat_str = deepcopy(biggermat)
	for i in range(1,len(biggermat_str)):
		for j in range(1,len(biggermat_str[i])):
			if i==j:
				biggermat_str[i][j] = "---"
			else:
				biggermat_str[i][j] = str(biggermat_str[i][j][0]) + "-" + str(biggermat_str[i][j][1])

	#see if players are gated
	players_gated_string = "players may join or leave"
	if main.arePlayersGated():
		players_gated_string = "players may NOT join or leave"

	#get tourney_status_string
	tourney_status_string = 'Tourney Not Yet Started'
	if main.isTourneyInPlay():
		if str(main.getTourneyType()) == 'swiss':
			tourney_status_string = 'Tourney In Progress.  Round '+str(main.getRoundNumber())+' of '+str(main.getNumRounds())
		else:
			tourney_status_string = 'Tourney In Progress.'
	elif main.hasTourneyFinished():
		winner = the_players[0]
		winner_name = winner.name
		tourney_status_string = 'Tourney has finished.  Congratulations to '+str(winner_name)+'!'

	minNumPlayersString= 'minNumPlayers: '+str(main.getMinimumNumberOfPlayers())
	maxNumPlayersString= 'maxNumPlayers: '+str(main.getMaximumNumberOfPlayers())
	starttimeString = 'starttime will be:  '+str(main.getStarttime())+'    provided we have minimum number of players.'
	currentTimeString = 'current time =     '+str(main.getCurrentTime())
	tourney_type_string = str(main.getTourneyType()) + ' tourney'

	return shortcuts.render_to_response('home.html',{'players': the_players, 'config': main.getClotConfig(), 'games': the_games, 
			'biggermat':biggermat_str,
			'players_gated_string':players_gated_string,
			'minNumPlayersString':minNumPlayersString,
			'maxNumPlayersString':maxNumPlayersString,
			'tourney_status_string':tourney_status_string,
			'starttimeString':starttimeString,
			'currentTimeString':currentTimeString,
			'tourney_type_string':tourney_type_string
			})

