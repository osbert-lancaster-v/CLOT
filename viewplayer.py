import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django.utils import simplejson as json

from django import http
from django import shortcuts


import players
import games


def go(request, playerID):
	playerID = int(playerID)
	p = players.Player.get_by_id(playerID)
	gameIDs = set([g.gameID for g in games.GamePlayer.all().filter('playerID =', playerID)])
	the_games = [g for g in games.Game.all() if g.key().id() in gameIDs]


	return shortcuts.render_to_response('viewplayer.html', {'player': p, 'games': the_games})
