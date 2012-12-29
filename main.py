import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
import httplib
import urllib
import logging

from itertools import groupby

from django import http
from django import shortcuts

from datetime import datetime

import clot
import tournament_swiss


#this is the main class for a tournament.
#it holds the tourney type, max number of players, etc.
class ClotConfig(db.Model):
	name = db.StringProperty(required=True, verbose_name="Name of your tournament or ladder")

	tourney_type = db.StringProperty(required=True, verbose_name="Tournament type:  swiss  roundrobin  randommatchup")

	adminEmail = db.StringProperty(required=True, verbose_name="Your WarLight.net e-mail address")
	adminApiToken = db.StringProperty(required=True, verbose_name="API token (see above for how to get this)")
	membersOnly = db.BooleanProperty(verbose_name="Only allow WarLight members to join")

	templateID = db.IntegerProperty(default=251301, verbose_name="templateID - default is 1v1 strategic (currently only 1V1 games will work)    [258265 is medium earth 1v1 BUT 75% luck plus other changes]" )

	numRounds = db.IntegerProperty(default= 3 , verbose_name="number of rounds (needed for swiss tourneys)")
	minimumNumberOfPlayers = db.IntegerProperty(default= 4 )
	#default_max_num_players = 2**int(numRounds) ##doesn't work.  IntegerProperty -> int complains
	maximumNumberOfPlayers = db.IntegerProperty(default=8)
	startDate = db.DateTimeProperty(required=True, default=datetime.now().replace(microsecond=0), verbose_name="Tourney Start Time")
	howLongYouHaveToJoinGames = db.IntegerProperty(default=15, verbose_name="players must join games within this number of minutes")

	#other variables, but not to be set by the user. 
	playersAreGated = db.BooleanProperty(default=False, verbose_name="playersAreGated: do NOT select this" )
	roundNumber = db.IntegerProperty(default=0, verbose_name="roundNumber: do NOT modify this" )

	tourneyInPlay = db.BooleanProperty(default=False, verbose_name="tourneyInPlay: do NOT select this")
	tourneyFinished = db.BooleanProperty(default=False, verbose_name="tourneyFinished: do NOT select this")


#START OF: horrible hacks :( - basically assumes/requires that we have only one instance of ClotConfig :(

def getTourneyType():
	for c in ClotConfig.all():
		return c.tourney_type

def seeIfTourneyCanStart():
	tourney_type = getTourneyType()
	if tourney_type == 'swiss':
		return tournament_swiss.seeIfTourneyCanStart()
	elif tourney_type == 'roundrobin':
		return tournament_swiss.seeIfTourneyCanStart()
	elif tourney_type == 'randommatchup':
		return tournament_swiss.seeIfTourneyCanStart()
	else:
		assert(False) #no valid fn

def createGames():
	tourney_type = getTourneyType()
	if tourney_type == 'swiss':
		return clot.createGames_Swiss()
	elif tourney_type == 'roundrobin':
		return clot.createGames_RoundRobin()
	elif tourney_type == 'randommatchup':
		return clot.createGames_RandomMatchup()
	else:
		assert(False) #no valid fn


def getHowLongYouHaveToJoinGames():
	for c in ClotConfig.all():
		return c.howLongYouHaveToJoinGames

def getStarttime():
	for c in ClotConfig.all():
		return c.startDate.replace(microsecond=0)

def getCurrentTime():
	return datetime.now().replace(microsecond=0)

def areWePastStarttime():
	for c in ClotConfig.all():
		return (c.startDate < datetime.now())

def getMaximumNumberOfPlayers():
	for c in ClotConfig.all():
		return c.maximumNumberOfPlayers

def arePlayersGated():
	for c in ClotConfig.all():
		if c.playersAreGated:
			return True
	return False

#def gatePlayers():
	#for c in ClotConfig.all():
		#c.playersAreGated = True
		#c.save()
		#logging.info(c)

#def unGatePlayers():
	#for c in ClotConfig.all():
		#c.playersAreGated = False
		#c.save()
		#logging.info(c)

def getRoundNumber():
	for c in ClotConfig.all():
		return c.roundNumber

def incrementRoundNumber():
	for c in ClotConfig.all():
		c.roundNumber += 1
		c.save()
		logging.info(str(c))

def getNumRounds():
	for c in ClotConfig.all():
		return c.numRounds

def getMinimumNumberOfPlayers():
	for c in ClotConfig.all():
		return c.minimumNumberOfPlayers

def isTourneyInPlay():
	for c in ClotConfig.all():
		return c.tourneyInPlay

def hasTourneyFinished():
	for c in ClotConfig.all():
		return c.tourneyFinished

def startTourney():
	for c in ClotConfig.all():
		c.tourneyInPlay = True
		c.playersAreGated = True #hack.  should not really be here. 
		c.save()
		logging.info(str(c))

def endTourney():
	for c in ClotConfig.all():
		c.tourneyInPlay = False
		c.tourneyFinished = True
		c.save()
		logging.info(c)

def getTemplateID():
	for c in ClotConfig.all():
		return c.templateID

#END OF: horrible hacks :( - basically assumes/requires that we have only one instance of ClotConfig :(

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ClotConfigForm(djangoforms.ModelForm):
	class Meta:
		model = ClotConfig

def getClotConfig():
	for c in ClotConfig.all():
			return c

def setup(request):
	"""Called the first time this site is accessed.
		GET shows a blank form, POST processes it."""

	form = ClotConfigForm(data=request.POST or None)

	if not request.POST:
		return shortcuts.render_to_response('setup.html', {'form': form})

	errors = form.errors
	if not errors:
		config = form.save(commit=False)

		#Verify the email/apitoken work
		verify = hitapiwithauth('/API/ValidateAPIToken', {}, config.adminEmail, config.adminApiToken)
		if not "apiTokenIsValid" in verify:
				errors['adminApiToken'] = 'The provided email or API Token were not valid.'
		
		tourney_type = config.tourney_type  #getTourneyType()
		if not (tourney_type=='swiss' or tourney_type=='roundrobin' or tourney_type=='randommatchup'):
			logging.info('tourney_type:')
			logging.info(tourney_type)
			logging.info(str(tourney_type))
			logging.info('not known !!')
			errors['unknown_tourney_type'] = 'unknown_tourney_type'

	if errors:
		return shortcuts.render_to_response('setup.html', {'form': form})

	config.put()

	return http.HttpResponseRedirect('/')

wlnet = 'warlight.net'


def hitapi(api, params):
	config = getClotConfig()
	return hitapiwithauth(api, params, config.adminEmail, config.adminApiToken)
	
def hitapiwithauth(api, params, email, apitoken):
	prms = { 'Email': email, 'APIToken': apitoken }
	prms.update(params)

	
	conn = httplib.HTTPConnection(wlnet, 80)
	conn.connect()
	request = conn.putrequest('POST', api)
	conn.send(urllib.urlencode(prms))
	resp = conn.getresponse()
	ret = resp.read()

	conn.close()
	return ret

def postToApi(api, postData):
	logging.info("POSTing to " + api + ", data=" + postData)

	conn = httplib.HTTPConnection(wlnet, 80)
	conn.connect()
	request = conn.putrequest('POST', api)
	conn.send(postData)
	resp = conn.getresponse()
	ret = resp.read()

	conn.close()
	return ret

def group(collection, keyfunc):
	data = sorted(collection, key=keyfunc)
	ret = {}
	for k,g in groupby(data, keyfunc):
		ret[k] = list(g)
	return ret
