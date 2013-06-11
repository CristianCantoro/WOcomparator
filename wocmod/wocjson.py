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

import urllib
import logging
import json

logger = logging.getLogger('woc.wocjson')

class JSONQuerier(object):

   def __init__(self,url,maxtries=10):
      self.url = url
      self.fpage = None
      self.jobj = None
      self.maxtries = maxtries
      self.ntry = 0
      
   def get_page(self):
      while (not self.fpage) or (self.ntry > self.maxtries):
         try:
            self.fpage = urllib.urlopen(self.url)
         except Exception as e:
            logger.debug(e)
            self.fpage = None
            self.ntry=self.ntry+1
      
      return self.fpage

   def get_jobj(self):   
      if not self.fpage:
         self.get_page()
      
      try:
         self.jobj = json.load(self.fpage)
      except Exception as e:
         logger.debug(e)

      return self.jobj
