#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import requests
try:
    import simplejson as json
except ImportError:
    import json

__author__ = 'Daniel Nibon <daniel@nibon.se>'

"""
Wrapper for norada solve360 API.
http://norada.com/answers/api/external_api_introduction
"""

LIST_MAX_LIMIT = 5000  # Defined max limit for _list operation

ENTITY_CONTACT = 'contacts'
ENTITY_COMPANY = 'companies'
ENTITY_PROJECTBLOG = 'projectblogs'

VALID_ENTITIES = [ENTITY_COMPANY, ENTITY_CONTACT, ENTITY_PROJECTBLOG]

ERR_MSG_VALID_ENTITIES = 'Invalid entity. Valid once are: {entities}' \
    .format(entities=VALID_ENTITIES)
ERR_MSG_INVALID_CRED = 'User and token required'


def valid_entity(fn):
    """Decorator to validate a valid entity type is
    always given before communicating with solve"""

    def fn2(*args, **kwargs):
        if kwargs.get('entity') not in VALID_ENTITIES:
            raise ValueError(ERR_MSG_VALID_ENTITIES)
        return fn(*args, **kwargs)

    return fn2


class Solve360():
    """Solve360 API wrapper class."""

    def __init__(self, user, token, url='https://secure.solve360.com/{url}'):
        if not user or not token:
            raise ValueError(ERR_MSG_INVALID_CRED)
        self.auth = (user, token)
        self.url = url
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json'}

    @staticmethod
    def _request(method, url, auth, headers={}, data=None):
        """Performs the given request and returns the parsed json response.
        In case of none 2XX response codes a HTTPError is raised.
        Any given data is converted to json."""
        if data:
            data = json.dumps(data)
        method = method.lower()
        if method not in ['get', 'post', 'put', 'delete']:
            raise ValueError('Invalid method {method}'.format(method=method))
        kwargs = {'auth': auth, 'headers': headers, 'data': data}
        response = getattr(requests, method)(url, **kwargs)
        response.raise_for_status()
        return response.json()

    @valid_entity
    def _create(self, payload, entity=None):
        """Create a new entity with payload."""
        return self._request('post',
                             self.url.format(url='{type}/'.format(type=entity)),
                             self.auth,
                             self.headers,
                             data=payload)

    @valid_entity
    def _update(self, uid, payload, entity=None):
        """Updates given entity with payload."""
        return self._request('put',
                             self.url.format(url='{type}/{uid}/'.format(type=entity, uid=uid)),
                             self.auth,
                             self.headers,
                             data=payload)

    @valid_entity
    def _show(self, uid, entity=None):
        """Show detailed information about entity with given ID."""
        return self._request('get',
                             self.url.format(url='{type}/{uid}/'.format(type=entity, uid=uid)),
                             self.auth,
                             self.headers)

    @valid_entity
    def _destroy(self, uid, entity=None):
        """Delete the entity with given ID."""
        return self._request('delete',
                             self.url.format(url='{type}/{uid}/'.format(type=entity, uid=uid)),
                             self.auth,
                             self.headers)

    @valid_entity
    def _list(self, entity=None, **kwargs):
        """List entities.  kwargs may include any optional parameter
        according to api documentation. """
        # Filter out None values
        payload = {k: v for k, v in kwargs.items() if v or v == 0}
        qs = urllib.urlencode(payload)

        return self._request('get',
                             self.url.format(url='{type}/?{qs}'.format(type=entity, qs=qs)),
                             self.auth,
                             self.headers)

    @valid_entity
    def _create_categories(self, name, entity=None):
        """Creates a category tag for type entity."""
        return self._request('post',
                             self.url.format(url='{type}/categories/'.format(type=entity)),
                             self.auth,
                             self.headers,
                             data={'name': name})

    @valid_entity
    def _list_categories(self, entity=None):
        """List category tags for type entity."""
        return self._request('get',
                             self.url.format(url='{type}/categories/'.format(type=entity)),
                             self.auth,
                             self.headers)

    @valid_entity
    def _list_fields(self, entity=None):
        """List fields for type entity."""
        return self._request('get',
                             self.url.format(url='{type}/fields/'.format(type=entity)),
                             self.auth,
                             self.headers)

    def list_ownership(self):
        """List available users and workgroups."""
        return self._request('get',
                             self.url.format(url='ownership/'),
                             self.auth,
                             self.headers)

    @valid_entity
    def _create_activity(self, parent, activity, payload, entity=None):
        """Creates a new activity linked to a parent item.
        See http://norada.com/answers/api/external_api_reference_contacts
        for availiable activities."""
        _payload = dict()
        _payload['parent'] = parent
        _payload['data'] = payload
        return self._request('post',
                             self.url.format(url='{type}/{activity}/'.format(type=entity,
                                                                             activity=activity)),
                             self.auth,
                             self.headers,
                             data=_payload)

    @valid_entity
    def _update_activity(self, activity, uid, payload, entity=None):
        """Updates an activity with uid."""
        _payload = dict()
        _payload['data'] = payload
        return self._request('put',
                             self.url.format(url='{type}/{activity}/{uid}/'.format(type=entity,
                                                                                   activity=activity,
                                                                                   uid=uid)),
                             self.auth,
                             self.headers,
                             data=_payload)

    @valid_entity
    def _destroy_activity(self, activity, uid, entity=None):
        """Deletes an activity with uid."""
        return self._request('delete',
                             self.url.format(url='{type}/{activity}/{uid}/'.format(type=entity,
                                                                                   activity=activity,
                                                                                   uid=uid)),
                             self.auth,
                             self.headers)

    # Contacts

    def create_contact(self, payload):
        return self._create(payload, entity=ENTITY_CONTACT)

    def show_contact(self, uid):
        return self._show(uid, entity=ENTITY_CONTACT)

    def update_contact(self, uid, payload):
        return self._update(uid, payload, entity=ENTITY_CONTACT)

    def destroy_contact(self, uid):
        return self._destroy(uid, entity=ENTITY_CONTACT)

    def list_contacts(self, **kwargs):
        return self._list(entity=ENTITY_CONTACT, **kwargs)

    def create_contacts_category(self, name):
        return self._create_categories(name, entity=ENTITY_CONTACT)

    def list_contacts_categories(self):
        return self._list_categories(entity=ENTITY_CONTACT)

    def list_contacts_fields(self):
        return self._list_fields(entity=ENTITY_CONTACT)

    def create_contact_activity(self, parent, activity, payload):
        return self._create_activity(parent, activity, payload, entity=ENTITY_CONTACT)

    def update_contact_activity(self, activity, uid, payload):
        return self._update_activity(activity, uid, payload, entity=ENTITY_CONTACT)

    def destroy_contact_activity(self, activity, uid):
        return self._destroy_activity(activity, uid, entity=ENTITY_CONTACT)

    # Companies

    def create_company(self, payload):
        return self._create(payload, entity=ENTITY_COMPANY)

    def show_company(self, uid):
        return self._show(uid, entity=ENTITY_COMPANY)

    def update_company(self, uid, payload):
        return self._update(uid, payload, entity=ENTITY_COMPANY)

    def destroy_company(self, uid):
        return self._destroy(uid, entity=ENTITY_COMPANY)

    def list_companies(self, **kwargs):
        return self._list(entity=ENTITY_COMPANY, **kwargs)

    def create_company_category(self, name):
        return self._create_categories(name, entity=ENTITY_COMPANY)

    def list_companies_categories(self):
        return self._list_categories(entity=ENTITY_COMPANY)

    def list_companies_fields(self):
        return self._list_fields(entity=ENTITY_COMPANY)

    def create_company_activity(self, parent, activity, payload):
        return self._create_activity(parent, activity, payload, entity=ENTITY_COMPANY)

    def update_company_activity(self, activity, uid, payload):
        return self._update_activity(activity, uid, payload, entity=ENTITY_COMPANY)

    def destroy_company_activity(self, activity, uid):
        return self._destroy_activity(activity, uid, entity=ENTITY_COMPANY)

    # Projectblogs

    def create_projectblog(self, payload):
        return self._create(payload, entity=ENTITY_PROJECTBLOG)

    def show_projectblog(self, uid):
        return self._show(uid, entity=ENTITY_PROJECTBLOG)

    def update_projectblog(self, uid, payload):
        return self._update(uid, payload, entity=ENTITY_PROJECTBLOG)

    def destroy_projectblog(self, uid):
        return self._destroy(uid, entity=ENTITY_PROJECTBLOG)

    def list_projectblogs(self, **kwargs):
        return self._list(entity=ENTITY_PROJECTBLOG, **kwargs)

    def create_projectblog_category(self, name):
        return self._create_categories(name, entity=ENTITY_PROJECTBLOG)

    def list_projectblogs_categories(self):
        return self._list_categories(entity=ENTITY_PROJECTBLOG)

    def list_projectblogs_fields(self):
        return self._list_fields(entity=ENTITY_PROJECTBLOG)

    def create_projectblog_activity(self, parent, activity, payload):
        return self._create_activity(parent, activity, payload, entity=ENTITY_PROJECTBLOG)

    def update_projectblog_activity(self, activity, uid, payload):
        return self._update_activity(activity, uid, payload, entity=ENTITY_PROJECTBLOG)

    def destroy_projectblog_activity(self, activity, uid):
        return self._destroy_activity(activity, uid, entity=ENTITY_PROJECTBLOG)

    # Reports

    def _show_report(self, report_type, **kwargs):
        """ Show reports.
        See http://norada.com/answers/api/external_api_reference_activityreports
        for examples of reports and available parameters. """
        # Filter out None values
        payload = {k: v for k, v in kwargs.items() if v or v == 0}
        if 'filter_' in payload:
            payload['filter'] = payload['filter_']
            del payload['filter_']
        qs = urllib.urlencode(payload)
        return self._request('get',
                             self.url.format(url='report/{type}/?{qs}'.format(type=report_type, qs=qs)),
                             self.auth,
                             self.headers)

    def show_report_nextactions(self, filter_, **kwargs):
        kwargs['filter_'] = filter_
        return self._show_report('nextactions', **kwargs)

    def show_report_calendar(self, start, end, **kwargs):
        kwargs['start'] = start
        kwargs['end'] = end
        return self._show_report('calendar', **kwargs)

    def show_report_followups(self, **kwargs):
        return self._show_report('followups', **kwargs)

    def show_report_opportunities(self, filter_, **kwargs):
        kwargs['filter_'] = filter_
        return self._show_report('opportunities', **kwargs)

    def show_report_activities(self, start, end, last, **kwargs):
        kwargs['start'] = start
        kwargs['end'] = end
        kwargs['last'] = last
        return self._show_report('activities', **kwargs)

    def show_report_timetracking(self, start, end, last, **kwargs):
        kwargs['start'] = start
        kwargs['end'] = end
        kwargs['last'] = last
        return self._show_report('activities', **kwargs)

