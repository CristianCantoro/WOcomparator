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


list_infile = open('../osm2wiki_distances.txt','r')
inlist = list(UnicodeReader(list_infile,
                            delimiter=',',
                            quotechar='"'))

outfile = open('osm2wiki_distances_wikitable.txt','w+')

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
   wiki_lon = row[5] 
   wiki_lat = row[6]
   distance = row[7]
   intersects = row[8]
   
   osm_element = ELEMENTS[osm_type]

#/?node=2321988596&mlat=46.07620&mlon=11.12461

   osmUrl = UrlBuilder(domain=OSMURL,
                       path='',
                       params='{osm_element}={osm_id}'.format(
                                                       osm_element=osm_element,
                                                       osm_id=osm_id),
                       attrs={'mlat': wiki_lat,
                              'mlon': wiki_lon
                             }
                      )
   osmurl = osmUrl.build()
   
   print row
   row[0] = '[[{wikipage}|{pagename}]]'.format(
                                          wikipage=wikipage,
                                          pagename=wikipage.replace('_',' '))
   
   row[1] = '[{osmurl} {osm_id}]'.format(osmurl=osmurl,
                                         osm_id=osm_id)
   
   if row[8] == 'False':
      row[0] = 'style="background: #DE2424" |' + row[0] 
   else:
      row[0] = 'style="background: #24DE24" |' + row[0]
      
   txt = '|'
   txt += '|| '.join(row) + '\n'
   txt += '|-\n'
   outfile.write(txt)                                     


outfile.write('|}')
outfile.close()