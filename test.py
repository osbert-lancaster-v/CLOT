﻿import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django import http
from django import shortcuts

import httplib
import urllib
import random
import logging


#the stuff here is just for testing.  visit /test on the webpage to call this code. 

import cron

import tournament_swiss


def test(request):
	logging.info('in test()')


	tournament_swiss.getMatchedList_Swiss()


	return shortcuts.render_to_response('test.html', {'testdata': 'foo unkn'})
	
	logging.info('leaving test()')



