
import re
import urllib
import datetime
import requests

import svy21

_om = {}
def OneMap(access_key):
    global _om
    if access_key not in _om:
        _om[access_key] = OneMapAPI(access_key)
    return _om[access_key]


class OneMapAPI(object):

    BASE_DOMAIN = "http://www.onemap.sg"
    API_ROUTE = "/API/services.svc"
    COMMON_PARAMS = {"wc": "", "returnGeom": 1, "rset": 1, "otptflds": "SEARCHVAL,CATEGORY,THEME"}
    WILDCARD_PATTERNS = {
        "startswith": "%s like '%s$'",
        "endswith": "%s like '$%s'",
        "includes": "%s like '$%s$'",
        "plain": "%s like '%s'"
    }

    def __init__(self, access_key):
        self.access_key = access_key
        self.token = None
        self.token_expiry = None


    def _ping(self, endpoint, params, api_route=None):

        if endpoint != 'getToken' and not params.get('token'):
            if not self.token:
                self.get_token()
            params['token'] = self.token

        url = "%s/%s/%s?%s" % (self.BASE_DOMAIN, api_route or self.API_ROUTE, endpoint, urllib.urlencode(params))
        rv = requests.get(url)

        data = {}
        error = None
        page_count = 0
        items = []

        try:
            data = rv.json()
            items = rv.json().pop(data.keys()[0])
            if 'ErrorMessage' in items[0] or 'PageCount' in items[0]:
                s = items.pop(0)
                error = s.get('ErrorMessage')
                page_count = s.get('PageCount', 0)
        except ValueError as e:
            error = e

        OMR = OneMapResult(
            endpoint,
            params,
            rv.status_code,
            page_count,
            items,
            error,
            data
        )
        return OMR


    def _validate_wildcard(self, term, wildcard, search_by=None):
        if wildcard not in self.WILDCARD_PATTERNS.keys():
            raise OneMapError("'wildcard' parameter needs to be one of 'startswith', 'endswith' or 'includes'")
        else:
            wildcard = self.WILDCARD_PATTERNS[wildcard] % (search_by or 'searchVal', term)

        return wildcard


    def _validate_geo(self, with_geo):
        return 1 if with_geo or with_geo is None else 0


    def _validate_page(self, page):
        return 1 if page is None else int(page)


    # def _validate_fields(self, field):
    #     fields = map(lambda x: x.strip(), fields.split(","))
    #     if all(map(lambda x: x in ))


    def _params(self, **kwargs):
        data = self.COMMON_PARAMS.copy()

        if kwargs.get('term') and kwargs.get('wildcard'):
            data['wc'] = self._validate_wildcard(kwargs.get('term'), kwargs.get('wildcard'), kwargs.get('search_by'))

        if kwargs.get('with_geo') is not None:
            data['returnGeom'] = self._validate_geo(kwargs.get('with_geo'))

        if kwargs.get('page') is not None:
            data['rset'] = self._validate_page(kwargs.get('page'))

        if kwargs.get('show_fields'):
            data['otptflds'] = kwargs.get('show_fields')

        return data


    def get_token(self):

        if self.token and self.token_expire and datetime.datetime.utcnow() < self.token_expiry:
            return self.token

        data = self._ping('getToken', {"accessKey": self.access_key})

        if data.raw.get('GetToken') and \
          len(data.raw.get('GetToken')) and \
          data.raw.get('GetToken')[0].get('NewToken'):
            self.token = data.raw.get('GetToken')[0].get('NewToken')
            self.token_expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            return self.token


    def search_address(self, term, wildcard='startswith', **kwargs):
        '''
        Basic address search on OneMap

        args
            term          Address string to search, eg. "City Hall"

        kwargs
            wildcard         Performs a wildcard search. Value can be one of 'startswith', 'endswith' or 'includes'
                             In common regex syntax, these are the effects of the wildcard values:
                                'startswith' :   "^<term>"
                                'endswith'   :   "<term>$"
                                'includes'   :   ".*<term>.*"

            with_geo         True, to return geometry (ie. coordinates) in results, False otherwise

            page             Page number to return. Default 1. Result sets are limited to 10 per page
        '''

        data = self._ping("basicSearch", self._params(term=term, wildcard=wildcard, **kwargs))

        return data


    def search_theme(self, term, wildcard='plain', search_by='theme', **kwargs):
        '''
        Search OneMap with terms in certain themes
        Themes and categories to search for can be found at: http://www.onemap.sg/themeexp/themeexplorer.aspx#

        Usage:

        >>> OM = OneMap(<onemap_api_token>)
        >>> OM.search_term(term="wireless_hotspots", search_by="theme")
        ...results...

        args
            term            The search term.
                            This will be used in the query in the format,
                            wc="<search_by> like '<term>'"

        kwargs

            wildcard        Performs a wildcard search. Value can be one of 'startswith', 'endswith' or 'includes'
                            In common regex syntax, these are the effects of the wildcard values:
                               'startswith' :   "^<term>"
                               'endswith'   :   "<term>$"
                               'includes'   :   ".*<term>.*"

            search_by       The search category in which to perform this search, used in the following format
                            wc="<search_by> like '<term>'"
                            Defaults to 'theme'
        '''

        params = self._params(**kwargs)
        params['wc'] = self._validate_wildcard(term, wildcard, search_by=search_by)
        data = self._ping('themesearch', params)
        return data


    def geocode(self, location, buffer=100, address_type='all'):
        '''
        Wraps the reverse geocoding API on OneMap

        args
            location          A string in the format "lng,lat", representing the
                              point to reverse geocode

        kwargs
            buffer            Radius around the point within which results should be returned

            address_type      One of 'all' or 'hdb'
                              Returns all location types if 'all' and only HDB results otherwise
        '''

        return self._ping('revgeocode', {
            "location": location,
            "buffer": buffer,
            "addressType": address_type
        })


    def public_transport(self, start, end, walking_distance=100, mode='bus/mrt', route='fastest', with_geo=True, max_solutions=1):
        '''
        Wraps the public transport routing API

        args
            start                   The start point of the route.
                                    Can be an SVY21 coordinate pair, or a Singapore postal code

            end                     The end point of the route
                                    Can be an SVY21 coordinate pair, or a Singapore postal code

        kwargs
            walking_distance        Walking distance to bus or train stop. Defaults to 100

            mode                    String representing preferred mode of transport. Can be
                                    one of "bus" or "bus/mrt"

            route                   One of 'fastest' (default) or 'cheapest'

            with_geo                True, to return segments between start and end points, False otherwise

            max_solutions           Maximum number of solutions to return from the API
        '''

        return self._ping("routesolns", {
            "sl": start,
            "el": end,
            "walkdist": walking_distance,
            "mode": mode,
            "route": route,
            "retgeo": str(with_geo).lower(),
            "maxsolns": max_solutions
        }, api_route="/publictransportation/service1.svc")


    def filter(self, results, **filters):
        '''
        Filters a given OneMap API result set

        args
            results          Result set returned from the OneMap API

        kwargs
            filters          Dictionary of filters
                             filter() will return only records that match key-value pairs in filters
        '''

        res = []
        if 'SearchResults' in results:
            res = results['SearchResults']

        res_iter = iter(res)
        meta = res_iter.next()
        for f, value in filters.iteritems():
            res = filter(lambda x: x[f] == value, res_iter)

        return res

    def resolve(self, address, buffer=10):
        m = re.match("(?P<lng>\d+\.\d+),\s?(?P<lat>\d+\.\d+)", address)
        if m:
            x, y = (m.groupdict()['lng'], m.groupdict()['lat'])
        else:
            res = self.search_address(address)
            if res.error:
                raise OneMapError(res.error)
            item = res.items[0]
            x, y = (item.x, item.y)

        geo = self.geocode("%s,%s" % (x, y), buffer=buffer)
        if geo.error:
            raise OneMapError(geo.error)

        item = geo.items[0]
        out = {k: v for k, v in item.iteritems()}
        S = svy21.SVY21()
        i = geo.items[0]
        coordinates = S.computeLatLon(i.y, i.x)
        coordinates = list(coordinates)
        coordinates.reverse()
        out['coordinates'] = coordinates
        return out


