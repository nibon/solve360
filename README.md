

# Solve360 API Python wrapper

Python wrapper for [Norada CRM Solve360](http://norada.com/) API. All current API operations are supported (2014-03-09).


## Solve360 API Documentation

http://norada.com/answers/api/external_api_introduction


## Installation

    $ pip install solve360


## Usage

    >>> from solve360 import Solve360
    >>> crm = Solve360(your_email, your_token)
    >>> crm.list_contacts(limit=10, start=0)
    {'status': 'success',
     'count': 2,
     '12345': {...},
     '12346': {...}}
    >>> crm.create_contact({'firstname': 'test', 'lastname': 'creation'})
    {'status': 'success',
     'item': {'id': 12347, ...},
     ...}
	>>> crm.show_report_activities('2014-03-05', '2014-03-11')
	u'66326826': {u'comments': [],
				   u'created': u'2014-03-05T08:48:07+00:00',
				   u'fields': {u'assignedto': u'88842777',
    			   u'assignedto_cn': u'John Doe',
    u'completed': u'0',
    u'duedate': u'2014-03-07T00:00:00+00:00',
    u'priority': u'0',
    u'remindtime': u'0',
	...}


## Error handling

All successful requests with `response.status_code == 2XX` will parse the json response body and only return the response data.

All invalid requests with `response.status_code == 4XX or 5XX` will raise an `requests.HTTPException` using requests `raise_for_status()` returning the complete stacktrace including server error message if available.


## Test

Edit `tests.py` and update variable `CRED_EMAIL` and `CRED_TOKEN` with your solve360 credentials. See [Norada API introduction](http://norada.com/answers/api/external_api_introduction) for more information how to obtain token.


Optionally set `CHANGE_CRM_STATE = True` to test operations that must be reversed manually. I.e. categories may be created through the API but no category destroy operation is available in the API.

    $ pip install pytest
    $ py.test solve360/tests.py


## Dependencies

* [requests](https://pypi.python.org/pypi/requests)

