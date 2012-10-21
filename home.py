import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django import http
from django import shortcuts
from players import Player
from main import *
from games import *

import httplib
import urllib

def index(request):
  """Request / """
  #Check if we need to do first-time setup
  if ClotConfig.all().count() == 0:
    return http.HttpResponseRedirect('/setup')

  rankedplayers = db.GqlQuery('SELECT * FROM Player WHERE currentRank > 0 ORDER BY currentRank ASC')
  nonrankedplayers = db.GqlQuery('SELECT * FROM Player WHERE currentRank = 0')
  return shortcuts.render_to_response('home.html',{'rankedplayers': rankedplayers, 'nonrankedplayers': nonrankedplayers, 'config': getClotConfig()})
