import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django.utils import simplejson as json
import logging

from django import http
from django import shortcuts
from django import newforms as forms


import main
import players


##from django.utils.encoding import smart_str, smart_unicode   #needed for non-unicode characters

class JoinForm(forms.Form):
	inviteToken = forms.CharField(label="Invite Token")
	tourney_id = forms.CharField(label="tourney_id")
	tourney_password = forms.CharField(label="tourney_password (enter only if it is required)",required=False)

def go(request):
	"""Create a player.	GET shows a blank form, POST processes it."""
	logging.info('in join.go')

	form = JoinForm(data=request.POST or None)

	#now deal with the form etc

	if not request.POST:
		return shortcuts.render_to_response('join.html', {'form': form})

	if not form.is_valid():
		return shortcuts.render_to_response('join.html', {'form': form})

	#see if we are letting more players join.
	tourney_id = int(form.clean_data['tourney_id'])
	tourney = main.ClotConfig.all().filter('tourney_id =', tourney_id).get()
	if not tourney:
		form.errors['tourney_id'] = 'tourney_id is invalid.'
		return shortcuts.render_to_response('join.html', {'form': form})
	
	players_are_gated_q = False
	if main.arePlayersGated(tourney_id):
		players_are_gated_q = True
		logging.info('players_are_gated_q = '+str(players_are_gated_q))
		return http.HttpResponseRedirect('/players_are_gated')

	if players.numPlayersParticipating(tourney_id) >= main.getMaximumNumberOfPlayers(tourney_id):
		logging.info('too many players')
		return http.HttpResponseRedirect('/cannot_join') 


	inviteToken = form.clean_data['inviteToken']

	#Call the warlight API to get the name, color, and verify that the invite token is correct
	apiret = main.hitapi('/API/ValidateInviteToken', { 'Token':  inviteToken })

	if not "tokenIsValid" in apiret:
		form.errors['inviteToken'] = 'The supplied invite token is invalid. Please ensure you copied it from WarLight.net correctly.'
		return shortcuts.render_to_response('join.html', {'form': form})

	tourney_password = str(form.clean_data['tourney_password'])
	if main.getIfRequirePasswordToJoin(tourney_id):
		if tourney_password != main.getTourneyPassword(tourney_id):
			form.errors['tourney_password'] = 'The supplied tourney_password is required but is not correct.  Please type the correct password for this tourney.'
			return shortcuts.render_to_response('join.html', {'form': form})

	#Ensure this invite token doesn't already exist
	existing = players.Player.all().filter('inviteToken =', inviteToken).filter("tourney_id =", tourney_id).get()
	if existing:
		#If someone tries to join when they're already in the DB, just set their isParticipating flag back to true
		existing.isParticipating = True
		existing.save()
		return http.HttpResponseRedirect('tourneys/' + str(tourney_id) + '/player/' + str(existing.key().id()))

	data = json.loads(apiret)

	player_name = data['name']
	if type(data['name']) is unicode:
		logging.info('dealing with unicode player name ...')
		player_name = player_name.encode('ascii','ignore')  #this deals with special characters that would mess up our code, by removing them. 
		logging.info('player_name:')
		logging.info(player_name)
		logging.info('player-name looks ok or not?')

	player = players.Player(inviteToken=inviteToken, name=player_name, color=data['color'], isMember=data['isMember'].lower() == 'true') 

	if main.getClotConfig(tourney_id).membersOnly and not player.isMember:
		form.errors['inviteToken'] = 'This site only allows members to join.	See the Membership tab on WarLight.net for information about memberships.'
		return shortcuts.render_to_response('join.html', {'form': form})

	player.put()
	player.player_id = str(player.key().id())
	player.tourney_id = tourney_id
	player.save()
	logging.info("Created player")
	logging.info(player)
	
	return http.HttpResponseRedirect('tourneys/' + str(tourney_id) + '/player/' + str(player.key().id()))

#def join_Redirect
