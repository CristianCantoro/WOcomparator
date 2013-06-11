#!/usr/bin/python
# -*- coding: utf-8  -*-
#########################################################################
# Copyright (C) 2012 Cristian Consonni <cristian.consonni@gmail.com>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (see COPYING).
# If not, see <http://www.gnu.org/licenses/>.
#########################################################################

# ***** logging module objects and definition *****
import logging

LOGFORMAT_STDOUT = { logging.DEBUG: '%(module)s:%(funcName)s:%(lineno)s - %(levelname)-8s: %(message)s',
             logging.INFO: '%(levelname)-8s: %(message)s',
             logging.WARNING: '%(levelname)-8s: %(message)s',
             logging.ERROR: '%(levelname)-8s: %(message)s',
             logging.CRITICAL: '%(levelname)-8s: %(message)s'
           }

LOGFORMAT_FILE = { logging.DEBUG: "%(module)s:%(funcName)s:%(lineno)s - ***%(levelname)s***: %(message)s",
           logging.INFO: "%(asctime)s ***%(levelname)s***: %(message)s",
           logging.WARNING: "%(asctime)s ***%(levelname)s***: [%(module)s:%(funcName)s] %(message)s",
           logging.ERROR: "%(asctime)s *****%(levelname)s*****: ***[%(module)s:%(funcName)s:%(lineno)s]*** ***%(message)s***",
           logging.CRITICAL: "%(asctime)s *****%(levelname)s*****: ***[%(module)s:%(funcName)s:%(lineno)s]*** ***%(message)s***"
         }

LOGDATEFMT = '%Y-%m-%d %H:%M:%S'

class NullHandler(logging.Handler):
   def emit(self, record):
      pass

class Formattatore(logging.Formatter):
   def format(self, record):
      self._fmt=LOGFORMAT_FILE[record.levelno]
      s = logging.Formatter.format(self,record)
      return s

# ***** END logging module *****

# ***** system imports *****
import os
import urllib

# ***** START *****
from wocmod import wocconfig as config
from wocmod.wocglobal import WOC
from wocmod.wocurlbuilder import UrlBuilder
from wocmod.wocquery import DBpediaTypeQuerier,NominatimPlaceQuerier
from wocmod.wocdb import PostgreSQLConnector
from wocmod.wocunicode import UnicodeWriter,UnicodeReader
from wocmod.wocitem import OSMItem,WikipediaItem,WOItem
from wocmod.woccoords import WikipediaCoordinateGetter,OSMCoordinateGetter
from wocmod.wocdistance import Distance
from wocmod.wocwiki import WikipediaGetter
from wocmod.wocstats import OItemStatistics,WItemStatistics

# ***** utility functions *****

# --- root logger
rootlogger = logging.getLogger('woc')
rootlogger.setLevel(logging.DEBUG)

lvl_config_logger = logging.INFO
#lvl_config_logger = logging.DEBUG

console = logging.StreamHandler()
console.setLevel(lvl_config_logger)

formatter = logging.Formatter(LOGFORMAT_STDOUT[lvl_config_logger])
console.setFormatter(formatter)

rootlogger.addHandler(console)

logger = logging.getLogger('woc.main')

cfgcli = config.parse()
  
BASE_DIR = WOC['BASE_DIR']
CURR_DIR = os.path.abspath(os.path.normpath(os.getcwd()))
verbose = cfgcli['verbose']
debug = cfgcli['debug']

manual = cfgcli['manual']
if manual:
   verbose=True
   logger.info("--manual set - activating verbose")

if verbose or debug:
   if debug: 
      lvl = logging.DEBUG
   else: 
      lvl = logging.INFO
   formatter = logging.Formatter(LOGFORMAT_STDOUT[lvl])
   console.setFormatter(formatter)
   console.setLevel(lvl)
else:
   h = NullHandler()
   console.setLevel(logging.WARNING)
   rootlogger.addHandler(h)

logger.info("BASE_DIR: %s" %BASE_DIR)
logger.info("CURR_DIR: %s" %CURR_DIR)
# ***** *****

# ***** OSM2Wiki *****
geodb = PostgreSQLConnector(WOC['GEODB'])

osmres = list()
try:
   osm_input = open('osm_query.txt','r')
   osmlist = osm_input.readlines()
   osmlist = [tuple(line.strip().split(',')) for line in osmlist] 
