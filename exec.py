# -*- coding: utf-8 -*-
import os
import xbmc
import urllib
import xbmcgui
from kodibgcommon.utils import *
from resources.lib.playlist import *
from resources.lib.utils import *

log("Addon running on: %s" % user_agent)
if scheduled_run:
  log(translate(32004))
  
### If addon is started manually or is in debug mode, display the progress bar 
if not scheduled_run or settings.debug:
  progress_bar = xbmcgui.DialogProgressBG()
  progress_bar.create(heading=this.getAddonInfo('name'))

try:
  # Initialize the playlsit object
  pl = Playlist(location=get_location(),
                user_agent=user_agent, 
                progress=progress_bar,
                temp_folder=get_profile_dir())
  
  if pl.count() == 0:
    notify_error(translate(32000))
    
  else:
    ### Replace stream URLs with static ones
    pl.set_static_stream_urls(STREAM_URL)
              
    ### Write playlist to disk
    if not pl.save(path=pl_path):
      notify_error(translate(32001))

    ### Copy playlist to additional folder if specified
    if settings.copy_playlist and os.path.isdir(settings.copy_to_folder):
      pl.save(path=os.path.join(settings.copy_to_folder, pl_name))

except Exception, er:
  log(er, 4)
  log_last_exception()

### Schedule next run
interval = int(settings.run_on_interval) * 60
log(translate(32007) % interval)

AlarmClock('ScheduledRegeneration', RUNSCRIPT, interval)

if progress_bar:
  progress_bar.close()
