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
import urllib
import re

from wocurlbuilder import UrlBuilder

logger = logging.getLogger('woc.wocwiki')

WIKIPEDIAURL='{lang}.wikipedia.org'
LANGREGEX = re.compile("[a-z]{2}\:")
LANGURLREGEX = re.compile("http\://[a-z]{2}\.")

class MissingInformation(Exception):
   pass

class WikipediaGetter(object):
   
   def __init__(self,wikipedia_page=None,wikipedia_lang=None,oitem=None,witem=None):
      self.wikipedia_page = wikipedia_page
      self.wikipedia_lang = wikipedia_lang
      self.oitem = oitem
      self.witem = witem
      
      if self.oitem:
         self.wikipedia_page = self._reconcile(wikipedia_page,
                                               self.oitem.wikipedia_page)

         self.wikipedia_lang = self._reconcile(wikipedia_lang,
                                               self.oitem.wikipedia_lang)

      if self.witem:
         self.wikipedia_page = self._reconcile(wikipedia_page,
                                               self.witem.wikipedia_page)

         self.wikipedia_lang = self._reconcile(wikipedia_lang,
                                               self.witem.wikipedia_lang)
         
      if self.witem and self.oitem:
         self.wikipedia_page = self._reconcile(self.oitem.wikipedia_page,
                                               self.witem.wikipedia_page)

         self.wikipedia_lang = self._reconcile(self.oitem.wikipedia_lang,
                                               self.witem.wikipedia_lang)

      assert self.wikipedia_page
      assert self.wikipedia_lang

   def _check_consistency(self,a,b):
      if (a is None) or (b is None):
         return True
      else:
         return a == b

   def _reconcile(self,a,b):
      assert self._check_consistency(a,b)
      return a or b
   
   def _string_to_int(self):
      ord3 = lambda x : '%.3d' % ord(x)
      return int('1'+''.join(map(ord3, self.wikipedia_page)))
   
   def get_page(self):
      return self.wikipedia_page
   
   def get_id(self):
      if self.wikipedia_page:
         return self._string_to_int()
      else:
         return None

   def get_link(self):
      urlpagename = urllib.quote(self.wikipedia_page)
      wikipediaurl = UrlBuilder(
                        domain=WIKIPEDIAURL.format(lang=self.wikipedia_lang),
                        path="wiki/{pagename}".format(pagename=urlpagename)
                     )
      wikiurl=wikipediaurl.build()
      logger.debug(wikiurl)
      
      self.wikipedia_link = wikiurl
      return self.wikipedia_link


if __name__ == '__main__':
   import sys
   sys.path.append('../')
   from wocitem import OSMItem,WikipediaItem
   
   oitem = OSMItem(12345)
   oitem.wikipedia_page = 'Abbazia_di_San_Galgano'
   oitem.wikipedia_lang = 'it'

   witem = WikipediaItem(54321)
   witem.wikipedia_page = 'Abbazia_di_San_Galgano'
   witem.wikipedia_lang = 'it'
   
   wikipedia_page = 'Abbazia_di_San_Galgano'
   wikipedia_lang = 'it'
   
   wg = WikipediaGetter(wikipedia_page=wikipedia_page,
                        wikipedia_lang=wikipedia_lang,
                        oitem=oitem,
                        witem=witem)

   wg = WikipediaGetter(wikipedia_page=wikipedia_page,
                        wikipedia_lang=wikipedia_lang,
                        witem=witem)

   wg = WikipediaGetter(wikipedia_page=wikipedia_page,
                        wikipedia_lang=wikipedia_lang,
                        oitem=oitem)

   wg = WikipediaGetter(oitem=oitem,
                        witem=witem)

   wg = WikipediaGetter(oitem=oitem)

   wg = WikipediaGetter(witem=witem)

   wg = WikipediaGetter(wikipedia_page=wikipedia_page,
                        wikipedia_lang=wikipedia_lang)

   try:
      wg = WikipediaGetter()
   except AssertionError:
      pass

   
   