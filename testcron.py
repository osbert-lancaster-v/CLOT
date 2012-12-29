
import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django import http
from django import shortcuts

import httplib
import urllib
import logging

import clot
import cron
import main


def testcron(request):

	logging.info('in testcron()')
	
	###main.gatePlayers()
	###logging.info('main.arePlayersGated() = '+str(main.arePlayersGated()))
	###main.unGatePlayers()
	###logging.info('main.arePlayersGated() = '+str(main.arePlayersGated()))

	#setRanks()
	#createGames()
	logging.info("about to call cron.go(dummy)")
	cron.go('db_unkn')
	logging.info("called cron.go(dummy)")


	
	logging.info('leaving testcron()')
	#return shortcuts.render_to_response('test.html', {'testdata': 'foo'})
	return shortcuts.render_to_response(
	'testcron.html', {'testcrondata': 'foo unkn cron'}
	)





