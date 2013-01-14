import os
import logging

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django.utils import simplejson as json

from django import http
from django import shortcuts


import players
import games
import main


def go(request, tourney_id, playerID):
	tourney_id = int(tourney_id)
	tourney_clotconfig = main.getClotConfig(tourney_id)
	playerID = int(playerID)
	p = players.Player.get_by_id(playerID)
	gameIDs = set([g.gameID for g in games.GamePlayer.all().filter("tourney_id =", int(tourney_id)).filter('playerID =', playerID)]) ###.run(batch_size=1000)])
	the_games = [g for g in games.Game.all() if g.key().id() in gameIDs]

	if not main.doesTourneyExist(tourney_id, tourney_clotconfig):
		logging.info('tourney does not exist')
		return shortcuts.render_to_response('tourney_does_not_exist.html')
	
	
		return shortcuts.render_to_response('player_does_not_exist_in_this_tourney.html')

	return shortcuts.render_to_response('viewplayer.html', {'player': p, 'games': the_games, 'tourney_id': tourney_id, 
	'tourney_name': main.getTourneyName(int(tourney_id), tourney_clotconfig),
	'tourney_path': '/tourneys/' + str(tourney_id)
	})
