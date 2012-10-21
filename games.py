import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django import http
from django import shortcuts
from main import hitapi
from main import getClotConfig
from players import Player
import json

class Game(db.Model):
    winner = db.IntegerProperty()

class GamePlayer(db.Model):
    gameID = db.IntegerProperty(required=True)
    playerID = db.IntegerProperty(required=True)

def cron(request):
    CreateGames()


def CreateGames():
    allPlayers = Player.all()
    activeGames = Game.all().filter( {"winner": None })
    #(map(lambda z: z.players, activeGames), [])
    
    
