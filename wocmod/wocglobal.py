#!/usr/bin/python
# -*- coding: utf-8  -*-
#########################################################################
# Copyright (C) 2013 Cristian Consonni <cristian.consonni@gmail.com>.
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
import os
import sys
import logging

from wocmod import woctuct as tuct

logger = logging.getLogger('sogbot.sbglobal')

# ***** application (meta)data *****
APPNAME = 'WOcomparator'

VERSION = '0.1'

BASE_DIR = os.path.dirname(os.path.normpath(os.path.realpath(sys.argv[0])))

CURR_DIR = os.path.abspath(os.path.normpath(os.getcwd()))

logger.debug("BASE_DIR: %s" %BASE_DIR)
logger.debug("CURR_DIR: %s" %CURR_DIR)

CONFIGSPECNAME = 'sogbot.spec.cfg'

CONFIGSPEC_DIR = os.path.join(BASE_DIR,'config/spec/')

CONFIGSPECFILE = os.path.join(CONFIGSPEC_DIR,CONFIGSPECNAME)

CONFIG_DIR = os.path.join(BASE_DIR,'config/')

CONFIGNAME = 'sogbot.cfg'

CONFIGFILE = os.path.join(CONFIG_DIR,CONFIGNAME)

DESCRIPTION="""WOcomparator description"""

EPILOG = """Copyright 2013 - Cristian Consonni.
This program is free software; you may redistribute it under the terms of
the GNU General Public License version 3 or (at your option) any later version. 
This program has absolutely no warranty."""

COORDSDB = {
            'DBMS': 'mysql',
            'HOST': "localhost",
            'DBNAME': "coordsit",
            'USER': "woc",
            'PASSWORD': "woc"
           }

GEODB = {
         'DBMS': 'postgresql',
         'HOST': "localhost",
         'DBNAME': "italy",
         'USER': "gis",
         'PASSWORD': "gis"
        }

# CONN_PARAMS = "host='{host}' ".format(host=HOST)
# CONN_PARAMS += "dbname='{dbname}' ".format(dbname=DBNAME)
# CONN_PARAMS += "user='{user}' ".format(user=USER)
# CONN_PARAMS += "password='{password}' ".format(password=PASSWORD)
# 
# ENGINE='{dbms}://{user}:{password}@{host}/{dbname}'.format(dbms=DBMS,
#                                                            user=USER,
#                                                            password=PASSWORD,
#                                                            host=HOST,
#                                                            dbname=DBNAME)

# ITALYBBOX = {'minlon': 6.527650,
#              'minlat': 35.532933,
#              'maxlon': 18.471650,
#              'maxlat': 47.059967             
#              }

IBBOXLAT = (35.532933,47.059967)
IBBOXLON = (6.527650,18.471650)
#    if    not (IBBOXLAT[0] <= lat <= IBBOXLAT[1]) \
#       or not (IBBOXLON[0] <= lon <= IBBOXLON[1]):
#       continue


WOC = tuct.Tuct(
        APPNAME = APPNAME,

        VERSION = VERSION,
        
        BASE_DIR = BASE_DIR,
        
        CURR_DIR = CURR_DIR,

        CONFIGNAME = CONFIGNAME,
        
        CONFIGFILE = CONFIGFILE,
        
        CONFIGSPECFILE = CONFIGSPECFILE,
        
        COORDSDB = COORDSDB,
        
        GEODB = GEODB,

        IBBOXLAT = IBBOXLAT,
        
        IBBOXLON = IBBOXLON,
        
        DESCRIPTION = DESCRIPTION,

        EPILOG = EPILOG 
       )
# ***** END application (meta)data *****

if __name__ == '__main__':
   pass
