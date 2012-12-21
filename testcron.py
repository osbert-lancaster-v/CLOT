
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

from clot import *
import cron


def testcron(request):

	logging.info('in testcron()')

	#setRanks()
	#createGames()
	logging.info("about to call cron.go(dummy)")
	cron.go('db_unkn')
	logging.info("called cron.go(dummy)")
	
	#return shortcuts.render_to_response('test.html', {'testdata': 'foo'})
	return shortcuts.render_to_response(
	'testcron.html', {'testcrondata': 'foo unkn cron'}

	)
	
	logging.info('leaving testcron()')




