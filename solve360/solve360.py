"""
Wrapper for norada solve360 API.

http://norada.com/answers/api/external_api_introduction
"""
__author__ = 'Daniel Nibon <daniel@nibon.se>'

import sys
import json

if sys.version_info[0] == 3:
    import urllib.parse as urllib_
else:
    import urllib as urllib_

import requests


LIST_MAX_LIMIT = 5000  # Defined max limit for _list operation

ENTITY_CONTACT = 'contacts'
ENTITY_COMPANY = 'companies'
ENTITY_PROJECTBLOG = 'projectblogs'

VALID_ENTITIES = [ENTITY_COMPANY, ENTITY_CONTACT, ENTITY_PROJECTBLOG]

VALID_LIST_PARAM = ['layout', 'fieldlist', 'categories', 'filtermode',
                    'filtervalue', 'special', 'searchmode', 'searchvalue',
                    'limit', 'start', 'sortfield', 'sortdir']

ERR_MSG_VALID_ENTITIES = 'Invalid entity. Valid once are: {entities}' \
    .format(entities=VALID_ENTITIES)
ERR_MSG_INVALID_CRED = 'User and token required'


def valid_entity(fun):
    """Validates that a valid Entity is set."""

    def fn2(*args, **kwargs):
        """Validates that a valid Entity is set wrapper function."""
        if kwargs.get('entity') not in VALID_ENTITIES:
            raise ValueError(ERR_MSG_VALID_ENTITIES)
        return fun(*args, **kwargs)

    return fn2


