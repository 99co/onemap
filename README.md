# OneMap

This library provides a thin wrapper over the OneMap Singapore API (http://www.onemap.sg/api/help/)

You'll need an access key from OneMapSG before you'll be able to use the OneMapSG API

Examples

    >>>
    >>> import onemap
    >>> OM = onemap.OneMap("onemap_key")
    >>>
    >>> res = OM.search_address("city hall")
    >>> type(res)
    <class 'core.ext.onemap.OneMapResult'>
    >>>
    >>> res
    [{u'searchval': u'CITY HALL', u'category': u'Building', u'y': u'30360.5886', u'x': u'30051.7694'}, {u'searchval': u'CITY HALL (MONUMENTS)', u'category': u'Culture', u'y':     u'30339.5771', u'x': u'30047.6749'}, {u'searchval': u'CITY HALL (STREET AND PLACES)', u'category': u'Culture', u'y': u'30318.8100', u'x': u'30064.6100'}, {u'searchval': u'CITY     HALL AND THE PADANG (HERITAGE SITES)', u'category': u'Culture', u'y': u'30340.3699', u'x': u'30049.0300'}, {u'searchval': u'CITY HALL MRT STATION', u'category': u'Building',     u'y': u'30597.7817', u'x': u'30139.4704'}, {u'searchval': u'CITY HALL MRT STATION (EW13/NS25) (FRIENDLY BUILDINGS)', u'category': u'Community', u'y': u'30597.7817', u'x':     u'30139.4704'}, {u'searchval': u'CITY HALL MRT STATION EXIT A', u'category': u'Building', u'y': u'30611.1767', u'x': u'30182.8492'}, {u'searchval': u'CITY HALL MRT STATION EXIT     B', u'category': u'Building', u'y': u'30610.8982', u'x': u'30073.6413'}, {u'searchval': u'CITY HALL/ESPLANADE MRT STATION EXIT A', u'category': u'Building', u'y':     u'30415.3350', u'x': u'30369.4938'}, {u'searchval': u'CITY HALL/ESPLANADE MRT STATION EXIT B', u'category': u'Building', u'y': u'30457.5147', u'x': u'30385.8054'},     {u'searchval': u'CITY HALL/ESPLANADE MRT STATION EXIT C', u'category': u'Building', u'y': u'30412.5744', u'x': u'30434.3890'}, {u'searchval': u'CITY HALL/ESPLANADE MRT STATION     EXIT D', u'category': u'Building', u'y': u'30367.6908', u'x': u'30424.1965'}, {u'searchval': u'CITY HALL/ESPLANADE MRT STATION EXIT E', u'category': u'Building', u'y':     u'30479.6293', u'x': u'30394.6855'}]
    >>>

Queries return a OneMapResult object, containing one or more `OneMapResultItem`s

    >>> geo = OM.geocode("%s,%s" % (res[0]['x'], res[0]['y']))
    >>> type(geo)
    <class 'core.ext.onemap.OneMapResult'>
    >>>
    >>> geo
    [{u'buildingname': u'CITY HALL', 'y': 30338.9616, u'block': u'3', u'postalcode': u'178958', 'x': 30047.2715, u'road': u"SAINT ANDREW'S ROAD"}, {u'buildingname': u'THE ADELPHI',     'y': 30398.6047, u'block': u'1', u'postalcode': u'179803', 'x': 29987.9521, u'road': u'COLEMAN STREET'}, {u'buildingname': u'THE OLD SUPREME COURT BUILDING', 'y': 30253.3835,     u'block': u'1', u'postalcode': u'178957', 'x': 30025.5209, u'road': u"SAINT ANDREW'S ROAD"}, {u'buildingname': u'SUPREME COURT BUILDING', 'y': 30322.8247, u'block': u'1',     u'postalcode': u'178879', 'x': 29938.7931, u'road': u'SUPREME COURT LANE'}, {u'buildingname': u'FORMER SUPREME COURT BUILDING', 'y': 30250.6217, u'block': u'1', u'postalcode':     u'178957', 'x': 29985.2869, u'road': u"SAINT ANDREW'S ROAD"}]
    >>>

Queries can return many results, so `.filter(key=value)` allows you to quickly filter by a particular value

    >>> geo.filter(buildingname='CITY HALL')
    [{u'buildingname': u'CITY HALL', 'y': 30338.9616, u'block': u'3', u'postalcode': u'178958', 'x': 30047.2715, u'road': u"SAINT ANDREW'S ROAD"}]
    >>>
    >>> geo.filter(block='1')
    [{u'buildingname': u'THE ADELPHI', 'y': 30398.6047, u'block': u'1', u'postalcode': u'179803', 'x': 29987.9521, u'road': u'COLEMAN STREET'}, {u'buildingname': u'THE OLD SUPREME     COURT BUILDING', 'y': 30253.3835, u'block': u'1', u'postalcode': u'178957', 'x': 30025.5209, u'road': u"SAINT ANDREW'S ROAD"}, {u'buildingname': u'SUPREME COURT BUILDING', 'y':     30322.8247, u'block': u'1', u'postalcode': u'178879', 'x': 29938.7931, u'road': u'SUPREME COURT LANE'}, {u'buildingname': u'FORMER SUPREME COURT BUILDING', 'y': 30250.6217,     u'block': u'1', u'postalcode': u'178957', 'x': 29985.2869, u'road': u"SAINT ANDREW'S ROAD"}]
    >>>
    >>> type(geo[0])
    <class 'core.ext.onemap.OneMapResultItem'>
    >>>
    >>> print geo[0]
    {u'buildingname': u'CITY HALL', 'y': 30338.9616, u'block': u'3', u'postalcode': u'178958', 'x': 30047.2715, u'road': u"SAINT ANDREW'S ROAD"}
    >>>

Feeling lucky? `.resolve()` cuts to the chase and returns you the first result it gets, or, raises an exception

    >>>
    >>> OM.resolve("the white house")
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "core/ext/onemap/__init__.py", line 280, in resolve
        raise OneMapError(res.error)
    core.ext.onemap.OneMapError: No result(s) found.
    >>>
    >>> res = OM.resolve("istana")
    >>> type(res)
    <type 'dict'>
    >>> res
    {u'buildingname': u'ISTANA', 'coordinates': [103.84309296124401, 1.3068716489030177], u'postalcode': u'238823', u'block': u'0', 'y': 32132.8209, 'x': 29087.8352, u'road':     u'ORCHARD ROAD'}


# SVY21

The OneMap API returns coordinates in the SVY21 format (instead of the more commonly found WGS84 lat,lng format)

There is a OneMap API that can be called to convert between these two projection systems (that hasn't been wrapped by this library yet).

However, if you'd like to be able to convert the points without hitting an external API, do check out this awesome opensource library

[https://github.com/cgcai/SVY21](https://github.com/cgcai/SVY21)

A copy of the Python version of the awesome SVY21 library has been included in this repo, but all credit goes to the team, naturally.
