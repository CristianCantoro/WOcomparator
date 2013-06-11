#! /usr/env/python
# -*- coding: utf-8  -*-
#########################################################################
# Adapted from the recipe found at:
# http://code.activestate.com/recipes/\
#      498072-implementing-an-immutable-dictionary/
#
# Adapted by Cristian Consonni
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
##########################################################################

class Tuct(dict):
   def __setitem__(self, key, value):
      pass

   def __hash__(self):
      items = self.items()
      res = hash(items[0])
      for item in items[1:]:
         res ^= hash(item)
         return res