except:
   osm_input = None

if not osm_input:
   geodb.connect()
   query="""SELECT osm_id, name, tags -> 'wikipedia' AS "wikipedia", 'point' AS "type"
               FROM planet_osm_point 
               WHERE (tags ? 'wikipedia')  AND ((amenity = 'place_of_worship') OR (building = 'church')
               OR (building = 'cathedral') OR (building = 'chapel'))
               UNION
               SELECT osm_id, name, tags -> 'wikipedia' AS "wikipedia",'line' AS "type" 
               FROM planet_osm_line 
               WHERE (tags ? 'wikipedia')  AND ((amenity = 'place_of_worship') OR (building = 'church')
               OR (building = 'cathedral') OR (building = 'chapel'))
               UNION
               SELECT osm_id, name, tags -> 'wikipedia' AS "wikipedia", 'polygon' AS "type"
               FROM planet_osm_polygon 
               WHERE (tags ? 'wikipedia')  AND ((amenity = 'place_of_worship') OR (building = 'church')
               OR (building = 'cathedral') OR (building = 'chapel'))
               UNION
               SELECT osm_id, name, tags -> 'wikipedia' AS "wikipedia", 'roads' AS "type"
               FROM planet_osm_roads 
               WHERE (tags ? 'wikipedia')  AND ((amenity = 'place_of_worship') OR (building = 'church')
               OR (building = 'cathedral') OR (building = 'chapel'))
         """
   res = geodb.query(query)
   geodb.close()

HEADER = ['pagename',
          'osm_id',
          'osm_type',
          'osm_lon',
          'osm_lat',
          'wiki_lon',
          'wiki_lat',
          'distance',
          'intersects'
         ]

NOWIKI_HEADER = ['pagename',
                 'osm_id',
                 'osm_type',
                 'osm_lon',
                 'osm_lat'
                 ]

osm2wiki_outfile = open('osm2wiki_distances.txt','w+')
osm2wiki_outcsv = UnicodeWriter(osm2wiki_outfile)
osm2wiki_outcsv.writerow(HEADER)

nowiki_outfile = open('osm_nowiki.txt','w+')
nowiki_outcsv = UnicodeWriter(nowiki_outfile)
nowiki_outcsv.writerow(NOWIKI_HEADER)

wiki2osm_outfile = open('wiki2osm_distances.txt','w+')
wiki2osm_outcsv = UnicodeWriter(wiki2osm_outfile)
wiki2osm_outcsv.writerow(HEADER)


wiki2osm_infile = open('edifici_religiosi_out.csv','r')
wikilist = list(UnicodeReader(wiki2osm_infile,
                                     delimiter='|',
                                     quotechar='"'))

wikilist_header = wikilist.pop(0)
logger.debug(wikilist_header)

oitem_stats = OItemStatistics()
OSMitems = list()
for osmitem in osmlist:

   logger.info('==========')
   logger.info(osmitem) 

   osm_id = osmitem[0]
   osm_name = osmitem[1]
   osm_wiki = osmitem[2]
   osm_type = osmitem[3]
   
   #logger.debug(osm_id,osm_name,osm_wiki,osm_type)
   oitem = OSMItem(osm_id,osm_name,osm_wiki,osm_type)
   oitem.get_wikipedia_link()
   oitem.get_wikipedia_page()
   
   wg = WikipediaGetter(oitem=oitem)
   wikipedia_id = wg.get_id()
   wikipedia_link = wg.get_link()
   wikipedia_page = wg.get_page()
   
   oitem.set_wikipedia_properties(wikipedia_id=wikipedia_id, 
                                  wikipedia_page=wikipedia_page, 
                                  wikipedia_link=wikipedia_link)
   
   logger.debug(oitem.wikipedia_lang)

   if oitem.wikipedia_lang != 'it':
      logger.info('Skipping items not from it.wiki - Skipping ...')
      continue

   logger.debug('Getting coordinates from Wikipedia')
   wpcg = WikipediaCoordinateGetter(oitem)
   wpcoords = wpcg.get_coords()
   
   logger.debug('Getting coordinates from OSM')
   osmcg = OSMCoordinateGetter(oitem)
   osmcoords = osmcg.get_coords()
   
   logger.debug('Setting OSM coordinates')
   oitem.set_osm_coords(osmcoords,bbox=oitem.osm_bbox)
   
   if wpcoords is None:
      logger.info('No coordinates from Wikipedia - Skipping ...')
      row = [ oitem.wikipedia_page,
              oitem.osm_id,
              oitem.osm_type,
              oitem.osm_lon,
              oitem.osm_lat
            ]
      nowiki_outcsv.writerow(row)
      continue
   
   logger.debug('Setting Wikipedia coordinates')
   oitem.set_wikipedia_coords(wpcoords)
   
   logger.debug('Calculating distance')
   dist = Distance(oitem)
   distance = dist.coord_distance()
   logger.debug(distance) 

   inters = dist.intersection()
   logger.debug(inters)
   
   row = [oitem.wikipedia_page,
          oitem.osm_id,
          oitem.osm_type,
          oitem.osm_lon,
          oitem.osm_lat,
          oitem.wikipedia_lon,
          oitem.wikipedia_lat,
          distance,
          inters
         ]
   logger.info(row)
   osm2wiki_outcsv.writerow(row)

   oitem_stats.analyze(oitem)

   OSMitems.append(oitem)


