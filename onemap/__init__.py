
import urllib
import datetime
import requests


class OneMap(object):

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
        return rv.json()


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
            data['wc'] = self._validate_wildcard(kwargs.get('term'), kwargs.get('wildcard'))

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

        if data.get('GetToken') and \
          len(data.get('GetToken')) and \
          data.get('GetToken')[0].get('NewToken'):
            self.token = data.get('GetToken')[0].get('NewToken')
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


class OneMapError(Exception):
    pass
