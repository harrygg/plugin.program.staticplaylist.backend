# -*- coding: utf-8 -*-
import os
import sys
import json

def __update__(action, location, crash=None):
  try:
    import time
    lu = settings.last_update
    day = time.strftime("%d")
    if lu != day:
      settings.last_update = day
      from ga import ga
      p = {}
      p['an'] = get_addon_name()
      p['av'] = get_addon_version()
      p['ec'] = 'Addon actions'
      p['ea'] = action
      p['ev'] = '1'
      p['ul'] = get_system_language()
      p['cd'] = location
      ga('UA-79422131-10').update(p, crash)
  except Exception, er:
    log(er)
  
def get_location():
  location = settings.url + settings.mac
  if os.environ.get('TVBGPVRDEBUG'):
    location = os.environ['TVBGPVRDEBUG']
  return location
  
def get_stream_url(name):
  """
  Reads stream list from cache and returns url of the selected stream name
  """
  try:
    # deserialize streams
    # streams = cPickle.load(open(pl_streams))
    streams = json.load(open(pl_streams))
    log("Deserialized %s streams from file %s" % (len(streams), pl_streams))
    return streams.get(name.decode("utf-8"))
  except Exception as er:
    log(er)
    return None
   
## Initialize the addon
pl_name       = 'playlist.m3u'
pl_path       = os.path.join(get_profile_dir(), pl_name)
pl_cache      = os.path.join(get_profile_dir(), ".cache")
pl_streams    = os.path.join(get_profile_dir(), ".streams")
__version__   = get_kodi_build()
VERSION       = int(__version__[0:2])
user_agent    = 'Kodi %s' % __version__
scheduled_run = len(sys.argv) > 1 and sys.argv[1] == str(True)
mapping_file  = os.path.join( get_resources_dir(), 'mapping.json' )
progress_bar  = None

### Literals
RUNSCRIPT     = 'RunScript(%s, True)' % get_addon_id()
GET           = 'GET'
HEAD          = 'HEAD'
NEWLINE       = '\n'
BIND_IP       = '0.0.0.0' if settings.bind_all else '127.0.0.1'
STREAM_URL    = 'http://' + settings.stream_ip + ':' + str(settings.port) + '/staticplaylist.backend/stream/%s'
START_MARKER  = "#EXTM3U"
INFO_MARKER   = "#EXTINF"

### Addon starts
if settings.firstrun:
  settings.open()
  settings.firstrun = False
  
__update__('operation', 'start')