'''
Created on 31/mag/2013

@author: cristian
'''

import urllib
import logging

from wocurlbuilder import UrlBuilder
from wocjson import JSONQuerier

logger = logging.getLogger('woc.wocsparql')

class SPARQLQueryBuilder:
   """
   A SPARQL query builder class
   """

   def __init__(self,subj,pred,obj,sel='*'):
      self.subject = subj
      self.predicate = pred
      self.object = obj
      self.select = sel
      self.query="""SELECT {sel} WHERE {{
                     {subj} {pred} {obj}.
                    }}
                  """

   def set_subject(self,subj):
      self.path = subj
      return self

   def set_predicate(self,pred):
      self.predicate = pred
      return self

   def set_object(self,obj):
      self.object = obj
      return self

   def __str__(self):
      return self.query.format(
                               sel=self.select,
                               subj=self.subject,
                               pred=self.predicate,
                               obj=self.object
                               )
   def build(self):
      return self.__str__()
   

DBPEDIAURL='it.dbpedia.org'
class DBpediaTypeQuerier():
   
   def __init__(self,wikipagename):
      subjUrl = UrlBuilder(domain=DBPEDIAURL,
                                path="resource/{pagename}".format(pagename=wikipagename))
      predUrl = UrlBuilder(domain="www.w3.org",
                                path="1999/02/22-rdf-syntax-ns#type")

      self.subj = '<{url}>'.format(url=subjUrl.build())
      self.pred = '<{url}>'.format(url=predUrl.build())   
      self.obj = "?type"
      
      self.dbpurl = None
      
   def _build_query(self):      
      q = SPARQLQueryBuilder(self.subj,self.pred,self.obj)
      query=q.build()
      
      query = urllib.quote(query)
      queryurl = UrlBuilder(domain=DBPEDIAURL,
                              path="sparql/",
                              params='default-graph-uri=',
                              attrs={'query': query,
                                     'format': 'json'
                                    }
                             )
      self.dbpurl=queryurl.build()
   
   def get_json(self):
      if not self.dbpurl:
         self._build_query()  

      jsonquery = JSONQuerier(self.dbpurl)
      return jsonquery.get_jobj()
      

NOMINATIMOSM='nominatim.openstreetmap.org'
class NominatimPlaceQuerier():
   
   def __init__(self,pagename):
      #http://nominatim.openstreetmap.org/search.php?q=Abbazia+di+Sant%27Antimo&format=json
      nominatimUrl = UrlBuilder(domain=NOMINATIMOSM,
                                path='search.php',
                                params='q={pagename}'.format(pagename=pagename),
                                attrs={'format': 'json'}
                               )
   
      self.nominurl = nominatimUrl.build()
      logger.debug(self.nominurl)

   def get_json(self):
      jsonquery = JSONQuerier(self.nominurl)
      return jsonquery.get_jobj()
      
