#! /usr/bin/python
# -*- coding: UTF-8 -*-

import logging
import re
import urllib

from wocurlbuilder import UrlBuilder

logger = logging.getLogger('woc.wocitem')

WIKIPEDIAURL='{lang}.wikipedia.org'
HTTPREGEX = re.compile("http(s)?\:")
LANGREGEX = re.compile("[a-z]{2,3}\:")
LANGURLREGEX = re.compile("http(s)?\://[a-z]{2}\.")

class MissingInformation(Exception):
   pass


class Item(object):

   def __init__(self,
                osm_name=None,
                osm_type=None,
                osm_wikipedia_tag=None,
                osm_lat=None,
                osm_lon=None,
                osm_bbox=None,
                wikipedia_page=None,
                wikipedia_link=None,
                wikipedia_coords=None,
                wikipedia_lat=None,
                wikipedia_lon=None):
   
      self.osm_name = osm_name
      self.osm_type = osm_type
      self.osm_wikipedia_tag = osm_wikipedia_tag
      self.osm_lat = osm_lat
      self.osm_lon = osm_lon
      self.osm_bbox = osm_bbox
      
      self.wikipedia_page = wikipedia_page
      self.wikipedia_link = wikipedia_link
      self.wikipedia_coords = wikipedia_coords
      self.wikipedia_lat = wikipedia_lat
      self.wikipedia_lon = wikipedia_lon

   def set_wikipedia_properties(self,
                                wikipedia_id=None,
                                wikipedia_page=None,
                                wikipedia_link=None,
                                wikipedia_coords=None,
                                wikipedia_lat=None,
                                wikipedia_lon=None):
   
      self.wikipedia_id = wikipedia_id
      self.wikipedia_page = wikipedia_page
      self.wikipedia_link = wikipedia_link
      self.wikipedia_coords = wikipedia_coords
      self.wikipedia_lat = wikipedia_lat
      self.wikipedia_lon = wikipedia_lon

   def set_osm_properties(self,
                          osm_id=None,
                          osm_name=None,
                          osm_type=None,
                          osm_wikipedia_tag=None,
                          osm_lat=None,
                          osm_lon=None,
                          osm_bbox=None,
                          osm_coords = None):
   
      self.osm_id = osm_id
      self.osm_name = osm_name
      self.osm_type = osm_type
      self.osm_wikipedia_tag = osm_wikipedia_tag
      self.osm_lat = osm_lat
      self.osm_lon = osm_lon
      self.osm_bbox = osm_bbox

   def set_wikipedia_coords(self,coords):
      self.wikipedia_coords=coords
      self.wikipedia_lat = coords[0]
      self.wikipedia_lon = coords[1]

   def set_osm_coords(self,coords,bbox=None):
      self.osm_coords = coords
      self.osm_lat = coords[0]
      self.osm_lon = coords[1]

      if bbox is not None:
         self.osm_bbox = bbox



class WOItem(Item):

   def __init__(self,osm_item=None, wikipedia_item=None):
      self.osm = osm_item
      self.wikipedia = wikipedia_item
      
   def __repr__(self):
      osm_repr = "(osm_id: {osm_id})".format(
                   osm_id=self.osm_id)
      
      wikipedia_repr = "(wikipedia_id: {wikipedia_id})".format(
                         wikipedia_id=self.wikipedia_id)
      
      return "WOItem<{osm_repr},{wikipedia_repr}>".format(
              osm_repr=osm_repr,
              wikipedia_repr=wikipedia_repr)

   def __str__(self):
      osm_str = "(osm: {osm_name}, {osm_id})".format(
                   osm_id=self.osm_id)
      
      wikipedia_str = "(wikipedia: {wikipedia_page}, {wikipedia_id})".format(
                         wikipedia_page=self.wikipedia_page,
                         wikipedia_id=self.wikipedia_id)

      return "WOItem<{osm_str},{wikipedia_str}>".format(
              osm_str=osm_str,
              wikipedia_str=wikipedia_str)


