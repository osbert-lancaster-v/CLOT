
import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django import http
from django import shortcuts

import httplib
import urllib
import random
import logging

#from clot import *
import cron


def go(request):

	logging.info('in players_are_gated.go()')

	
	logging.info('leaving players_are_gated.go()')

	return shortcuts.render_to_response('players_are_gated.html')


def cannot_join(request):
	logging.info('in cannot_join.go()')

	
	logging.info('leaving cannot_join.go()')

	return shortcuts.render_to_response('cannot_join.html')

