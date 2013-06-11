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

import sys
sys.path.append('../')

from wocmod.wocunicode import UnicodeReader
from wocmod.wocurlbuilder import UrlBuilder

OSMURL = 'www.openstreetmap.org'
ELEMENTS = {'point': 'node',
            'line': 'way',
            'polygon': 'way',
            'roads':   'way'
            }


list_infile = open('../osm_nowiki.txt','r')
inlist = list(UnicodeReader(list_infile,
                            delimiter=',',
                            quotechar='"'))

outfile = open('osm_nowiki_wikitable.txt','w+')

header_list = inlist.pop(0)

outfile.write('{| {{prettytable}}\n')
txt = '!'
txt += '!! '.join(header_list) + '\n'
txt += '|-\n'
outfile.write(txt)                                     

for row in inlist:
   row[:] = [r.encode('utf-8') for r in row]
   wikipage = row[0]
   osm_id = row[1]
   osm_type = row[2]
   osm_lon = row[3]
   osm_lat = row[4]
   
   osm_element = ELEMENTS[osm_type]

   osmUrl = UrlBuilder(domain=OSMURL,
                       path='',
                       params='{osm_element}={osm_id}'.format(
                                                       osm_element=osm_element,
                                                       osm_id=osm_id),
                       attrs={'mlon': osm_lon,
                              'mlat': osm_lat
                             }
                      )
   osmurl = osmUrl.build()
   
   print row
   row[0] = '[[{wikipage}|{pagename}]]'.format(
                                          wikipage=wikipage,
                                          pagename=wikipage.replace('_',' '))
   
   row[1] = '[{osmurl} {osm_id}]'.format(osmurl=osmurl,
                                         osm_id=osm_id)
         
   txt = '|'
   txt += '|| '.join(row) + '\n'
   txt += '|-\n'
   outfile.write(txt)                                     


outfile.write('|}')
outfile.close()