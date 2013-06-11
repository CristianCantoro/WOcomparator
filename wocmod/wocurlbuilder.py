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

class UrlBuilder:
   """
   A URL builder class, expects a domain, a path and a parameter.
   The default is:
     http://www.example.com/api.php?action
   Attributes in the form &attrname=attrvalue can be added to the 
   url with an appropriate function.
   """

   def __init__(self,domain="www.example.com",path="api.php",params=None,attrs=None):
      self.domain = domain
      self.path = path
      self.params = params
      
      if attrs is None:
         self.attrs = dict()
      else:
         self.attrs = attrs

   def with_path(self,path):
      self.path = path
      return self

   def with_params(self,params):
      self.params = params
      return self

   def set_attr(self,key,value):
      self.attrs[key]=value
      return self

   def __str__(self):
      res='http://' + self.domain + '/' + self.path
      if self.params is not None:
         res += '?' + self.params
      if len(self.attrs)>0:
         for k,v in self.attrs.iteritems():
            res=res+ "&" + k + '=' + v
      return res

   def build(self):
      return self.__str__()