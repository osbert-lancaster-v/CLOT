import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
import logging
from django import http
from django import shortcuts

from copy import deepcopy

import new_utility_functions
import main
import games
import players


#maybe you need tournament-type specific things here, maybe
import tournament_swiss


def index(request):    #deprecated
	"""Request / """
	return shortcuts.render_to_response('home.html',{'nowt': 'nowt' })


def index_new(request,tourney_id):
	"""Request / """
	logging.info('in index_new(' +str(tourney_id)+ ')')

	tourney_id = int(tourney_id)
	logging.info('tourney_id = '+str(tourney_id))
	tourney_clotconfig = main.getClotConfig(tourney_id)

	if not main.doesTourneyExist(tourney_id, tourney_clotconfig):
		logging.info('tourney does not exist, redirecting user to tourneys info instead')
		return shortcuts.render_to_response('tourney_does_not_exist.html' )

	#arrange players by rank
	the_players = players.Player.all().filter("tourney_id =", tourney_id)#.run(batch_size=1000)
	the_players = sorted(the_players, key=lambda z: z.currentRank)

	gamePlayers = main.group(games.GamePlayer.all().filter("tourney_id =", tourney_id), lambda z: z.gameID)  #.run(batch_size=1000)

	#arrange games by reverse of created date
	the_games = games.Game.all().filter("tourney_id =", tourney_id)#.run(batch_size=1000)
	the_games = sorted(the_games, key=lambda z: z.dateCreated, reverse=True)
	#for game in the_games:
	#	logging.info('game: '+str(game))
	#	logging.info('game.winningTeamName = '+str(game.winningTeamName))


	#do the head-to-head table
	biggermat, head_to_head_2d = new_utility_functions.getHeadToHeadTable(tourney_id)
	biggermat_str = deepcopy(biggermat)
	for i in range(1,len(biggermat_str)):
		for j in range(1,len(biggermat_str[i])):
			if i==j:
				biggermat_str[i][j] = "---"
			else:
				biggermat_str[i][j] = str(biggermat_str[i][j][0]) + "-" + str(biggermat_str[i][j][1])

	#see if players are gated
	players_gated_string = "players may join or leave"
	if main.arePlayersGated(tourney_id, tourney_clotconfig):
		players_gated_string = "players may NOT join or leave"

	#get tourney_status_string
	tourney_status_string = 'Tourney Not Yet Started'
	if main.isTourneyInPlay(tourney_id, tourney_clotconfig):
		if str(main.getTourneyType(tourney_id, tourney_clotconfig)) == 'swiss':
			tourney_status_string = 'Tourney In Progress.  Round '+str(main.getRoundNumber(tourney_id, tourney_clotconfig))+' of '+str(main.getNumRounds(tourney_id, tourney_clotconfig))
		else:
			tourney_status_string = 'Tourney In Progress.'
	elif main.hasTourneyFinished(tourney_id, tourney_clotconfig):
		winner = the_players[0]
		winner_name = winner.name
		tourney_status_string = 'Tourney has finished.  Congratulations to '+str(winner_name)+'!'

	minNumPlayersString= 'minNumPlayers: '+str(main.getMinimumNumberOfPlayers(tourney_id, tourney_clotconfig))
	maxNumPlayersString= 'maxNumPlayers: '+str(main.getMaximumNumberOfPlayers(tourney_id, tourney_clotconfig))
	starttimeString = 'starttime will be:  '+str(main.getStarttime(tourney_id, tourney_clotconfig))+'    provided we have minimum number of players.'
	currentTimeString = 'current time =     '+str(main.getCurrentTime())
	tourney_type_string = str(main.getTourneyType(tourney_id, tourney_clotconfig)) + ' tourney'
	how_long_you_have_to_join_games_string = 'You have '+str(main.getHowLongYouHaveToJoinGames(tourney_id, tourney_clotconfig))+' minutes to join your auto-created games.  After that you may lose that game!!'
	template_id = main.getTemplateID(tourney_id, tourney_clotconfig)

	#things for specific tourney types
	if main.getTourneyType(tourney_id, tourney_clotconfig)=='swiss':
		swiss_games_info_table = tournament_swiss.getTourneyRoundsAndGameInfo(tourney_id)
	else:
		swiss_games_info_table = 0
	#end of things for specific tourney types

	return shortcuts.render_to_response('tourney_home.html',{'players': the_players, 'config': tourney_clotconfig, 'games': the_games, 
			'biggermat':biggermat_str,
			'players_gated_string':players_gated_string,
			'minNumPlayersString':minNumPlayersString,
			'maxNumPlayersString':maxNumPlayersString,
			'tourney_status_string':tourney_status_string,
			'starttimeString':starttimeString,
			'currentTimeString':currentTimeString,
			'tourney_type_string':tourney_type_string,
			'how_long_you_have_to_join_games_string':how_long_you_have_to_join_games_string,
			'template_title_string':'Game Template',
			'template_id':template_id,
			'swiss_games_info_table':swiss_games_info_table,
			'join_url':'/tourneys/'+str(tourney_id)+'/join',
			'leave_url':'/tourneys/'+str(tourney_id)+'/leave',
			'tourney_id':str(tourney_id)
			})




def display_tourneys(request):
	"""Request / """
	
	tourneys = main.ClotConfig.all()
	tourney_list = [tourney for tourney in tourneys]
	tourney_list = sorted(tourney_list, key=lambda tourney: tourney.startDate, reverse=True)
	
	logging.info('tourney_list = '+str(tourney_list))

	return shortcuts.render_to_response('tourneys.html',{'tourney_list': tourney_list
			})


