

# Solve360 API Python wrapper

Python wrapper for [Norada CRM Solve360](http://norada.com/) API. All current API operations are supported (2014-08-03).


## Solve360 API Documentation

http://norada.com/answers/api/external_api_introduction


## Installation

    $ pip install solve360


## Usage

### Initiate solve object

    >>> from solve360 import Solve360
    >>> crm = Solve360(your_email, your_token)

### Get contacts

    >>> crm.list_contacts()
    {u'status': 'success',
     u'count': 2,
     u'12345': {...},
     u'12346': {...}}
     
### Get contacts - paginated

The solve360 API have a fixed upper limit on objects each list request will return, currently set to 5000.
To fetch more objects in a single request this wrapper offers an parameter `pages`. The request
will continue to fetch objects until either all objects are returned or the number of given
pages have been reached. 

    >>> contacts = crm.list_contacts(limit=solve360.LIST_MAX_LIMIT, pages=2)
    >>> contacts
    {u'status': 'success',
     u'count': 12000,
     u'12345': {...},
     u'12346': {...}}
    >>> len(contacts)
    10002  # Keys 'status' and 'count' plus 10000 contacts 

Parameter `pages` must be a positive number. There is currently no 
parameter that means fetches all objects disregarding how many there is. Just set `pages` to
a number high enough. 

### Show contact

    >>> crm.show_contact(12345)
    {u'status': 'success',
     u'id': 12345,
     u'fields': {...},
     ...}

### Create contact

    >>> crm.create_contact({'firstname': 'test', 'lastname': 'creation'})
    {'status': 'success',
     'item': {'id': 12347, ...},
     ...}

### Show report activities 

    >>> crm.show_report_activities('2014-03-05', '2014-03-11')
    {u'status': 'success', 
     u'66326826': {u'comments': [],
            u'created': u'2014-03-05T08:48:07+00:00',
            u'fields': {u'assignedto': u'88842777',
            u'assignedto_cn': u'John Doe',
            u'completed': u'0',
            u'duedate': u'2014-03-07T00:00:00+00:00',
            u'priority': u'0',
            u'remindtime': u'0',
        ...}
    }


## Error handling

Successful requests with `response.status_code == 2XX` will parse the json response body and only return the response data.

Invalid requests with `response.status_code == 4XX or 5XX` will raise an `requests.HTTPException` using requests `raise_for_status()` returning the complete stacktrace including server error message if available.


## Test

    $ pip install pytest httpretty
    $ py.test solve360/tests.py


## Dependencies

* [requests](https://pypi.python.org/pypi/requests)

### Dependencies Testing

* [pytest](https://pypi.python.org/pypi/pytest)
* [httpretty](https://pypi.python.org/pypi/httpretty)

