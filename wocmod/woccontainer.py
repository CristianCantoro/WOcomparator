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

import sys
import logging
from operator import itemgetter

#from sogbotmod import devel

logger = logging.getLogger('sogbot.container')

class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class RequestedError(Error):
  
  def __init__(self, missing):
    self.missing = missing
    self.msg = "The following elements are missing: %s\n" %(', '.join(missing))

    logger.error(self.msg)
    sys.stderr.write(self.msg)

class DependencyError(Error):

  def __init__(self, name, dep):
    self.name = name
    self.dep = dep

    optmsg = '''Option "%s" depends on "%s", but "%s" is neither
    an optional or a requested argument.\n'''
    self.msg = optmsg %(self.name, self.dep, self.dep)
    logger.error(self.msg)
    sys.stderr.write(self.msg)

class UnexpectedElement(Error):
  
  def __init__(self, ele):
    self.ele = ele
    self.msg = 'Element "%s" unexpected\n' %self.ele

    logger.error(self.msg)
    sys.stderr.write(self.msg)

class ConfigContainer(dict):

  def __init__(self, dictionary={}):
    self.lst_req = []
    self.lst_opt = []
    self.lst_dep = []
    self.lst_tot = []

    self.flag_req = False
    self.flag_opt = False
    self.flag_dep = False
    
    self.cont = dictionary
    
  def add_requested(self, name):
    if not self.lst_tot.count(name):
      self.lst_req.append(name)
      self.lst_tot.append(name)
    elif [dizio['name'] for dizio in self.lst_opt].count(name):
      index = [dizio['name'] for dizio in self.lst_opt].index(name)
      self.lst_opt.pop(index)
      self.lst_req.append(name)
    elif [dizio['name'] for dizio in self.lst_dep].count(name):
      index = [dizio['name'] for dizio in self.lst_dep].index(name)
      self.lst_dep.pop(index)
      self.lst_req.append(name)
    else:
      pass

  def add_optional(self, name, default):
    dic = {'name': name,
           'val': default
          }
    logger.debug("dic: %s" %dic)
    logger.debug("self.lst_tot.count(name=%s): %s" %(name, self.lst_tot.count(name)))
    if not self.lst_tot.count(name):
      self.lst_opt.append(dic)
      self.lst_tot.append(name)
    elif self.lst_req.count(name):
      self.lst_req.remove(name)
      self.lst_opt.append(dic)
    elif [dizio['name'] for dizio in self.lst_dep].count(name):
      index = [dizio['name'] for dizio in self.lst_dep].index(name)
      logger.debug("index: %s" %index)
      logger.debug("dic: %s" %dic)
      self.lst_dep.pop(index)
      self.lst_opt.append(dic)
    else:
      index = [dizio['name'] for dizio in self.lst_opt].index(name)
      logger.debug("index: %s" %index)
      logger.debug("list: %s" %[dizio['name'] for dizio in self.lst_opt])
      logger.debug("dic: %s" %dic)
      self.lst_opt.pop(index)
      self.lst_opt.append(dic)
      

  def add_depending(self, name, depends, value):
    if not isinstance(value, tuple):
      value = (value)
    
    dic = {'name': name,
           'dep': depends,
           'val': value
          }

    if not self.lst_tot.count(name):
      self.lst_dep.append(dic)
      self.lst_tot.append(name)
    elif self.lst_req.count(name):
      self.lst_req.remove(name)
      self.lst_dep.append(dic)
    elif [dizio['name'] for dizio in self.lst_opt].count(name):
      index = [dizio['name'] for dizio in self.lst_opt].index(name)
      self.lst_opt.pop(index)
      self.lst_dep.append(dic)
    else:
      index = [dizio['name'] for dizio in self.lst_dep].index(name)
      self.lst_dep.pop(index)
      self.lst_dep.append(dic)

  def merge(self, dictionary, priority=False):
    for k, v in dictionary.iteritems():
      try:
        self.cont[k]
      except:
        self.cont[k] = v

  def check_requested(self):
    if not self.flag_req:
      self.flag_req = True
      self.lst_miss_req = []
      for req in self.lst_req:
	try:
	  self.cont[req]
	except:
	  self.lst_miss_req.append(req)
    
    if len(self.lst_miss_req):
      return False
    else:
      return True

  def missing_requested(self):
    if self.lst_miss_req is None:
      self.check_requested()

    return self.lst_miss_req

  def __enforce_optional(self):
    for dic in self.lst_opt:
      name = dic['name']
      val = dic['val']
      try:
        self.cont[name]
      except:
        self.cont[name] = val

  def check_optional(self):
    if not self.flag_opt:
      self.flag_opt = True
      self.__enforce_optional()
    return True

  def __build_deptree(self, name, dep, deplist):
    if (self.lst_req.count(dep) or [dizio['name'] for dizio in self.lst_opt].count(dep)):
      deplist.append(dep)
      depdic = {'name': name,
                'deplist': deplist
               }
      return depdic
    else:
      deppar=[dic['dep'] for dic in self.lst_dep if dic['name'] in dep][0]
      logger.debug("deppar: %s" %deppar)
      deplist.append(dep)
      deplist = self.__build_deptree(name, deppar, deplist=deplist)
      return deplist

  def __enforce_depending(self):
    if not (self.flag_req and self.flag_opt):
      self.check_requested()
      self.check_optional()

    self.lst_dep_req = []
    self.lst_dep_notreq = []
    self.lst_deptree = []
    
    for dic in self.lst_dep:
      name = dic['name']
      dep = dic['dep']
      if not self.lst_tot.count(dep):
        raise DependencyError(name, dep)
      depdic = {}
      depdic = self.__build_deptree(name=name, dep=dep, deplist=[])
      self.lst_deptree.append(depdic)

    self.lst_deptree = sorted(self.lst_deptree, cmp=lambda x,y: cmp(len(x), len(y)), key=itemgetter('deplist'))

    for dictree in self.lst_deptree:
      name = dictree['name']
      val = [dic['val'] for dic in self.lst_dep if dic['name'] == name][0]
      dictree['deplist'].reverse()
      deplist = dictree['deplist']
      firstdep = deplist.pop()

      try:
        logger.debug("self.cont[%s]: %s" %(firstdep, self.cont[firstdep]))
        self.cont[firstdep]
        if self.cont[firstdep] == val:
          self.lst_dep_req.append(name)
        else:
          self.lst_dep_notreq.append(name)
      except:
        self.lst_dep_notreq.append(name)

    return self.lst_dep_req 

  def __check_dep_requested(self, lista):
    lst_miss_dep = []
    for req in lista:
      try:
        self.cont[req]
      except:
        lst_miss_dep.append(req)

    return lst_miss_dep

  def check_depending(self):
    if not self.flag_dep:
      logger.debug('check_depending')

      self.flag_dep = True
      self.lst_miss_dep = []
      lista = self.__enforce_depending()
      self.lst_miss_dep = self.__check_dep_requested(lista)

    if len(self.lst_miss_dep):
      return False
    else:
      return True

  def missing_depending(self):
    if self.lst_miss_dep is None:
      self.check_depending()
    return self.lst_miss_dep

  def get_container(self, type='dict'):
    logger.debug("self.cont: %s" %self.cont)
    if not self.check_requested():
      raise RequestedError(self.missing_requested())

    self.check_optional()

    if not self.check_depending():
      raise RequestedError(self.missing_depending())

    total = []
    total.extend(self.lst_req)
    total.extend([dizio['name'] for dizio in self.lst_opt])
    total.extend([dizio['name'] for dizio in self.lst_dep])

    for k in self.cont.keys():
      if not total.count(k):
        raise UnexpectedElement(k)

    return self.cont

  def get_meta(self):
    self.meta = {}
    for k in self.lst_req:
      dizreq = {'type': 'requested'}
      self.meta[k] = dizreq

    for k in self.lst_opt:
      dizopt = {'type': 'optional'}
      self.meta[k] = dizopt

    for k in self.lst_req:
      dizdep = {'type': 'depending'}
      self.meta[k] = dizdep

  def list_requested(self):
    return self.lst_req
  
  def list_optional(self):
    return self.lst_opt

  def list_depending(self):
    return self.lst_dep
