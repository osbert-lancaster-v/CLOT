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
import new_utility_functions
import site_password

#also, import the files for your own special tournament types
import tournament_swiss
import tournament_roundrobin
import tournament_randommatchup


#this is the main class for a tournament.
#it holds the tourney type, max number of players, etc.
class ClotConfig(db.Model):
	name = db.StringProperty(required=True, verbose_name="Name of your tournament or ladder")

	tourney_type = db.StringProperty(required=True, verbose_name="Tournament type:  swiss  roundrobin  randommatchup")

	adminEmail = db.StringProperty(required=True, verbose_name="Your WarLight.net e-mail address")
	adminApiToken = db.StringProperty(required=True, verbose_name="API token (see above for how to get this)")
	site_password = db.StringProperty(required=True, verbose_name="the site_password")
	membersOnly = db.BooleanProperty(verbose_name="Only allow WarLight members to join")
	requirePasswordToJoin = db.BooleanProperty(verbose_name="Require password to join")
	tourney_password = db.StringProperty(default = '-----', verbose_name="tourney_password (only if you want password)")
	
	templateID = db.IntegerProperty(default=251301, verbose_name="template ID - (only 1v1 games  work atm)  e.g. 258265" )

	numRounds = db.IntegerProperty(default= 3 , verbose_name="number of rounds (needed for swiss tourneys)")
	minimumNumberOfPlayers = db.IntegerProperty(default= 2 )
	#default_max_num_players = 2**int(numRounds) ##doesn't work.  IntegerProperty -> int complains
	maximumNumberOfPlayers = db.IntegerProperty(default=8)
	startDate = db.DateTimeProperty(required=True, default=datetime.now().replace(microsecond=0), verbose_name="Tourney Start Time")
	howLongYouHaveToJoinGames = db.IntegerProperty(default=15, verbose_name="players must join games within this number of minutes")

	#other variables, but not to be set by the user. 
	playersAreGated = db.BooleanProperty(default=False, verbose_name="do NOT modify this" )
	roundNumber = db.IntegerProperty(default=0, verbose_name="do NOT modify this" )

	tourneyInPlay = db.BooleanProperty(default=False, verbose_name="do NOT modify this" )
	tourneyFinished = db.BooleanProperty(default=False, verbose_name="do NOT modify this" )
	
	tourney_id = db.IntegerProperty(default = -1, verbose_name="do NOT modify this" )
	tourney_urlpath = db.StringProperty(default = 'none', verbose_name="do NOT modify this" )
	



	def __unicode__(self):
		return str(self.name) +'    '+ str(self.tourney_type) +'   '+ str(self.tourneyInPlay)

	def __repr__(self):
		return str(self.name) +'    '+ str(self.tourney_type) +'   '+ str(self.tourneyInPlay)

#---------------------------------------------------------------------
#functions associated with ClotConfig

def getTourneyType(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		return c.tourney_type
	assert False #should not have got here

def getTourneyName(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		return c.name
	assert False #should not have got here

def getIfRequirePasswordToJoin(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		return c.requirePasswordToJoin
	assert False #should not have got here

def getTourneyPassword(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		return c.tourney_password
	assert False #should not have got here

def seeIfTourneyCanStart(tourney_id):
	tourney_type = getTourneyType(tourney_id)
	if tourney_type == 'swiss':
		return tournament_swiss.seeIfTourneyCanStart_Swiss(tourney_id) #we use the swiss version of this function
	elif tourney_type == 'roundrobin':
		return new_utility_functions.seeIfTourneyCanStart(tourney_id) #we use the default function
	elif tourney_type == 'randommatchup':
		return new_utility_functions.seeIfTourneyCanStart(tourney_id) #we use the default function
	else:
		assert(False) #no valid fn

def createGames(tourney_id):
	tourney_type = getTourneyType(tourney_id)
	if tourney_type == 'swiss':
		return tournament_swiss.createGames_Swiss(tourney_id) #we use the swiss version of this function
	elif tourney_type == 'roundrobin':
		return tournament_roundrobin.createGames_RoundRobin(tourney_id)
	elif tourney_type == 'randommatchup':
		return tournament_randommatchup.createGames_RandomMatchup(tourney_id)
	else:
		assert(False) #no valid fn


def getHowLongYouHaveToJoinGames(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		return c.howLongYouHaveToJoinGames
	assert False #should not have got here

def getStarttime(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		return c.startDate.replace(microsecond=0)
	assert False #should not have got here

def getCurrentTime():
	return datetime.now().replace(microsecond=0)

def areWePastStarttime(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		return (c.startDate < datetime.now())
	assert False #should not have got here

def getMaximumNumberOfPlayers(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		return c.maximumNumberOfPlayers
	assert False #should not have got here

def arePlayersGated(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		if c.playersAreGated:
			return True
		else:
			return False
	assert False #should not have got here

def getRoundNumber(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		return c.roundNumber
	assert False #should not have got here

def incrementRoundNumber(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		c.roundNumber += 1
		c.save()
		logging.info(str(c))
		return
	assert False #should not have got here

def getNumRounds(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		return c.numRounds
	assert False #should not have got here

def getMinimumNumberOfPlayers(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		return c.minimumNumberOfPlayers
	assert False #should not have got here

def isTourneyInPlay(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		return c.tourneyInPlay
	assert False #should not have got here

def hasTourneyFinished(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		return c.tourneyFinished
	assert False #should not have got here

def startTourney(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		c.tourneyInPlay = True
		c.playersAreGated = True #hack.  should not really be here. 
		c.save()
		logging.info(str(c))
		return
	assert False

def endTourney(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		c.tourneyInPlay = False
		c.tourneyFinished = True
		c.save()
		logging.info(c)
		return
	return False

def getTemplateID(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
		return c.templateID
	assert False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ClotConfigForm(djangoforms.ModelForm):
	class Meta:
		model = ClotConfig

def getClotConfig(tourney_id):
	for c in ClotConfig.all().filter("tourney_id =", tourney_id):
			return c

def getAnyClotConfig():
	for c in ClotConfig.all():
		return c

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
			errors['tourney_type'] = 'unknown_tourney_type'
		
		if config.site_password != site_password.getSitePassword():
			logging.info('site_password incorrect !')
			errors['site_password'] = 'site_password incorrect'

	if errors:
		return shortcuts.render_to_response('setup.html', {'form': form})

	config.put()
	config.tourney_id = config.key().id()
	logging.info('config.tourney_id = ' + str(config.tourney_id))
	config.tourney_urlpath = 'tourneys/'+str(config.tourney_id)
	logging.info('config.tourney_urlpath = ' + config.tourney_urlpath)
	config.save()

	return http.HttpResponseRedirect(config.tourney_urlpath)

wlnet = 'warlight.net'


def hitapi(api, params):
	config = getAnyClotConfig()
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


