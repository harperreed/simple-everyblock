import time
import urllib, urllib2
from BeautifulSoup import BeautifulStoneSoup

"""
here is a wrapper for the EveryBlock API
  Built by Harper Reed (harper@nata2.org) - @harper
  git@github.com:harperreed/simple-everyblock.git

You can get an API key here:
  https://chicago.everyblock.com/api-signup/

Documentation is here:
  http://www.everyblock.com/apidocs/

Google Group is here:
  http://groups.google.com/group/everyblock-api/

Notes:
  For some reason I found this API a pain in the ass to deal with. One of the
  reasons I built this class is to make it super easy. 

  Hopefully this will help some people consume the data

  I used beutiful soup to handle the XML so it could be used in places that
  lxml and the like cannot be used (App Engine).

  <small_rant>
  A couple things have bothered me about this API since I started playing with
  it. I figured I would put them here. 

  1) WTF are Schemas? They seem to complicate things.

  2) WTF @ xml. This isn't 1998. Most people are going to want this data as an
  object, so why not use JSON or some other machine serializable data format.
  If XML is important, then have it be an option. If XML is the only option,
  then treat it like xml: have DTDs and use Namespaces. 

  3) Why only 24 hrs of data? You are creating a relationship here the API consumers 
  will have to cache and store all of *your* data, because it is impossible to get at
  the data past 24hrs. You lose control of your data.

  4) Where is my API key? If you lose it, you have to get another one. I wish
  it were associated with my EB account. 

  This API seems built to dissuade people from using the EB data. Why is it 
  so hard to figure out? I have dealt with a few apis and I still don't 
  understand exactly whats going on here. 

  Once you get the data, it is awesome.
  </small_rant>

Usage:
  >>> from simple_everyblock import simple_everyblock
  >>> api = simple_everyblock(api_key=api_key)
  >>> print api.get_metros()
  [{'city': u'Atlanta', 'state': u'GA',...............
  >>> print api.get_schemas('dc')[0]
  {'url': u'http://dc.everyblock.com/commercial-real-estate/', ...............
  >>> print api.get_location_types('dc')
  [{'url': u'http://dc.everyblock.com/locatim.................
  >>> print api.get_locations('dc','neighborhoods')
  [{'url': u'http://dc.everyblock.com/locations/neighborhoods/bolling-air-force.......
  >>> print api.get_newsitems('dc', '2010-01-06-1900', '11')

  Should be simple



"""

class simple_everyblock:

    api_key = ''

    def __init__(self,  api_key=None):
      self.api_key = api_key

    def make_request(self, url, params=None, method='GET', ):
      if params:
        params = urllib.urlencode(params, True).replace('+', '%20')
      if method=='GET':
        if params:
          url = url + '?'+params
      f = urllib2.urlopen(url,params)
      data = f.read()
      f.close()
      response = self.parse_xml(data)
      return response

    def parse_xml(self, response):
      # i wish this was json. I think someone needs to welcome the EB devs to
      # the year 2004. json is our friend. 
      soup = BeautifulStoneSoup(response)
      response_code = soup.result.status.codeTag.string
      error_message = soup.result.status.messageTag.string
      if response_code == '-1':
        raise  Exception(response_code, error_message)
      return soup

    def get_metros(self):
      url = 'http://api.everyblock.com/0.1/metros/'
      result = self.make_request(url)
      metros_xml = result.findAll('metro')
      metros = []
      for metro_xml in metros_xml:
        metro = {
            'name':metro_xml['name'],
            'short_name':metro_xml['short_name'],
            'city':metro_xml['city'],
            'state':metro_xml['state'],
            'tz':metro_xml['tz'],
            'sw_longitude':metro_xml['sw_longitude'],
            'sw_latitude':metro_xml['sw_latitude'],
            'ne_longitude':metro_xml['ne_longitude'],
            'ne_latitude':metro_xml['ne_latitude'],
            }
        metros.append(metro)
      return metros

    def get_schemas(self, metro):
      url = 'http://api.everyblock.com/0.1/schemas/'
      params = {
          'metro': metro,
          }
      result = self.make_request(url=url, params=params, method='GET')
      schemas_xml = result.findAll('schema')
      schemas = []
      for schema_xml in schemas_xml:
        fields_xml = schema_xml.findAll('field')
        fields = []
        for f in fields_xml:
          field = {
              'name':f['name'],
              'pretty_name':f['pretty_name'],
              'pretty_name_plural':f['pretty_name_plural'],
              }
          fields.append(field)
        schema = {
          'id': schema_xml['id'],
          'name': schema_xml['name'], 
          'plural_name':schema_xml['plural_name'],
          'slug':schema_xml['slug'],
          'indefinite_article':schema_xml['indefinite_article'],
          'url':schema_xml['url'],
          'url_about':schema_xml['url_about'],
          'fields':fields,
          }
        schemas.append(schema)
      return schemas

    def get_location_types(self, metro):
      url ='http://api.everyblock.com/0.1/location_types/'
      params = {
          'metro': metro,
          }
      result = self.make_request(url=url, params=params, method='GET')
      location_type_xml = result.findAll('location_type')
      location_types = []
      for location_type_xml in location_type_xml:
        location_type = {
            'id':location_type_xml['id'],
            'name':location_type_xml['name'],
            'plural_name':location_type_xml['plural_name'],
            'slug':location_type_xml['slug'],
            'url':location_type_xml['url'],
            }
        location_types.append(location_type)
      return location_types

    def get_locations(self, metro, location_type):
      url = 'http://api.everyblock.com/0.1/locations/'
      params = {
          'metro': metro,
          'location_type':location_type,
          }
      result = self.make_request(url=url, params=params, method='GET')
      locations_xml = result.findAll('location')
      locations = []
      for location_xml in locations_xml:
        location = {
          'id':location_xml['id'],
          'name':location_xml['name'],
          'slug':location_xml['slug'],
          'url':location_xml['url'],
            }
        locations.append(location)
      return locations

    def get_newsitems(self, metro, start_date, schemas):
      url = 'http://api.everyblock.com/0.1/newsitems/'
      params = {
          'metro': metro,
          'api_key': self.api_key,
          'since': start_date,
          'schemas': schemas,
          }
      result = self.make_request(url=url, params=params, method='GET')
      newsitems_xml = result.findAll('newsitem')
      newsitems = []
      for newsitem_xml in newsitems_xml:
        newsitem = {
            'id':newsitem_xml['id'],
            'title':newsitem_xml['title'],
            'url':newsitem_xml['url'],
            'location_name':newsitem_xml['location_name'],
            'schema':newsitem_xml['schema'],
            'schema_id':newsitem_xml['schema_id'],
            'pub_date':newsitem_xml['pub_date'],
            'longitude':newsitem_xml['longitude'],
            'latitude':newsitem_xml['latitude'],
            }
        newsitems.append(newsitem)
      return newsitems

if __name__ == "__main__": 
    api_key = ""
    api = simple_everyblock(api_key=api_key)
    print api.get_metros()
    print api.get_schemas('dc')[0]
    print api.get_location_types('dc')
    print api.get_locations('dc','neighborhoods')
    print api.get_newsitems('dc', '2011-40-13', '11')

