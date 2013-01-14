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


class LeaveForm(forms.Form):
	inviteToken = forms.CharField(label="Invite Token")
	tourney_id = forms.CharField(label="tourney_id")

def go(request):
	"""This allows players to leave the CLOT.  GET shows a blank form, POST processes it."""

	form = LeaveForm(data=request.POST or None)

	if not request.POST:
		return shortcuts.render_to_response('leave.html', {'form': form})

	if not form.is_valid():
		return shortcuts.render_to_response('leave.html', {'form': form})

	#see if we are letting players join or leave
	tourney_id = int(form.clean_data['tourney_id'])
	tourney_clotconfig = main.ClotConfig.all().filter('tourney_id =', tourney_id)#.run(batch_size=1000)
	if not tourney_clotconfig:
		form.errors['tourney_id'] = 'tourney_id is invalid.'
		return shortcuts.render_to_response('leave.html', {'form': form})

	players_are_gated_q = False
	if main.arePlayersGated(tourney_id, tourney_clotconfig):
		players_are_gated_q = True
		logging.info('players_are_gated_q = '+str(players_are_gated_q))
		return http.HttpResponseRedirect('/players_are_gated')
	logging.info('players_are_gated_q = '+str(players_are_gated_q))

	inviteToken = form.clean_data['inviteToken']

	#Find the player by their token
	player = players.Player.all().filter('inviteToken =', inviteToken).filter("tourney_id =", tourney_id).get() #.run(batch_size=1000)
	if not player:
		form.errors['inviteToken'] = 'Invite token is invalid.'
		return shortcuts.render_to_response('leave.html', {'form': form})

	#When they leave, just set their isParticipating to false
	player.isParticipating = False
	player.save()

	logging.info("Player left ladder ")
	logging.info(player)
	return http.HttpResponseRedirect('tourneys/' + str(tourney_id) + '/player/' + str(player.key().id()))

