import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django.utils import simplejson as json

from django import http
from django import shortcuts
from main import hitapi
from main import getClotConfig
from main import group
from games import GamePlayer
from games import Game
from players import Player

def go(request, playerID):
	playerID = int(playerID)
	p = Player.get_by_id(playerID)
	gameIDs = set([g.gameID for g in GamePlayer.all().filter('playerID =', playerID)])
	games = [g for g in Game.all() if g.key().id() in gameIDs]


	return shortcuts.render_to_response('viewplayer.html', {'player': p, 'games': games})