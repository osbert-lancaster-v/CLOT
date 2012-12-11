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

def index(request):
	"""Request / """
	#Check if we need to do first-time setup
	if ClotConfig.all().count() == 0:
		return http.HttpResponseRedirect('/setup')

	#Gather data used by home.html
	players = Player.all()
	playersDict = dict([(p.key().id(),p) for p in players])

	gamePlayers = group(GamePlayer.all(), lambda z: z.gameID)
	games = Game.all()

	return shortcuts.render_to_response('home.html',{'players': players, 'config': getClotConfig(), 'games': games})
