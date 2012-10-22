import os

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django import http
from django import shortcuts
import httplib
import urllib

class ClotConfig(db.Model):
  name = db.StringProperty(required=True)
  adminEmail = db.StringProperty(required=True)
  adminApiToken = db.StringProperty(required=True)
  templateID = db.IntegerProperty(required=True)
  membersOnly = db.BooleanProperty(required=True)


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

  

def hitapi(api, params):
  config = getClotConfig()
  return hitapiwithauth(api, params, config.adminEmail, config.adminApiToken)
  
def hitapiwithauth(api, params, email, apitoken):
  prms = { 'Email': email,'APIToken': apitoken }
  prms.update(params)

  wlnet = 'warlight.net'
  
  conn = httplib.HTTPConnection(wlnet, 80)
  conn.connect()
  request = conn.putrequest('POST', api)
  conn.send(urllib.urlencode(prms ))
  resp = conn.getresponse()
  ret = resp.read()

  conn.close()
  return ret
