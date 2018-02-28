# -*- coding: utf8 -*-
import re
import json
from utils import *

class Stream:
  
  def __init__(self, line):
    try:
      self.name = re.compile(',(?:\d+\.)*\s*(.*)').findall(self.line)[0].rstrip()
    except:
      log("Stream name could not be extracted. Failing!")
      return None
      
    try: 
      self.id = re.compile('tvg-id[="\']+(.*?)[\'"\s]+').findall(self.line)[0]
      log("Extracted stream id '%s'" % self.id)
      if not id or id == "":
        log("Empty id, using stream name as id '%s'" % self.name)
        self.id = self.name
    except: 
      self.id = self.name
    
    try: 
      self.group = re.compile('group-title[="\']+(.*?)["\'\s]+').findall(self.line)[0]
      log("Stream group set to '%s'" % self.group)
    except: 
      self.group = None
    
    try: 
      self.logo = re.compile('logo[="\']+(.*?)["\'\s]+').findall(self.line)[0]
      log("Extracted stream logo '%s'" % self.logo)
    except: 
      self.logo = None
    
    try: 
      self.shift = re.compile('shift[=\"\']+(.*?)["\'\s]+').findall(self.line)[0]
    except: 
      self.shift = None    

    try: 
      self.is_radio = re.compile('radio[=\"\']+T|true["\'\s]+').findall(self.line) > 0
    except: 
      self.is_radio = False

  def to_string(self):    
    buffer = '%s:-1' % INFO_MARKER
    if self.is_radio:
      buffer += ' radio="%s"' % self.is_radio
    if self.shift:
      buffer += ' tvg-shift="%s"' % self.shift
    if self.group:
      buffer += ' group-title="%s"' % self.group
    if self.logo:
      buffer += ' tvg-logo="%s"' % self.logo
    if self.id:
      buffer += ' tvg-id="%s"' % self.id
    
    buffer += ',%s\n' % self.name
    buffer += '%s\n' % self.url

    return buffer
  
  
  def to_json(self):
    '''
      Outputs the stream object into a JSON formatted string
    '''
    #return json.dumps({"name": self.name, "id": self.id, "url": self.url, "logo": self.logo, "group": self.group, "is_radio": self.is_radio, "shift": self.shift, "order": self.order, "quality": self.quality}, ensure_ascii=False).encode('utf8')
    return json.dumps({"name": self.name, "id": self.id}, ensure_ascii=False).encode('utf8')