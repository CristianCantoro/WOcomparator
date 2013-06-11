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


import MySQLdb as mdb
import psycopg2

import logging
logger = logging.getLogger('woc.wocdb')


class MySQLConnector(object):

   def __init__(self,par):
      assert par['DBMS'] == 'mysql'

      self.host = par['HOST']
      self.user = par['USER']
      self.password = par['PASSWORD']
      self.dbname =  par['DBNAME']
      self.con = None
      
   def connect(self):
      try:
         #con = mdb.connect('localhost', 'woc', 'woc', 'coordsit');
         self.con = mdb.connect(self.host,
                                self.user,
                                self.password,
                                self.dbname
                               );
      except mdb.Error, e:
         logger.error("Error %d: %s" % (e.args[0],e.args[1]))
   
   def query(self,query):
      res = None
      try:
         cur = self.con.cursor()
         cur.execute(query)
         res = cur.fetchall()
      except Exception as e:
         logger.error("Error executing: {query}".format(query=query))
         logger.error("Error: {e}".format(e=e))
   
      return res

   def close(self):
      if self.con:
         self.con.close()

class PostgreSQLConnector(object):

   def __init__(self,par):
      assert par['DBMS'] == 'postgresql'
       
      self.host = par['HOST']
      self.user = par['USER']
      self.password = par['PASSWORD']
      self.dbname =  par['DBNAME']
      
      self.con = None

   def connect(self):
      conn_params ='{dbms}://{user}:{password}@{host}/{dbname}'.format(
                   dbms='postgresql',
                   user=self.user,
                   password=self.password,
                   host=self.host,
                   dbname=self.dbname
                  )
      self.con = psycopg2.connect(conn_params)
   
   def close(self):
      if self.con:
         self.con.close()
   
   def query(self,query):
      res = None
      try:
         cur = self.con.cursor()
         cur.execute(query)
         res = cur.fetchall()
      except Exception as e:
         logger.error("Error executing: {query}".format(query=query))
         logger.error("Error: {e}".format(e=e))
   
      return res
   
# cur = con.cursor()
# cur.execute("SELECT gc_from,gc_lat,gc_lon,gc_name FROM coord_itwiki WHERE gc_name LIKE '%Abbazia%'")
# 
# res = cur.fetchall()

#    @ConnectionManager
#    def query_db(lat,lon,name,con=None,cur=None):
#       res=None
#       try:
#          query="""
#                SELECT 
#                   osm_id,ST_AsText(ST_Transform(way,4326)),name,amenity,admin_level,tags
#                FROM 
#                   planet_osm_point
#                WHERE
#                   ST_Dwithin(ST_GeographyFromText('POINT({lon} {lat})'),
#                              ST_Transform(way,4326),
#                              10000) 
#                AND 
#                   name ILIKE '{name}';
#                """
#          query=query.format(lon=lon,lat=lat,name=name)
#          logger.debug(query)
#          cur.execute(query)
#          res=cur.fetchall()
#       except Exception as e:
#          print "Error: {err}".format(err=e)
#    
#       return res
   
   
if __name__ == '__main__':
   # ----- imports -----
   import sys
   sys.path.append('../')
   from wocglobal import WOC
   
   # ----- logger -----
   rootlogger = logging.getLogger('woc.wocdb')
   rootlogger.setLevel(logging.DEBUG)

   lvl_config_logger = logging.DEBUG

   console = logging.StreamHandler()
   console.setLevel(lvl_config_logger)

   rootlogger.addHandler(console)
   # ----- -----
   
   # ----- start test -----
   coordsdb = MySQLConnector(WOC['COORDSDB'])
   coordsdb.connect()
   res = coordsdb.query('SELECT VERSION()')
   logger.debug(res)
   
   geodb = PostgreSQLConnector(WOC['GEODB'])
   geodb.connect()
   res = geodb.query('SELECT VERSION()')
   logger.debug(res)
   