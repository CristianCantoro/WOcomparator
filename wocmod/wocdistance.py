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
from wocglobal import WOC
from wocdb import PostgreSQLConnector

logger = logging.getLogger('woc.wocdistance')
 
class Distance(object):
   
   def __init__(self,item):
      self.item = item
      self.coord_dist = None
      self.intersects = None
   
   def coord_distance(self):      
      if self.coord_dist is None:
         query=""" SELECT 
                   ST_Distance(
                     ST_GeographyFromText('POINT({osm_lon} {osm_lat})'),
                     ST_GeographyFromText('POINT({wikipedia_lon} {wikipedia_lat})')
                   );
               """
         
         query=query.format(osm_lon = self.item.osm_lon,
                            osm_lat = self.item.osm_lat,
                            wikipedia_lon = self.item.wikipedia_lon,
                            wikipedia_lat = self.item.wikipedia_lat
                           )
         #logger.debug(query)
         
         self.coord_dist = -1
         
         geodb = PostgreSQLConnector(WOC['GEODB'])
         geodb.connect()
         res = geodb.query(query)
         geodb.close()
      
         if res:
            if len(res) > 0:
               self.coord_dist = res[0][0]
      
      return self.coord_dist


   def intersection(self):      
      if self.intersects is None:

         if self.item.osm_type == 'point':
            query=""" SELECT 
                      ST_DWithin(
                        ST_GeographyFromText('POINT({osm_lon} {osm_lat})'),
                        ST_GeographyFromText('POINT({wikipedia_lon} {wikipedia_lat})'),
                        20
                      );
                  """
            
            query=query.format(osm_lon = self.item.osm_lon,
                               osm_lat = self.item.osm_lat,
                               wikipedia_lon = self.item.wikipedia_lon,
                               wikipedia_lat = self.item.wikipedia_lat
                              )
         else:
            query=""" SELECT 
                      ST_Contains(
                        osmgeom.way,
                        ST_Transform(ST_GeometryFromText('POINT({wikipedia_lon} {wikipedia_lat})',4326),900913)
                      )
                      FROM (SELECT way
                            FROM planet_osm_{type}
                            WHERE osm_id = {osm_id}
                           ) AS osmgeom;
                  """
#             query=""" SELECT 
#                       ST_Within(
#                         ST_GeometryFromText('POINT({wikipedia_lon} {wikipedia_lat})',4326),
#                         ST_Transform(osmgeom.way,4326)
#                       )
#                       FROM (SELECT way
#                             FROM planet_osm_{type}
#                             WHERE osm_id = {osm_id}
#                            ) AS osmgeom;
#                   """
            query=query.format(wikipedia_lon = self.item.wikipedia_lon,
                               wikipedia_lat = self.item.wikipedia_lat,
                               type = self.item.osm_type,
                               osm_id = self.item.osm_id
                              )
         logger.debug(query)
         
         self.intersects = False
         geodb = PostgreSQLConnector(WOC['GEODB'])
         geodb.connect()
         res = geodb.query(query)
         if len(res) > 0:
            self.intersects = res[0][0]
         geodb.close()
      
      return self.intersects
