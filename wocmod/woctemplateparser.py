#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
Uses the JSON DBpedia interface (JSONpedia)
http://json.it.dbpedia.org/
to scrape (Italian) Wikipedia pages.

A list of pages to scrape can be passed with a file or 
querying the it.wiki API
"""

import urllib, urllib2
import json
import time
import codecs
from xml.dom.minidom import parseString

from wocmod.wocurlbuilder import UrlBuilder

"""
Template data extractors
"""
def extract_data_edificio_religioso(template):
   data=dict()
   for attr,value in template.iteritems():
      attr=attr.replace(' ','').lower()
      data[attr]=''
      if type(value) is list:
         for v in value:
            if type(v) is unicode:
               data[attr]+=v
            elif type(v) is dict:
               if v['__type'] == "reference":
                  wikilink = v['label']
                  if len(v['content']) > 0:
                     k, wikilink = v['content'].popitem()
                     url = "http://it.wikipedia.org/wiki/%s" %wikilink
                     url = urllib.quote(url.encode('utf-8'))
                     data[attr] += " %s " %(v['label'])
               elif v['__type'] == "link":
                  data[attr] = "%s" %(v['description'])
               elif v['__type'] == "template":
                  data[attr] = v['name']
               elif v['__type'] == "inline_tag":
                  if v['name'] != 'br':
                     data[attr]+=' '
               elif v['__type'] == "open_tag":
                  if v['name'] != 'small':
                     data[attr]+=' '
               elif v['__type'] == "close_tag":
                  if v['name'] != 'small':
                     data[attr]+=' '
               else:
                  print type(v), v
                  print value
            else:
               print type(v), attr
      data[attr] = data[attr].strip()
   return data

def extract_data_coord(template):
   print template
   
   coord={'lat': '', 'long': ''}
   optionalpars= [u'dim:', u'globe:',u'region:',u'scale:',u'source:',u'type:']
   
   todel=set()
   for k,v in template.iteritems():
      for op in optionalpars:
         if op in v[0]:
            todel.add(k)
            break
   
   for k in todel:
      del template[k]
   
   anonpars=[tpar for tpar in template.keys() if '__anon_' in tpar]
   for ap in anonpars:
      template[int(ap.strip('__anon_'))]=template[ap][0]
      del template[ap]
   
   parsnums=[int(p.strip('__anon_')) for p in anonpars]
   parcount=len(anonpars)
   startpar=min(parsnums)
   stoppar=max(parsnums)
   
   gglat=float(template[startpar])
   mmlat=0
   sslat=0
   gglong=0
   mmlong=0
   sslong=0
   dirlat=''
   dirlong=''
   if parcount == 2:
      gglong=float(template[startpar+1])
   elif parcount == 4:
      dirlat=str(template[startpar+1])
      gglong=float(template[startpar+2])
      dirlong=str(template[startpar+3])
   elif parcount == 6:
      mmlat=float(template[startpar+1])
      dirlat=str(template[startpar+2])
      gglong=float(template[startpar+3])
      mmlong=float(template[startpar+4])
      dirlong=str(template[startpar+5])
   elif parcount == 8:
      mmlat=float(template[startpar+1])
      sslat=float(template[startpar+2])
      dirlat=str(template[startpar+3])
      gglong=float(template[startpar+4])
      mmlong=float(template[startpar+5])
      sslong=float(template[startpar+6])
      dirlong=str(template[startpar+7])
   
   deglat=float(gglat)+float(mmlat)/60.0+float(sslat)/3600.0
   deglong=float(gglong)+float(mmlong)/60.0+float(sslong)/3600.0
   
   if dirlat == "S":
      deglat =-deglat
   if dirlong == "W":
      deglong =-deglong
   
   coord['lat']=str(deglat)
   coord['long']=str(deglong)
   return coord

"""
Configuration params
"""
MAXTRIES=10
CSVFILENAME="edifici_religiosi_out.csv"
CSVDELIMITER='|'

# Percorso (locale o remoto) del file contente la lista delle voci.
INLISTURL="file:///home/cristian/FBK/SpazioDati/edifici-religiosi/new/edifici_religiosi_in.txt"
#INLISTURL=""
#INLISTURL= "https://dl.dropboxusercontent.com/u/1197917/it_edificio_religioso.txt"

WPDOMAIN="it.wikipedia.org"
WPTNAME='Template:Edificio religioso'
WPTCALL=extract_data_edificio_religioso
OTHERTEMPLATES={
  'Template:coord': extract_data_coord
}

# Attributes for Template:Edificio religioso
# {{Edificio religioso
# |Nome =
# |Immagine =
# |Larghezza =
# |Didascalia =
# |SiglaStato =
# |Regione =
# |Città =
# |Religione =
# |DedicatoA =
# |Ordine =
# |Diocesi =
# |AnnoConsacr =
# |AnnoSconsacr =
# |Fondatore =
# |Architetto =
# |StileArchitett =
# |InizioCostr =
# |FineCostr =
# |Demolizione =
# |Sito =
# }}

ATTRLIST=[
u'wikipediaid',
u'NomeVoce',
u'Nome',
u'Immagine',
u'Larghezza',
u'Didascalia',
u'SiglaStato',
u'Regione',
u'Città',
u'Religione',
u'DedicatoA',
u'Ordine',
u'Diocesi',
u'AnnoConsacr',
u'AnnoSconsacr',
u'Fondatore',
u'Architetto',
u'StileArchitett',
u'InizioCostr',
u'FineCostr',
u'Demolizione',
u'Sito',
u'lat',
u'long'
]

"""
Utility functions
"""
_jsonu = UrlBuilder(
               domain="json.it.dbpedia.org",
               path="annotate/resource/json/it%3A{wp-page}",
               params="filter=__type:template"
              )
_jsonu.set_attr('flags','-Extractors,Structure,')
_jsonbaseurl=_jsonu.build()

def get_jsonpedia_page(v):
   """
   Gets the corrisponding JSONpedia page (only templates)
   for Wikipedia article titled 'v'.
   Tries MAXTRIES times or returns none.
   """
   vsafe = v.replace(' ','_')
   jsonurl = _jsonbaseurl.replace('{wp-page}',urllib.quote(vsafe))
   for ntry in range(1,MAXTRIES):
      try:
         print "Request no. %d: requesting: %s" %(ntry,jsonurl)
         jsonpage = urllib2.urlopen(jsonurl)
         break
      except:
         print "Request no. %d failed." %ntry
         jsonpage = None
         time.sleep(3)

   return jsonpage

def query_api():
   queryurl = UrlBuilder(domain=WPDOMAIN,path="w/api.php",params="action=query")
   queryurl.set_attr('generator','embeddedin')
   queryurl.set_attr('geititle',WPTNAME)
   queryurl.set_attr('einamespace','0')
   queryurl.set_attr('geilimit','500')
   queryurl.set_attr('format','xml')
   
   inlist=list()
   
   while True:
      print "Requesting %s" %queryurl.build()
      infile = urllib2.urlopen(queryurl.build())
      inxml = infile.read()
      
      xml = parseString(inxml)
      
      pagelist=xml.getElementsByTagName("page")
      
      for page in pagelist:
         inlist.append(page.getAttribute("title"))
      
      querycont=xml.getElementsByTagName("embeddedin")
      if len(querycont) == 0:
         break
      
      geicontinue=querycont[0].getAttribute("geicontinue")
      queryurl.set_attr("geicontinue",geicontinue)
      
      time.sleep(5)
   
   return inlist

def get_page_id(v):
   pageid = None
   #http://it.wikipedia.org/w/api.php?action=query&titles=Abbazia_di_San_Galgano&format=json
   #{"query":{"normalized":[{"from":"Abbazia_di_San_Galgano","to":"Abbazia di San Galgano"}],"pages":{"83117":{"pageid":83117,"ns":0,"title":"Abbazia di San Galgano"}}}}
   queryurl = UrlBuilder(domain=WPDOMAIN,path="w/api.php",params="action=query")
   queryurl.set_attr('titles',v)
   queryurl.set_attr('format','json')
   query=queryurl.build()
   for ntry in range(1,MAXTRIES):
      print "Request no. %d - Requesting %s" %(ntry,query)
      jsonpage = urllib2.urlopen(query)
      
      try:
         jobj = json.load(jsonpage)
         pageid = int(jobj['query']['pages'].keys()[0])
         break
      except Exception as e:
         print e
         pageid = None
         time.sleep(5)
         continue
   
   return pageid

  

"""
Main loop
"""
inlist=list()

for v in inlist:
   v=v.strip()
   
   # create empty dictionary with keys in ATTRLIST
   # sets 'NomeVoce'
   rowdict={key: '' for key in ATTRLIST}
   rowdict['wikipediaid']=get_page_id(v)
   rowdict['nomevoce']=v
   
   # request page, skip on fail
   jsonpage=get_jsonpedia_page(v)
   if jsonpage is None:
      continue
   jobj = json.load(jsonpage)
   
   # process templates
   for template in jobj['result']:
      wptname=unicode(WPTNAME.split(':')[1]).lower()
      if template['name'].lower() == wptname:
         try:
            row = WPTCALL(template['content'])
            rowdict.update(row)
         except Exception as e:
            print "Caught exception while processing %s" %WPTNAME
            print "Template content:"
            print template['content']
            continue
      
      for tname, tcall in OTHERTEMPLATES.iteritems():
         if template['name'].lower() == unicode(tname.split(':')[1]).lower():
            try:
               row = tcall(template['content'])
               rowdict.update(row)
            except Exception as e:
               print "Caught exception while processing %s" %template['name']
               print "Template content:"
               print template['content']
