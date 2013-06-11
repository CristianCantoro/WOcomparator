#! /usr/bin/python
# -*- coding: UTF-8 -*-

import psycopg2
import logging

logger = logging.getLogger('wocmod.connection')

from wocglobal import WOC

class ConnectionManager(object):
   
   def __init__(self, f):
      self.f = f
   
   def connection_setup(self):
      self.con = psycopg2.connect(WOC['CONN_PARAMS'])
      #logger.debug("Connecting to DB '%s'" %OSMSNA['DBNAME'])
      return self.con
   
   def connection_close(self):
      #logger.debug("Closing connection to DB '%s'" %OSMSNA['DBNAME'])
      return self.con.close()
   
   
   def __call__(self,*args,**kwargs):
      self.connection_setup()
      self.cur=self.con.cursor()
      kwargs['con']=self.con
      kwargs['cur']=self.cur
      res=self.f(*args,**kwargs)
      self.connection_close()
      return res
   
# ----- main -----
if __name__ == '__main__':
   pass   