class OSMItem(Item):
   def __init__(self,osm_id,
                osm_name=None,
                osm_wikipedia_tag=None,
                osm_type = None,
                osm_lat=None,
                osm_lon=None,
                osm_bbox=None,
                osm_coords = None):

      self.osm_id = osm_id
      self.osm_name = osm_name
      self.osm_wikipedia_tag = osm_wikipedia_tag
      self.osm_type = osm_type
      self.osm_lat = osm_lat
      self.osm_lon = osm_lon
      self.osm_bbox = osm_bbox      

      self.wikipedia_id = None
      self.wikipedia_page = None
      self.wikipedia_lang = None
      self.wikipedia_link = None
      self.wikipedia_coords = None
      self.wikipedia_lat = None
      self.wikipedia_lon = None
      
   def __repr__(self):
      osm_repr = "(osm_id: {osm_id})".format(
                   osm_id=self.osm_id)
            
      return "OSMItem<{osm_repr}>".format(
              osm_repr=osm_repr)

   def __str__(self):
      osm_str = "(osm: {osm_name}, {osm_id})".format(
                   osm_id=self.osm_id)
      
      return "OSMItem<{osm_str}>".format(
              osm_str=osm_str)

   def get_wikipedia_page(self):
      logger.debug(self.wikipedia_page)
      if self.wikipedia_page is None:
         logger.debug(self.osm_wikipedia_tag)
         if HTTPREGEX.search(self.osm_wikipedia_tag):
            logger.debug(self.osm_wikipedia_tag)
            urlsplit = self.osm_wikipedia_tag.split('/')
            self.wikipedia_page = urlsplit[-1]
            
            match=LANGURLREGEX.search(self.osm_wikipedia_tag)
            logger.debug(match)
            if match:
               end=match.end()
               self.wikipedia_lang = self.osm_wikipedia_tag[end-3:end-1]
         else:
            match = LANGREGEX.search(self.osm_wikipedia_tag)
            if match:
               start=match.start()
               end=match.end()
               self.wikipedia_page = self.osm_wikipedia_tag[end:]
               self.wikipedia_lang = self.osm_wikipedia_tag[start:end-1]
         
         self.wikipedia_page = self.wikipedia_page.replace(' ','_')
   
         logger.debug(self.wikipedia_page)
         logger.debug(self.wikipedia_lang)
         
         assert self.wikipedia_page
         assert self.wikipedia_lang
      
      return self.wikipedia_page
   
   def get_wikipedia_link(self):
      if self.wikipedia_page is None:
         self.get_wikipedia_page()
      urlpagename = urllib.quote(self.wikipedia_page)
      wikipediaurl = UrlBuilder(
                        domain=WIKIPEDIAURL.format(lang=self.wikipedia_lang),
                        path="wiki/{pagename}".format(pagename=urlpagename)
                     )
      wikiurl=wikipediaurl.build()
      logger.debug(wikiurl)
      
      self.wikipedia_link = wikiurl
      return self.wikipedia_link

           
class WikipediaItem(Item): 
   def __init__(self,wikipedia_id,
               wikipedia_page=None,
               wikipedia_lang=None,
               wikipedia_link=None,
               wikipedia_coords=None,
               wikipedia_lat=None,
               wikipedia_lon=None):

      self.wikipedia_id = wikipedia_id
      self.wikipedia_page = wikipedia_page
      self.wikipedia_lang = wikipedia_lang
      self.wikipedia_link = wikipedia_link
      self.wikipedia_coords = wikipedia_coords
      self.wikipedia_lat = wikipedia_lat
      self.wikipedia_lon = wikipedia_lon

      self.osm_id = None
      self.osm_name = None
      self.osm_wikipedia_tag = None
      self.osm_lat = None
      self.osm_lon = None
      self.osm_bbox = None    
      
   def __repr__(self):
      osm_repr = "(osm_id: {osm_id})".format(
                   osm_id=self.osm_id)
      
      wikipedia_repr = "(wikipedia_id: {wikipedia_id})".format(
                         wikipedia_id=self.wikipedia_id)
      
      return "WikipediaItem<{osm_repr},{wikipedia_repr}>".format(
              osm_repr=osm_repr,
              wikipedia_repr=wikipedia_repr)

   def __str__(self):
      osm_str = "(osm: {osm_name}, {osm_id})".format(
                   osm_id=self.osm_id)
      
      wikipedia_str = "(wikipedia: {wikipedia_page}, {wikipedia_id})".format(
                         wikipedia_page=self.wikipedia_page,
                         wikipedia_id=self.wikipedia_id)

      return "WikipediaItem<{osm_str},{wikipedia_str}>".format(
              osm_str=osm_str,
              wikipedia_str=wikipedia_str)
      



if __name__ == '__main__':
   # ----- imports -----
   import sys
   sys.path.append('../')
   
   # ----- logger -----
   rootlogger = logging.getLogger('woc.wocitem')
   rootlogger.setLevel(logging.DEBUG)

   lvl_config_logger = logging.DEBUG

   console = logging.StreamHandler()
   console.setLevel(lvl_config_logger)

   rootlogger.addHandler(console)
   # ----- -----
   
   logger.debug('test')
   oitem = OSMItem(62505610,
                   osm_name="Mantova",
                   osm_wikipedia_tag="it:Mantova")
   oitem.get_wikipedia_link()
   oitem.get_wikipedia_page()

   oitem = OSMItem(256212396,
                   osm_name="Sant'Antonio Mantovano",
                   osm_wikipedia_tag="it:Stazione di Sant'Antonio Mantovano")
   oitem.get_wikipedia_link()
   oitem.get_wikipedia_page()
   
   oitem = OSMItem(731422324,
                   osm_name="Punta Ala",
                   osm_wikipedia_tag="http://it.wikipedia.org/wiki/Punta_Ala")
   oitem.get_wikipedia_link()
   oitem.get_wikipedia_page()


