# -*- coding: utf8 -*-
import os
import re
import sys
import json
import urllib
import requests
from stream import *
from utils import *

reload(sys)  
sys.setdefaultencoding('utf8')

class Playlist:
  cache_playlist = False
  streams = []
  channels = {}
  disabled_groups = []
  size = 0
  cache_file = ".cache"
  streams_file = ".streams"
  __map = {}
  
  def __init__(self, **kwargs):
    try:
      ## keyword arguments
      self.location = kwargs.get('location')
      if not self.location:
        raise Exception("No m3u location provided")
      self.cache_playlist = kwargs.get('cache_playlist')
      self.progress_callback = kwargs.get('progress')
      self.name = kwargs.get('name', 'playlist.m3u')
      self.include_radios = kwargs.get('include_radios', False)
      self.user_agent = kwargs.get('user_agent')
      self.temp_folder = kwargs.get('temp_folder')
      if self.temp_folder:
        self.cache_file = os.path.join(self.temp_folder, self.cache_file)
        self.streams_file = os.path.join(self.temp_folder, self.streams_file)
      
      self.__load()

      if self.self.cache_playlist:
        self.__serialize()
      
      log("Playlist initialized with %s channels" % self.count())
    except Exception as e:
      log("__init__() " + str(e), 4)
      raise

  def __progress(self, percent, msg):
    if self.progress_callback:
      self.progress_callback.update(percent, str(msg))
    
  def __load(self):
    ''' 
    Loads m3u from given location - local storage or online resource
    '''
    ret = True
    log("__load() started")
    self.__progress(5, "Loading playlist from: %s" % self.location)
    if self.location.startswith("http") or self.location.startswith("ftp"):
      ret = self.__download()
    
    if ret and self.cache_playlist:
      self.__parse()
    
    log("__load() ended")

  def __download(self):
    try:
      headers = {}
      if self.user_agent:
        headers = {"User-agent": self.user_agent}
      log("Downloading resource from: %s " % self.location)
      response = requests.get(self.location, headers=headers)
      log("Server status_code: %s " % response.status_code)
      if response.status_code >= 200 and response.status_code < 400:
        chunk_size = self.__get_chunk_size__(response)
        self.__cache(self.__iter_lines__(response, chunk_size)) #using response.text.splitlines() is way too slow on singleboard devices!!!
      else:
        log("Unsupported status code received from server: %s" % response.status_code)
        return False
      return True
    except Exception, er:
      log(er, 4)
      return False
    
  def __get_chunk_size__(self, response):
    try:
      size = int(response.headers['Content-length'])
      if size > 0: 
        return size/100
    except: pass
    return 2048
  
  def __iter_lines__(self, response, chunk_size, delimiter=None):
    '''
      Implementation of iter_lines to include progress bar
    '''
    pending = None
    for chunk in response.iter_content(chunk_size=chunk_size, decode_unicode=True):
      if pending is not None:
        chunk = pending + chunk
      if delimiter:
        lines = chunk.split(delimiter)
      else:
        lines = chunk.splitlines()
      if lines and lines[-1] and chunk and lines[-1][-1] == chunk[-1]:
        pending = lines.pop()
      else:
        pending = None
      for line in lines:
        yield line
    if pending is not None:
        yield pending

  def __cache(self, content):
    '''
    Saves the m3u locally and counts the lines 
    Needed for the progress bar
    '''
    log("cache() started!")
    self.location = self.cache_file
    with open(self.location, "w") as file:
      for line in content:
        self.size += 1
        file.write("%s\n" % line.rstrip().encode("utf-8"))
    log("cache() ended!")
 
  def __parse(self):
    '''
      Parse m3u file line by line
    '''
    log("parse() started!")
    stream = None
    percent = 10  
    max = 80
    step = round(self.size/max) if self.size > 0 else 16
    with open(self.location, "r") as file_content:
      for i, line in enumerate(file_content):
        if self.size > 0: # if true, we have counted the lines
          if i % step == 0: 
            percent += 1
          self.__progress(percent, "Parsing playlist")
        
        if not line.startswith(START_MARKER):
          line = line.rstrip()
          if line and line.startswith(INFO_MARKER):
            stream = Stream(line)            
          else:
            if not stream:
              continue
            stream.url = line
            self.streams.append(stream)
            stream = None #reset
    log("parse() ended") 
        

  def __serialize(self):
    '''
    Serializes streams dict into a file so it can be used later
    '''
    log("__serialize() started")
    self.__progress(10, "Serializing streams")
    _streams = {}
    for stream in self.streams:
      _streams[stream.name] = stream.url
    log("serializing %s streams in %s" % (len(_streams), self.streams_file))
    with open(self.streams_file, "w") as w:
      w.write(json.dumps(_streams, ensure_ascii=False))
    log("__serialize() ended")

  
  def add(self, new_m3u_location):
    ''' 
    Adds channels from new playlist to current one
    '''
    self.load(new_m3u_location)
  
  def count(self, count_disabled_channels=True):
    if count_disabled_channels:
      return len(self.streams)
    else:
      i = 0
      for stream in self.streams:
        if stream.group not in self.disabled_groups:
          i += 1
      return i

  
  def __to_string(self):
    ''' 
      Outputs the current streams into different formats
    '''
    log("__to_string() started!")
    self.__progress(98, "Saving playlist.")  
    buffer = ""
    percent = 0
    n = len(self.streams)
    for i in range(0, n):
      stream_string = self.streams[i].to_string()
      buffer += stream_string
      buffer = "%s\n%s" % (START_MARKER, buffer)
    
    log("__to_string() returned %s streams" % n)
    return buffer.encode("utf-8", "replace")
    
 
  def save(self, **kwargs):   
    # If no path is provided overwite current file
    file_path = kwargs.get('path', self.cache_file)
      
    try:
      with open(file_path, 'w') as file:
        log("Saving playlist in %s " % file_path)
        file.write(self.__to_string())
      return True
    
    except Exception, er:
      log(er, 4)
      return False

  def set_static_stream_urls(self, url):
    '''
    Replaces all stream urls with static ones
    That point to our proxy server
    '''
    for stream in self.streams:
      name = urllib.quote(stream.name.encode("utf-8"))
      stream.url = url % (name)
  

  def get_stream_url(self, name):
    """
    Reads stream list from cache and returns url of the selected stream name
    """
    try:
      name = name.decode("utf-8")
      
      if self.cache_playlist:
        streams = json.load(open(self.streams_file))
        log("Deserialized %s streams from file %s" % (len(streams), self.streams_file))
        return streams.get(name)
        
      else:
        with open(self.location) as file:
          found = False
          
          for line.rstrip() in file:
            if found:
              log("Stream url: %s" % line)
              return line
              
            pattern = ",\s*%s$" % name
            match = re.compile(pattern).findall(line)
            if len(match) > 0:
              log("Found url for stream %s" % name)
              found = True
          log("Stream url not found for %s" % name)    
          return None
          
    except Exception as er:
      log(er)
      return None