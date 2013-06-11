#! /usr/bin/python
# -*- coding: UTF-8 -*-

import os

from validate import ValidateError
from validate import Validator

import logging
logger = logging.getLogger('sogbot.validate')

logger.setLevel(logging.WARNING)

from wocglobal import WOC

def writefile_check(value):
   if os.path.dirname(value) == '':
      curr_dir=WOC['CURR_DIR']
      value = os.path.abspath(os.path.normpath(os.path.join(curr_dir,value)))

   if isinstance(value, list):
      msg = 'A list was passed when a path with write permission was expected'
      logger.error(msg)
      raise ValidateError(msg)
      
#    logger.debug(value)
#    if os.path.exists(value):
#       msg = '"%s" already exists' %value
      
      logger.error(msg)
      raise ValidateError(msg)
      
   elif not os.access(os.path.dirname(value), os.W_OK):
      msg = 'User has not the valid permissions to write: "%s"' % value
      logger.error(msg)
      
      raise ValidateError(msg)
   return value

def readpath_check(value):
   value = os.path.abspath(os.path.normpath(value))
   #print "path: %s" %value
   if isinstance(value, list):
      msg = 'A list was passed when a path with read permission was expected'
      logger.error(msg)
      raise ValidateError(msg)
      
   #print "type: ", type(value)
   #print os.path.exists(value)
    
   logger.debug(value)
   if not os.path.exists(value):
      msg = '"%s" is not a valid path' % value
      logger.error(msg)
      
      raise ValidateError(msg)
      
   elif not os.access(value, os.R_OK):
      msg = 'User has not the valid permissions to read: "%s"' % value
      logger.error(msg)
      raise ValidateError(msg)
            
   return value

def readfile_check(value):
   value = os.path.abspath(os.path.normpath(value))
   #print "path: %s" %value
   if isinstance(value, list):
      msg = 'A list was passed when a path with read permission was expected'
      logger.error(msg)
      raise ValidateError(msg)

   #print "type: ", type(value)
   #print os.path.exists(value)

   logger.debug(value)
   if not os.path.exists(value):
      msg = '"%s" is not a valid path' % value
      raise ValidateError(msg)

   elif not os.path.isfile(value):
      msg = '"%s" is not a regular file:' % value
      raise ValidateError(msg)

   elif not os.access(value, os.R_OK):
      msg = 'User has not the valid permissions to read: "%s"' % value
      raise ValidateError(msg)

   return value

LOGLEVELS = {'debug': logging.DEBUG,
             'info': logging.INFO,
             'warning': logging.WARNING,
             'error': logging.ERROR,
             'critical': logging.CRITICAL
            }


def loglevel_check(value):
   #print "path: %s" %value
   if isinstance(value, list):
      msg = 'A list was passed when a log level was expected'
      logger.warning(msg)
      raise ValidateError(msg)

   level = LOGLEVELS.get(value.lower(), logging.NOTSET)
   return level