class Solve360(object):  # pylint: disable=R0904
    """Solve360 API wrapper class."""

    def __init__(self, user, token, url='https://secure.solve360.com/{url}'):
        """Sets given credentials and url for solve360."""
        if not user or not token:
            raise ValueError(ERR_MSG_INVALID_CRED)
        self.auth = (user, token)
        self.url = url
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json'}

    @staticmethod
    def _request(method, url, auth, headers, data=None):
        """Performs the given request and returns the parsed json response.
        In case of none 2XX response codes a HTTPError is raised.
        Any given data is converted to json."""
        if data:
            data = json.dumps(data)
        method = method.lower()
        if method not in ['get', 'post', 'put', 'delete']:
            raise ValueError('Invalid method {method}'.format(method=method))
        response = getattr(requests, method)(url,
                                             auth=auth,
                                             headers=headers,
                                             data=data)
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
        url = self.url.format(url='{type}/{uid}/'.format(type=entity, uid=uid))
        return self._request('put',
                             url,
                             self.auth,
                             self.headers,
                             data=payload)

    @valid_entity
    def _show(self, uid, entity=None):
        """Show detailed information about entity with given ID."""
        url = self.url.format(url='{type}/{uid}/'.format(type=entity, uid=uid))
        return self._request('get',
                             url,
                             self.auth,
                             self.headers)

    @valid_entity
    def _destroy(self, uid, entity=None):
        """Delete the entity with given ID."""
        url = self.url.format(url='{type}/{uid}/'.format(type=entity, uid=uid))
        return self._request('delete',
                             url,
                             self.auth,
                             self.headers)

    def _list_build_query(self, entity, **kwargs):
        """Builds the url and query for a list type entity request.
        The query might be updated when fetching incomplete set"""
        payload = dict((k, v) for k, v in kwargs.items()
                       if (v or v == 0) and k in VALID_LIST_PARAM)
        query = urllib_.urlencode(payload)
        url = self.url.format(url='{type}/?{query}'.format(type=entity,
                                                           query=query))
        return url

    @valid_entity
    def _list(self, entity=None, **kwargs):
        """List entities."""
        response = {}
        pages = kwargs.get('pages', 1)
        if not type(pages) == int or not pages > 0:
            raise ValueError('Parameter <pages> must be a positive number.')
        while pages > 0:
            _response = self._request('get',
                                      self._list_build_query(entity, **kwargs),
                                      self.auth,
                                      self.headers)
            response.update(_response)
            kwargs['start'] = kwargs.get('start', 0) + kwargs.get('limit', 0)
            pages -= 1
            # Checking response entities excluding keys 'count' and 'status'
            if 'count' in response and response['count'] == len(response) - 2:
                break  # We got all objects

        return response

    @valid_entity
    def _create_categories(self, name, entity=None):
        """Creates a category tag for type entity."""
        url = self.url.format(url='{type}/categories/'.format(type=entity))
        return self._request('post',
                             url,
                             self.auth,
                             self.headers,
                             data={'name': name})

    @valid_entity
    def _list_categories(self, entity=None):
        """List category tags for type entity."""
        url = self.url.format(url='{type}/categories/'.format(type=entity))
        return self._request('get',
                             url,
                             self.auth,
                             self.headers)

    @valid_entity
    def _list_fields(self, entity=None):
        """List fields for type entity."""
        url = self.url.format(url='{type}/fields/'.format(type=entity))
        return self._request('get',
                             url,
                             self.auth,
                             self.headers)

    def list_ownership(self):
        """List available users and workgroups."""
        return self._request('get',
                             self.url.format(url='ownership/'),
                             self.auth,
                             self.headers)

    @valid_entity
    def _create_activity(self, parent, segment, payload, entity=None):
        """Creates a new activity linked to a parent entity.

        See http://norada.com/answers/api/external_api_reference_contacts
        for available activities.
        """
        _payload = dict()
        _payload['parent'] = parent
        _payload['data'] = payload
        url = self.url.format(url='{type}/{segment}/'
                              .format(type=entity,
                                      segment=segment))
        return self._request('post',
                             url,
                             self.auth,
                             self.headers,
                             data=_payload)

    @valid_entity
    def _update_activity(self, segment, activity_id, payload, entity=None):
        """Updates an activity with id ``activity_id``."""
        _payload = dict()
        _payload['data'] = payload
        url = self.url.format(url='{type}/{segment}/{id}/'
                              .format(type=entity,
                                      segment=segment,
                                      id=activity_id))
        return self._request('put',
                             url,
                             self.auth,
                             self.headers,
                             data=_payload)

    @valid_entity
    def _destroy_activity(self, segment, activity_id, entity=None):
        """Deletes an activity with id ``activity_id``."""
        url = self.url.format(url='{type}/{segment}/{id}/'
                              .format(type=entity,
                                      segment=segment,
                                      id=activity_id))
        return self._request('delete',
                             url,
                             self.auth,
                             self.headers)

    # Contacts

    def create_contact(self, payload):
        """Creates a new contact.

        :param payload: dict - Full or partial contact data to update.
        """
        return self._create(payload, entity=ENTITY_CONTACT)

    def show_contact(self, contact_id):
        """Shows a contact.

        Shows all data related to an existing contact
        including companies, related-to, category tags and
        all activities (excluding email messages).

        :param contact_id: int - id of the contact to update.
        """
        return self._show(contact_id, entity=ENTITY_CONTACT)

    def update_contact(self, contact_id, payload):
        """Updates an existing contact.

        :param contact_id: int - id of the contact to update.
        :param payload: dict - Full or partial contact data to update.
        """
        return self._update(contact_id, payload, entity=ENTITY_CONTACT)

    def destroy_contact(self, contact_id):
        """Destroys an existing contact.

        :param contact_id: int - id of the contact to destroy.
        """
        return self._destroy(contact_id, entity=ENTITY_CONTACT)

    def list_contacts(self, **kwargs):
        """List contacts that match the requested criteria.

        :param kwargs: dict - valid value is documented in method ``_list``.
        """
        return self._list(entity=ENTITY_CONTACT, **kwargs)

    def create_contacts_category(self, name):
        """Creates a contact category tag.

        :param name: Name for category.
        """
        return self._create_categories(name, entity=ENTITY_CONTACT)

    def list_contacts_categories(self):
        """List available contact category tags."""
        return self._list_categories(entity=ENTITY_CONTACT)

    def list_contacts_fields(self):
        """List available contact fields."""
        return self._list_fields(entity=ENTITY_CONTACT)

    def create_contact_activity(self, contact_id, segment, payload):
        """Creates a contact activity.

        :param contact_id: int - id of the contact to create the activity for.
        :param segment: str - type of segment. See ``_create_activity``.
        :param payload: dict - Activity data.
        """
        return self._create_activity(contact_id, segment, payload,
                                     entity=ENTITY_CONTACT)

    def update_contact_activity(self, segment, activity_id, payload):
        """Updates a contact activity.

        :param segment: str - type of segment. See ``_create_activity``.
        :param activity_id: int - id of the activity to update.
        :param payload: dict - Full or partial activity data to update.
        """
        return self._update_activity(segment, activity_id, payload,
                                     entity=ENTITY_CONTACT)

    def destroy_contact_activity(self, segment, activity_id):
        """Destroys a contact activity.

        :param segment: str - type of segment. See ``_create_activity``.
        :param activity_id: int - id of the activity to update.
        """
        return self._destroy_activity(segment, activity_id,
                                      entity=ENTITY_CONTACT)

    # Companies

    def create_company(self, payload):
        """Creates a new company.

        :param payload: dict - Full or partial company data to update.
        """
        return self._create(payload, entity=ENTITY_COMPANY)

    def show_company(self, company_id):
        """Shows a company.

        Shows all data related to an existing company
        including contacts, related-to, category tags and
        all activities (excluding email messages).

        :param company_id: int - id of the company to update.
        """
        return self._show(company_id, entity=ENTITY_COMPANY)

    def update_company(self, company_id, payload):
        """Updates an existing company.

        :param company_id: int - id of the company to update.
        :param payload: dict - Full or partial company data to update.
        """
        return self._update(company_id, payload, entity=ENTITY_COMPANY)

    def destroy_company(self, company_id):
        """Destroys an existing company.

        :param company_id: int - id of the company to destroy.
        """
        return self._destroy(company_id, entity=ENTITY_COMPANY)

    def list_companies(self, **kwargs):
        """List companies that match the requested criteria.

        :param kwargs: dict - valid value is documented in method ``_list``.
        """
        return self._list(entity=ENTITY_COMPANY, **kwargs)

    def create_company_category(self, name):
        """Creates a company category tag.

        :param name: Name for category.
        """
        return self._create_categories(name, entity=ENTITY_COMPANY)

    def list_companies_categories(self):
        """List available company category tags."""
        return self._list_categories(entity=ENTITY_COMPANY)

    def list_companies_fields(self):
        """List available company fields."""
        return self._list_fields(entity=ENTITY_COMPANY)

    def create_company_activity(self, company_id, segment, payload):
        """Creates a company activity.

        :param company_id: int - id of the company to create the activity for.
        :param segment: str - type of activity. See ``_create_activity``.
        :param payload: dict - Activity data.
        """
        return self._create_activity(company_id, segment, payload,
                                     entity=ENTITY_COMPANY)

    def update_company_activity(self, segment, activity_id, payload):
        """Updates a company activity.

        :param segment: int - type of segment. See ``_create_activity``.
        :param activity_id: str - id of the activity to update.
        :param payload: dict - Full or partial segment data to update.
        """
        return self._update_activity(segment, activity_id, payload,
                                     entity=ENTITY_COMPANY)

    def destroy_company_activity(self, segment, activity_id):
        """Destroys a company activity.

        :param segment: str - type of segment. See ``_create_activity``.
        :param activity_id: int - id of the segment to update.
        """
        return self._destroy_activity(segment, activity_id,
                                      entity=ENTITY_COMPANY)

    # Projectblogs

    def create_projectblog(self, payload):
        """Creates a new projectblog.

        :param payload: dict - Full or partial projectblog data to update.
        """
        return self._create(payload, entity=ENTITY_PROJECTBLOG)

    def show_projectblog(self, projectblog_id):
        """Shows a projectblog.

        Shows all data related to an existing projectblog
        including contacts, companies, related-to, category tags and
        all activities (excluding email messages).

        :param projectblog_id: int - id of the projectblog to update.
        """
        return self._show(projectblog_id, entity=ENTITY_PROJECTBLOG)

    def update_projectblog(self, projectblog_id, payload):
        """Updates an existing projectblog.

        :param projectblog_id: int - id of the projectblog to update.
        :param payload: dict - Full or partial projectblog data to update.
        """
        return self._update(projectblog_id, payload, entity=ENTITY_PROJECTBLOG)

    def destroy_projectblog(self, projectblog_id):
        """Destroys an existing projectblog.

        :param projectblog_id: int - id of the projectblog to destroy.
        """
        return self._destroy(projectblog_id, entity=ENTITY_PROJECTBLOG)

    def list_projectblogs(self, **kwargs):
        """List projectblogs that match the requested criteria.

        :param kwargs: dict - valid value is documented in method ``_list``.
        """
        return self._list(entity=ENTITY_PROJECTBLOG, **kwargs)

    def create_projectblog_category(self, name):
        """Creates a projectblog category tag.

        :param name: Name for category.
        """
        return self._create_categories(name, entity=ENTITY_PROJECTBLOG)

    def list_projectblogs_categories(self):
        """List available projectblog category tags."""
        return self._list_categories(entity=ENTITY_PROJECTBLOG)

    def list_projectblogs_fields(self):
        """List available projectblog fields."""
        return self._list_fields(entity=ENTITY_PROJECTBLOG)

    def create_projectblog_activity(self, projectblog_id, segment, payload):
        """Creates a projectblog activity.

        :param projectblog_id: int - the projectblog to create the activity for.
        :param segment: str - type of activity. See ``_create_activity``.
        :param payload: dict - Activity data.
        """
        return self._create_activity(projectblog_id, segment, payload,
                                     entity=ENTITY_PROJECTBLOG)

    def update_projectblog_activity(self, segment, activity_id, payload):
        """Updates a projectblog activity.

        :param segment: str - type of segment. See ``_create_activity``.
        :param activity_id: int - id of the activity to update.
        :param payload: dict - Full or partial segment data to update.
        """
        return self._update_activity(segment, activity_id, payload,
                                     entity=ENTITY_PROJECTBLOG)

    def destroy_projectblog_activity(self, segment, activity_id):
        """Destroys a projectblog activity.

        :param segment: str - type of segment. See ``_create_activity``.
        :param activity_id: int - id of the segment to update.
        """
        return self._destroy_activity(segment, activity_id,
                                      entity=ENTITY_PROJECTBLOG)

    # Reports

    def _show_report(self, report_type, **kwargs):
        """Show reports.

        :param report_type: str - Type of report.
        :param kwargs: dict - Search criteria.

        The Solve360 web interface does query all activities via XHR by default.

        Reference:
        http://norada.com/answers/api/external_api_reference_activityreports
        """
        # Filter out None values
        payload = dict((k, v) for k, v in kwargs.items() if v or v == 0)
        if 'filter_' in payload:
            payload['filter'] = payload['filter_']
            del payload['filter_']
        query = urllib_.urlencode(payload)
        url = self.url.format(url='report/{type}/?{query}'
                              .format(type=report_type,
                                      query=query))
        return self._request('get',
                             url,
                             self.auth,
                             self.headers)

    def show_report_nextactions(self, filter_, **kwargs):
        """List open tasks, events and milestones.

        :param filter_: (integer [user id, group id]), or
                        (integer [no one=0, anyone=<empty>]
        :param kwargs: dict - Search criteria.

        kwargs:
            due (string [now, next7, next30, nodate, or dateFrom,dateTo]), or
                 not sending due will not filter by date
            itemsdata (integer [0=do not include parent data,
                                1=include parent data])
        """
        kwargs['filter_'] = filter_
        return self._show_report('nextactions', **kwargs)

    def show_report_calendar(self, start, end, **kwargs):
        """List open tasks, events and milestones.

        :param start: date - Startdate in yyyy-mm-dd format
        :param end: date - Enddate in yyyy-mm-dd format
        :param kwargs: dict - Search criteria.

        kwargs:
            filter (integer [user id, group id]), or
            filter (integer [without attendees=0, anyone=<empty>]
            itemsdata (integer [0=do not include parent data,
                                1=include parent data])
        """
        kwargs['start'] = start
        kwargs['end'] = end
        return self._show_report('calendar', **kwargs)

    def show_report_followups(self, **kwargs):
        """List open follow-ups.

        :param kwargs: dict - Search criteria.

        kwargs:
            responsible (integer [user id, group id]), or
                        (integer [no one=0, anyone=<empty>]
            due (string [now, next7, next30, nodate, or dateFrom,dateTo]), or
                 not sending due will not filter by date
            itemsdata (integer [0=do not include parent data,
                                1=include parent data])
        """
        return self._show_report('followups', **kwargs)

    def show_report_opportunities(self, filter_, **kwargs):
        """Lists opportunities by user and status criteria.

        :param filter_: (integer [user id, group id]), or
                        (integer [no one=0, anyone=<empty>])
        :param kwargs: dict - Search criteria.

        kwargs:
            status (string [discussion, pending, won, lost, on-hold])
            due (string [now, next7, next30, nodate, or dateFrom,dateTo]), or
                not sending due will not filter by date
            itemsdata (integer [0=do not include parent data,
                                1=include parent data])
        """
        kwargs['filter_'] = filter_
        return self._show_report('opportunities', **kwargs)

    def show_report_activities(self, start, end, last='created', **kwargs):
        """List activities that have been created, modified,
        created or modified, or when specifying only tasks,
        completed, matching different search criteria.

        :param start: date - Startdate in yyyy-mm-dd format
        :param end: date - Enddate in yyyy-mm-dd format
        :param last: string - [created, updated, changed, completed]
        :param kwargs: dict - Search criteria.

        kwargs:
            types (integer [3, 4, 6, 14, 23, 24, 32, 73, 88])
                All activity types are queried by default, types are mapped as:
                note=3, event=4, followup=6, task=14, file=23,
                photo=24, opportunity=32, event (non-linked)=61,
                call log=73, scheduled email=88
            users (integer [group id, user id])
            categories (integer)
            itemtypes (integer [1, 2, 40])
            itemsdata (integer [0=do not include parent data,
                                1=include parent data])

        The Solve360 web interface does query all
        activities via XHR by default too.
        """
        kwargs['start'] = start
        kwargs['end'] = end
        kwargs['last'] = last
        if 'types' not in kwargs:
            kwargs['types'] = '73,4,6,3,14,32,88,23,24,61'
        return self._show_report('activities', **kwargs)

    def show_report_timetracking(self, start, end, last, **kwargs):
        """Lists time records matching a specific date range and status.

        :param start: date in yyyy-mm-dd format
        :param end: date in yyyy-mm-dd format
        :param last: string - [created, updated, changed, completed]
        :param kwargs: dict - Search criteria.

        kwargs:
            filter (string, [invoiced, billable, non-billable])
            itemtypes (integer [1, 2, 40])
            itemsdata (integer [0=do not include parent data,
                                1=include parent data])
        """
        kwargs['start'] = start
        kwargs['end'] = end
        kwargs['last'] = last
        return self._show_report('timetracking', **kwargs)