class OneMapResult(object):

    def __init__(self, endpoint, params, status_code, page_count, items, error=None, raw=None):
        self.endpoint = endpoint
        self.params = params
        self.status_code = status_code
        self.page_count = int(page_count) if isinstance(page_count, basestring) else page_count
        self.error = error
        self.raw = raw
        self.items = [OneMapResultItem(**i) for i in items]

    def filter(self, **filters):
        def do_filter(item):
            return all(map(lambda (k,v): (item.get(k) or '').lower() == v.lower(), filters.iteritems()))

        return filter(do_filter, self.items)

    def __getitem__(self, key):
        return self.items[key]

    def __iter__(self):
        return self.items.__iter__()

    def __repr__(self):
        return str(self.items)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return str(self.items)


class OneMapResultItem(object):

    def __init__(self, **kwargs):
        self.__raw = {k.lower(): v for k, v in kwargs.items()}

        # Sanitise result field names
        for f in ['xcoord', 'x', 'ycoord', 'y']:
            if self.__raw.get(f):
                self.__raw[f[0]] = float(self.__raw.pop(f))

        if all([self.__raw.get('x'), self.__raw.get('y')]):
            S = svy21.SVY21()
            coordinates = S.computeLatLon(self.__raw['y'], self.__raw['x'])
            self.__raw['lat'] = coordinates[0]
            self.__raw['lng'] = coordinates[1]

    def __getattr__(self, name):
        try:
            return getattr(self.__raw, name)
        except AttributeError:
            if name in self.__raw:
                return self.__raw[name]
            else:
                raise AttributeError()

    def __getitem__(self, name):
        try:
            return self.__raw.get(name)
        except KeyError:
            raise AttributeError()

    def __dir__(self):
        return self.__raw.keys()

    def __repr__(self):
        return str(self.__raw)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return unicode(self.__raw)


class OneMapError(Exception):
    pass
