import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django import http
from django import shortcuts
from clot import *
import httplib
import urllib
import random
import logging

def test(request):
	setRanks()
	return shortcuts.render_to_response('test.html', {'testdata': 'foo'})



