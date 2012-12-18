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


class LeaveForm(forms.Form):
	inviteToken = forms.CharField(label="Invite Token")

def go(request):
	"""This allows players to leave the CLOT.  GET shows a blank form, POST processes it."""

	form = LeaveForm(data=request.POST or None)

	if not request.POST:
		return shortcuts.render_to_response('leave.html', {'form': form})

	if not form.is_valid():
		return shortcuts.render_to_response('leave.html', {'form': form})

	inviteToken = form.clean_data['inviteToken']

	#Find the player by their token
	player = Player.all().filter('inviteToken =', inviteToken).get()
	if not player:
		form.errors['inviteToken'] = 'Invite token is invalid.'
		return shortcuts.render_to_response('leave.html', {'form': form})

	#When they leave, just set their isParticipating to false
	player.isParticipating = False
	player.save()

	logging.info("Player left ladder " + str(player))
	return http.HttpResponseRedirect('/player/' + str(player.key().id()))

