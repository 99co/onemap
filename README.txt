=======
OneMap
=======

This library provides a thin wrapper over the OneMapSG API (http://www.onemap.sg/api/help/)

You'll need an access key from OneMap before you'll be able to use the OneMap API

    Examples::

        >>> # Initialising
        >>> from onemap import OneMap
        >>> access_key = "onemap_api_access_key"
        >>> OM = OneMap(access_key)
        >>>
        >>> # Search by address
        >>> OM.search_address("lucky plaza")
        {u'SearchResults': [{u'PageCount': u'0'}, {u'SEARCHVAL': u'LUCKY PLAZA', u'CATEGORY': u'Building', u'Y': u'31866.4964', u'X': u'28076.4100'}]}
        >>>
        >>> # Search by theme
        >>> results =  OM.search_theme("childcare")
        >>> results
        {u'SearchResults': [{u'PageCount': u'1'}, {u'SEARCHVAL': u'3-IN-1 FAMILY CENTRE', u'CATEGORY': u'Family', u'THEME': u'childcare', u'Y': u'37091.9086', u'X': u'41203.8054'}, {u'SEARCHVAL': u'A & J CHILD CARE CENTRE', u'CATEGORY': u'Family', u'THEME': u'childcare', u'Y': u'39828.9045', u'X': u'34733.2933'}, {u'SEARCHVAL': u'ABLELAND @ TAMPINES PTE. LTD.', u'CATEGORY': u'Family', u'THEME': u'childcare', u'Y': u'37412.2497', u'X': u'40664.6250'}, {u'SEARCHVAL': u'ACADEMY KIDZ INC PTE. LTD.', u'CATEGORY': u'Family', u'THEME': u'childcare', u'Y': u'33260.4607', u'X': u'31336.3859'}, {u'SEARCHVAL': u'ACADEMY KIDZ INC PTE. LTD.', u'CATEGORY': u'Family', u'THEME': u'childcare', u'Y': u'33913.5338', u'X': u'37888.1394'}, {u'SEARCHVAL': u'ACE @ WORK CHILDCARE PTE LTD', u'CATEGORY': u'Family', ...}]}
        >>>
        >>> # Second page of search results, without geo data applicable to all search methods
        >>> results_page_two = OM.search_theme("childcare", page=2, with_geo=False)
        >>> results_page_two
        {u'SearchResults': [{u'PageCount': u'1'}, {u'SEARCHVAL': u'AGAPE KIDS CAMPUS LLP', u'CATEGORY': u'Family', u'THEME': u'childcare'}, {u'SEARCHVAL': u'AGAPE LITTLE UNI (KALLANG) PTE. LTD.', u'CATEGORY': u'Family', u'THEME': u'childcare'}, {u'SEARCHVAL': u'AGAPE LITTLE UNI @ CENTRAL PTE. LTD.', u'CATEGORY': u'Family', u'THEME': u'childcare'}, {u'SEARCHVAL': u'AGAPE LITTLE UNI @ SERANGOON PTE. LTD.', u'CATEGORY': u'Family', u'THEME': u'childcare'}, {u'SEARCHVAL': u'AGAPE LITTLE UNI @ TAMPINES PTE. LTD.', u'CATEGORY': u'Family', u'THEME': u'childcare'},...]}
        >>>
        >>> # Reverse geocode
        >>> OM.geocode("103.8333086,1.3043267", buffer=20)
        {u'GeocodeInfo': [{u'BUILDINGNAME': u'LUCKY PLAZA', u'YCOORD': 31854.8977, u'BLOCK': u'304', u'POSTALCODE': u'238863', u'ROAD': u'ORCHARD ROAD', u'XCOORD': 28017.0234}, {u'BUILDINGNAME': u'LUCKY PLAZA', u'YCOORD': 31876.6461, u'BLOCK': u'304', u'POSTALCODE': u'238863', u'ROAD': u'ORCHARD ROAD', u'XCOORD': 28070.0637}]}
        >>>



SVY21
========

The OneMap API returns coordinates in the SVY21 format (instead of the more commonly found WGS84 lat,lng format)

There is a OneMap API that can be called to convert between these two projection systems (that hasn't been wrapped by this library yet).

However, if you'd like to be able to convert the points without hitting an external API, do check out this awesome opensource library

`https://github.com/cgcai/SVY21 <https://github.com/cgcai/SVY21>`_
