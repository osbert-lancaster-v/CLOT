
import logging
from copy import deepcopy

from django import shortcuts

import new_utility_functions
import main
import players
import games
import clot


def myadmin_tourneys(request):
	logging.info('in tourneys()')
	
	tourneys = main.ClotConfig.all()
	tourney_list = [tourney for tourney in tourneys]
	tourney_list = sorted(tourney_list, key=lambda tourney: tourney.startDate, reverse=True)

	return shortcuts.render_to_response('myadmin_tourneys.html',{'tourney_list': tourney_list }  )



def myadmin_players(request):
	logging.info('in tourneys()')
	
	the_players = players.Player.all()
	the_players_list = [the_player for the_player in the_players]

	return shortcuts.render_to_response('myadmin_players.html',{'the_players_list': the_players_list }  )


