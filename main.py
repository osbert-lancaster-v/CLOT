import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
import httplib
import urllib

from itertools import groupby

from django import http
from django import shortcuts


class ClotConfig(db.Model):
	name = db.StringProperty(required=True, verbose_name="Name of your tournament or ladder")
	adminEmail = db.StringProperty(required=True, verbose_name="Your WarLight.net e-mail address")
	adminApiToken = db.StringProperty(required=True, verbose_name="API token (see above for how to get this)")
	membersOnly = db.BooleanProperty(required=True, verbose_name="Only allow WarLight members to join")


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
		try:
			config = form.save(commit=False)

			#Verify the email/apitoken work
			verify = hitapiwithauth('/API/ValidateAPIToken', {}, config.adminEmail, config.adminApiToken)
			if not "apiTokenIsValid" in verify:
					errors['__all__'] = 'Email/APIToken were not valid. Response = ' + verify
					
		except ValueError, err:
			errors['__all__'] = unicode(err)
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
	#logging.info("POSTing to " + api + ", data=" + postData)

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