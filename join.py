import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django.utils import simplejson as json
import logging

from django import http
from django import shortcuts
from django import newforms as forms
from main import hitapi
from main import getClotConfig
from main import group
from players import Player


class JoinForm(forms.Form):
	inviteToken = forms.CharField(label="Invite Token")

def go(request):
	"""Create a player.	GET shows a blank form, POST processes it."""

	form = JoinForm(data=request.POST or None)

	if not request.POST:
		return shortcuts.render_to_response('join.html', {'form': form})

	if not form.is_valid():
		return shortcuts.render_to_response('join.html', {'form': form})

	inviteToken = form.clean_data['inviteToken']

	#Call the warlight API to get the name, color, and verify that the invite token is correct
	apiret = hitapi('/API/ValidateInviteToken', { 'Token':  inviteToken })

	if not "tokenIsValid" in apiret:
		form.errors['inviteToken'] = 'The supplied invite token is invalid. Please ensure you copied it from WarLight.net correctly.'
		return shortcuts.render_to_response('join.html', {'form': form})

	#Ensure this invite token doesn't already exist
	existing = Player.all().filter('inviteToken =', inviteToken).get()
	if existing:
		#If someone tries to join when they're already in the DB, just set their isParticipating flag back to true
		existing.isParticipating = True
		existing.save()
		return http.HttpResponseRedirect('/player/' + str(existing.key().id()))

	data = json.loads(apiret)
	player = Player(inviteToken=inviteToken, name=data['name'], color=data['color'], isMember=data['isMember'].lower() == 'true')

	if getClotConfig().membersOnly and not player.isMember:
		form.errors['inviteToken'] = 'This site only allows members to join.	See the Membership tab on WarLight.net for information about memberships.'
		return shortcuts.render_to_response('join.html', {'form': form})

	player.put()
	logging.info("Created player " + str(player))
	
	return http.HttpResponseRedirect('/player/' + str(player.key().id()))