#! /usr/env/python
# -*- coding: UTF-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# If not, see <http://www.gnu.org/licenses/>.

import sys 
import logging

logger = logging.getLogger('sogbot.parse')

from configobj import ConfigObj, ConfigObjError, flatten_errors
from validate import Validator
from wocvalidate import writefile_check, readfile_check, loglevel_check


class Error(Exception):
   """Base class for exceptions in this module."""
   pass

class FailedValidation(Error):
   def __init__(self, key, section_list):
      self.key = key
      self.section_list = section_list
      self.msg = 'The "%s" key in the section "%s" failed validation' %(key, ', '.join(section_list))

      logger.error(self.msg)
      sys.stderr.write(self.msg)

class MissingParameter(Error):
   def __init__(self, section_list):
      self.section_list = section_list
      self.msg = 'The following section was missing:%s' % ', '.join(section_list)
    
      logger.error(self.msg)
      sys.stderr.write(self.msg)

def azzera_errori(cfg, res):
   logger.debug("res: %s" %res)
   if res == True:
      return cfg
   #logger.debug("res.items(): %s" %res.items())
   for (key, val) in res.items():
      logger.debug("key: %s" %key)
      logger.debug("val: %s" %val)
      if val == True:
         logger.debug("OK")
         continue
      if isinstance(cfg.get(key), dict):
         # Go down one level
         logger.debug("--- down one level ---")
         conf = azzera_errori(cfg[key], val)
         logger.debug("conf: %s" %conf)
         cfg[key] = conf
         continue

      logger.debug("Some errors here")
      cfg[key] = None
       
   return cfg

def _update_dict(section, key, diz):
   """
   Dumps all contents in a dictionary
   """
  
   val = section[key]
   if val is not None:
      diz[key] = val

VALIDATEDICT = {
      'writefile' : writefile_check,      
      'loglevel' : loglevel_check,
      'readfile' : readfile_check,
    }


def parse(config_infile, spec_infile):
   try:
      config = ConfigObj(infile=config_infile, options=None, configspec=spec_infile, encoding=None, \
		  interpolation=True, raise_errors=False, list_values=False, \
		  create_empty=False, file_error=True, stringify=True, \
		  indent_type='    ', default_encoding=None, unrepr=False, \
		  write_empty_values=False, _inspec=False)

   except (ConfigObjError, IOError), e:
      logger.error('Could not read "%s": %s' % (config_infile, e))
      raise IOError

   validator = Validator(VALIDATEDICT)
   validation_result = config.validate(validator, preserve_errors=True) 
  
   if validation_result is not True:
      for (section_list, key, _) in flatten_errors(config, validation_result):
         logger.debug(section_list)
         logger.debug(key)
         if key is not None:
            #raise FailedValidation(key, section_list)
            msg = 'The "%s" key in the section "%s" failed validation\n' % (key, ', '.join(section_list))
            logger.warning(msg)

         else:
            #raise MissingParameter(section_list)
            msg = 'The following section was missing:%s' % ', '.join(section_list)
            logger.warning(msg)
  
   logger.debug("config  %s" %config)
  
   logger.debug("validation_result  %s" %validation_result)

   logger.debug("-----\n\n\n\n")

   conf = azzera_errori(config, validation_result)
  
   logger.debug("-----\n\n\n\n")
  
   logger.debug("conf  %s" %conf)
  
   dizionario={}
  
   config.walk(_update_dict, raise_errors=True, \
	      call_on_sections=False, diz=dizionario)

  
   logger.debug("%s" %dizionario)
  
   return dizionario

  
# ----- main -----
if __name__ == '__main__':
   import os
  
   CONFIGNAME = 'autosend.cfg'

   CONFIGSPECNAME = 'autosend.spec.cfg'
  
   CFGDIR = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../config')
  
   #print "CFGDIR =", CFGDIR
   #print "type: ", type(CFGDIR)
   #print os.path.exists(CFGDIR)
  
   CFGFILE = CFGDIR + '/' + CONFIGNAME
  
   #print "CFGFILE = ", CFGFILE
  
   CFGSPECFILE = CFGDIR + '/' + CONFIGSPECNAME
  
   #print "CFGSPECFILE = ", CFGSPECFILE
  
   parse(config=CFGFILE, spec=CFGSPECFILE)