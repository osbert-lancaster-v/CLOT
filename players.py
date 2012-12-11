import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
import json

from django import http
from django import shortcuts
from main import hitapi
from main import getClotConfig
from main import group

class Player(db.Model):
	name = db.StringProperty()
	inviteToken = db.StringProperty(required=True)
	color = db.StringProperty()
	isParticipating = db.BooleanProperty(default=True, required=True)
	currentRank = db.IntegerProperty(default=0, required=True)
	created = db.DateTimeProperty(auto_now_add=True)
	modified = db.DateTimeProperty(auto_now=True)
	isMember = db.BooleanProperty()

	def __repr__(self):
		return str(self.key().id()) + " " + self.name

class EditPlayerForm(djangoforms.ModelForm):
	class Meta:
		model = Player
		fields = ['isParticipating']


def edit(request, player_id):
	"""edit a player.	GET shows a blank form, POST processes it."""
	player = Player.get(db.Key.from_path(Player.kind(), int(player_id)))
	if player is None:
		return http.HttpResponseNotFound('No player exists with that key (%r)' %
																			 player_id)
	

	form = EditPlayerForm(data=request.POST or None, instance=player)

	if not request.POST:
		return shortcuts.render_to_response('editplayer.html', {'form': form, 'player': player})

	errors = form.errors
	if not errors:
		try:
			player = form.save()
		except ValueError, err:
			errors['__all__'] = unicode(err)
	if errors:
		return shortcuts.render_to_response('editplayer.html', {'form': form, 'player': player})

	return http.HttpResponseRedirect('/')