# ***** Wiki2OSM *****
wiki_stats = WItemStatistics()
WIKIPEDIAURL = 'it.wikipedia.org'
Wikiitems = list()
wikilist=()
for wikiitem in wikilist:
   
   logger.info('==========')
   logger.info(wikiitem) 

   wikipedia_page = wikiitem[1].encode('utf-8')
   wikipedia_lang='it'
   wikipedia_id = WikipediaGetter(wikipedia_page=wikipedia_page,
                                  wikipedia_lang=wikipedia_lang)
   wikipedia_link = UrlBuilder(domain=WIKIPEDIAURL,
                               path='wiki/{pagename}'.format(pagename=wikipedia_page)).build()
   wikipedia_coords = (wikiitem[22],wikiitem[23])
   wikipedia_lat = wikiitem[22]
   wikipedia_lon = wikiitem[23]
   
   
   
   witem = WikipediaItem(wikipedia_id=wikipedia_id,
                 wikipedia_page=wikipedia_page,
                 wikipedia_lang='it',
                 wikipedia_link=wikipedia_link,
                 wikipedia_coords=wikipedia_coords,
                 wikipedia_lat=wikipedia_lat,
                 wikipedia_lon=wikipedia_lon)

#    dbquery = DBpediaTypeQuerier(oitem.wikipedia_page)
#    dbjobj = dbquery.get_json()
#  
#    if (dbjobj is None) or len(dbjobj) == 0:
#       logger.info('No info from DBpedia - Skipping ...')
#       continue
#     
#    #logger.debug(dbjobj)
#    #logger.debug(dbjobj['results']['bindings'])
#  
   urlpagename=urllib.quote(witem.wikipedia_page.replace('_',' '))
   nomquery = NominatimPlaceQuerier(urlpagename)
   nomjobj = nomquery.get_json()
     
   if (nomjobj is None) or len(nomjobj) == 0:
      logger.info('No info from Nominatim - Skipping ...')
      continue
   
   logger.debug(nomjobj)
   osm_name = nomjobj[0]['display_name']
   osm_id = nomjobj[0]['osm_id']
   osm_lon = nomjobj[0]['lon']
   osm_lat = nomjobj[0]['lat']
   osm_bbox = nomjobj[0]['boundingbox']
   osm_type = nomjobj[0]['osm_type']
   
   witem.set_osm_properties(osm_id=osm_id,
                            osm_name=osm_name,
                            osm_type=osm_type,
                            osm_lat=osm_lat,
                            osm_lon=osm_lon,
                            osm_bbox=osm_bbox,
                            osm_coords =(osm_lat,osm_lon))
   
   dist = Distance(witem)
   geores = dist.coord_distance() 
   logger.debug(geores)

   if (geores is not None) and len(geores) > 0:
      distance = geores[0][0]
      row = [witem.wikipedia_page,
             witem.osm_id,
             witem.osm_type,
             witem.osm_lon,
             witem.osm_lat,
             witem.wikipedia_lon,
             witem.wikipedia_lat,
             distance
            ]
      logger.info(row)
      wiki2osm_outcsv.writerow(row)

   Wikiitems.append(witem)

geodb.close()
logger.debug("Finishing ...")