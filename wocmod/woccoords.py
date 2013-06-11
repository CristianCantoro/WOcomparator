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

import logging
from wocmod.wocurlbuilder import UrlBuilder
from wocmod.wocjson import JSONQuerier
from wocmod.wocdb import MySQLConnector,PostgreSQLConnector
from wocmod.wocglobal import WOC

logger = logging.getLogger('woc.woccoords')

_jsonu = UrlBuilder(
               domain="json.it.dbpedia.org",
               path="annotate/resource/json/it%3A{wppage}",
               params="filter=__type:template"
              )
_jsonu.set_attr('flags','-Extractors,Structure,')
JSONPEDIABASEURL=_jsonu.build()


class CoordinateGetter(object):

   def __init__(self,item):
      self.item = item
      self.coords = None
   
   def _from_db(self):
      pass   

   def _from_page(self):
      pass

   def get_coords(self):
      self._from_db()
      self._from_page()
      return self.coords

class WikipediaCoordinateGetter(CoordinateGetter):
   
   def __init__(self,item):
      self.item = item
      self.coords = None
      
   def _from_db(self):
      
      if not self.coords:
         wikipage = self.item.wikipedia_page.replace('_',' ')
         logger.debug(wikipage)
         wikipage = wikipage.replace("'","\\'")
         coordsdb = MySQLConnector(WOC['COORDSDB'])
         coordsdb.connect()
         query = """SELECT gc_from,gc_lat,gc_lon
                 FROM coord_itwiki 
                 WHERE gc_name LIKE '{wikiname}'
               """.format(wikiname=wikipage)
         logger.debug(query)
         res = coordsdb.query(query)
         logger.debug(res)
         coordsdb.close()
         
         if not (res is None) and len(res) != 0:
            lat=res[0][1]
            lon=res[0][2]
            self.coords = (lat,lon)
   
   def _extract_data_coord(self,template):
      logger.debug(template)
      
      coord={'lat': '', 'lon': ''}
      optionalpars= [u'dim:', u'globe:',u'region:',u'scale:',u'source:',u'type:']
      
      todel=set()
      for k,v in template.iteritems():
         for op in optionalpars:
            if op in v[0]:
               todel.add(k)
               break
      
      for k in todel:
         del template[k]
      
      anonpars=[tpar for tpar in template.keys() if '__anon_' in tpar]
      for ap in anonpars:
         template[int(ap.strip('__anon_'))]=template[ap][0]
         del template[ap]
      
      parsnums=[int(p.strip('__anon_')) for p in anonpars]
      parcount=len(anonpars)
      startpar=min(parsnums)
      stoppar=max(parsnums)
      
      gglat=float(template[startpar])
      mmlat=0
      sslat=0
      gglon=0
      mmlon=0
      sslon=0
      dirlat=''
      dirlon=''
      if parcount == 2:
         gglon=float(template[startpar+1])
      elif parcount == 4:
         dirlat=str(template[startpar+1])
         gglon=float(template[startpar+2])
         dirlon=str(template[startpar+3])
      elif parcount == 6:
         mmlat=float(template[startpar+1])
         dirlat=str(template[startpar+2])
         gglon=float(template[startpar+3])
         mmlon=float(template[startpar+4])
         dirlon=str(template[startpar+5])
      elif parcount == 8:
         mmlat=float(template[startpar+1])
         sslat=float(template[startpar+2])
         dirlat=str(template[startpar+3])
         gglon=float(template[startpar+4])
         mmlon=float(template[startpar+5])
         sslon=float(template[startpar+6])
         dirlon=str(template[startpar+7])
      
      deglat=float(gglat)+float(mmlat)/60.0+float(sslat)/3600.0
      deglon=float(gglon)+float(mmlon)/60.0+float(sslon)/3600.0
      
      if dirlat == "S":
         deglat =-deglat
      if dirlon == "W":
         deglon =-deglon
   
      coord['lat']=str(deglat)
      coord['lon']=str(deglon)
      return coord
   
   def _from_page(self):
      jsonurl = JSONPEDIABASEURL.format(wppage=self.item.wikipedia_page)
      jsonquery = JSONQuerier(jsonurl)
      jobj = jsonquery.get_jobj()
      
      if jobj is None:
         return
      # process templates
      for template in jobj['result']:
         if template['name'].lower() == 'coord':
            try:
               row = self._extract_data_coord(template['content'])
               logger.debug(row)
               if row['lat'] != '' and row['lon'] != '':
                  self.coords = (row['lat'],row['lon'])
            except Exception as e:
               print "Caught exception %s" %e
               print "Template content:"
               print template['content']
               continue
      
class OSMCoordinateGetter(CoordinateGetter):
   
   def __init__(self,item):
      self.item = item
      self.coords = None
      
   def _from_db(self):
      
      if not self.coords:
         geodb = PostgreSQLConnector(WOC['GEODB'])
         geodb.connect()
         query = """SELECT 
                       centr_x AS x,
                       centr_y AS y  
                    FROM planet_osm_{type}
                    WHERE osm_id = {osm_id}
               """.format(type=self.item.osm_type,
                          osm_id=self.item.osm_id)
         logger.debug(query)
         res = geodb.query(query)
         logger.debug(res)
         geodb.close()
         
         if not (res is None) and len(res) != 0:
            lat=res[0][1]
            lon=res[0][0]
            self.coords = (lat,lon)

   def get_coords(self):
      self._from_db()
      self._from_page()
      return self.coords
   