from _pytest.python import raises
from requests import HTTPError
import httpretty

from solve360 import Solve360


__author__ = 'Daniel Nibon <daniel@nibon.se>'

crm = None


def setup_module():
    global crm
    crm = Solve360('email', 'token')


def test_init_solve_missing_cred():
    with raises(TypeError):
        Solve360()
    with raises(ValueError):
        Solve360(None, None)


def test_init_solve():
    Solve360('email', 'token')


def test_invalid_entity():
    with raises(ValueError):
        # noinspection PyProtectedMember
        crm._list(entity='invalid_entity')


def test_invalid_method():
    with raises(ValueError):
        # noinspection PyProtectedMember
        crm._request('invalid_method', 'localhost', (None, None), {})


@httpretty.activate
def test_list_ownership():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='ownership/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.list_ownership()
    assert response['status'] == 'success'


# --------------------------------------
# CONTACTS
# --------------------------------------

@httpretty.activate
def test_contact_create():
    httpretty.register_uri(httpretty.POST, crm.url.format(url='contacts/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    contact = crm.create_contact({'firstname': 'A', 'lastname': 'B'})
    assert contact['status'] == 'success'


@httpretty.activate
def test_contact_non_200():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='contacts/10000/'), status=404)
    with raises(HTTPError):
        crm.show_contact(10000)


@httpretty.activate
def test_contact_create_categories():
    httpretty.register_uri(httpretty.POST, crm.url.format(url='contacts/categories/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    category = crm.create_contacts_category('C1')
    assert category['status'] == 'success'


@httpretty.activate
def test_contact_list_categories():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='contacts/categories/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    categories = crm.list_contacts_categories()
    assert categories['status'] == 'success'


@httpretty.activate
def test_show_contact():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='contacts/131/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    contact = crm.show_contact(131)
    assert contact['status'] == 'success'


@httpretty.activate
def test_update_contact():
    httpretty.register_uri(httpretty.PUT, crm.url.format(url='contacts/151/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    contact = crm.update_contact(151, {'lastname': 'D'})
    assert contact['status'] == 'success'


@httpretty.activate
def test_list_contacts():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='contacts/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    contacts = crm.list_contacts()
    assert contacts['status'] == 'success'


@httpretty.activate
def test_list_contacts_paginate_stop_on_pages():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='contacts/'),
                           responses=[
                               httpretty.Response(body='{"status": "success", "count": 3,'
                                                       ' "obj1": []}',
                                                  content_type='application/json'),
                               httpretty.Response(body='{"status": "success", "count": 3,'
                                                       ' "obj2": []}',
                                                  content_type='application/json'),
                               httpretty.Response(body='{"status": "success", "count": 3,'
                                                       ' "obj3": []}',
                                                  content_type='application/json')
                           ])
    contacts = crm.list_contacts(limit=1, pages=2)
    assert contacts['status'] == 'success'
    assert contacts['count'] == 3
    assert contacts['obj1'] == []
    assert contacts['obj2'] == []
    assert 'obj3' not in contacts
    assert len(contacts) == 2 + 2  # 'status' + 'count' + <results>


@httpretty.activate
def test_list_contacts_paginate_stop_on_objects():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='contacts/'),
                           responses=[
                               httpretty.Response(body='{"status": "success", "count": 2,'
                                                       ' "obj1": [],  "obj2": []}',
                                                  content_type='application/json'),
                               httpretty.Response(body='{"status": "success", "count": 2,'
                                                       ' "obj3": [], "obj4": []}',
                                                  content_type='application/json')
                           ])
    contacts = crm.list_contacts(limit=2, pages=3)
    assert contacts['status'] == 'success'
    assert contacts['count'] == 2
    assert contacts['obj1'] == []
    assert contacts['obj2'] == []
    assert 'obj3' not in contacts
    assert 'obj4' not in contacts
    assert len(contacts) == 2 + 2  # 'status' + 'count' + <results>


@httpretty.activate
def test_contact_activity_create():
    httpretty.register_uri(httpretty.POST, crm.url.format(url='contacts/note/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.create_contact_activity(131, 'note', {'details': 'test'})
    assert response['status'] == 'success'


@httpretty.activate
def test_contact_activity_update():
    httpretty.register_uri(httpretty.PUT, crm.url.format(url='contacts/note/111/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.update_contact_activity('note', 111, {'details': 'test2'})
    assert response['status'] == 'success'


@httpretty.activate
def test_contact_activity_destroy():
    httpretty.register_uri(httpretty.DELETE, crm.url.format(url='contacts/note/112/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.destroy_contact_activity('note', 112)
    assert response['status'] == 'success'


@httpretty.activate
def test_contact_destroy():
    httpretty.register_uri(httpretty.DELETE, crm.url.format(url='contacts/151/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    contact = crm.destroy_contact(151)
    assert contact['status'] == 'success'


@httpretty.activate
def test_list_contacts_fields():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='contacts/fields/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    fields = crm.list_contacts_fields()
    assert fields['status'] == 'success'


@httpretty.activate
def test_list_contacts_categories():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='contacts/categories/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    categories = crm.list_contacts_categories()
    assert categories['status'] == 'success'


# --------------------------------------
# COMPANIES
# --------------------------------------


@httpretty.activate
def test_company_create():
    httpretty.register_uri(httpretty.POST, crm.url.format(url='companies/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    contact = crm.create_company({'firstname': 'A', 'lastname': 'B'})
    assert contact['status'] == 'success'


@httpretty.activate
def test_contact_non_200():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='companies/10000/'), status=404)
    with raises(HTTPError):
        crm.show_company(10000)


@httpretty.activate
def test_company_create_categories():
    httpretty.register_uri(httpretty.POST, crm.url.format(url='companies/categories/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    category = crm.create_company_category('C1')
    assert category['status'] == 'success'


@httpretty.activate
def test_company_list_categories():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='companies/categories/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    categories = crm.list_companies_categories()
    assert categories['status'] == 'success'


@httpretty.activate
def test_show_company():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='companies/131/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.show_company(131)
    assert response['status'] == 'success'


@httpretty.activate
def test_update_company():
    httpretty.register_uri(httpretty.PUT, crm.url.format(url='companies/151/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.update_company(151, {'lastname': 'D'})
    assert response['status'] == 'success'


@httpretty.activate
def test_list_companies():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='companies/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.list_companies()
    assert response['status'] == 'success'


@httpretty.activate
def test_company_activity_create():
    httpretty.register_uri(httpretty.POST, crm.url.format(url='companies/note/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.create_company_activity(131, 'note', {'details': 'test'})
    assert response['status'] == 'success'


@httpretty.activate
def test_company_activity_update():
    httpretty.register_uri(httpretty.PUT, crm.url.format(url='companies/note/111/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.update_company_activity('note', 111, {'details': 'test2'})
    assert response['status'] == 'success'


@httpretty.activate
def test_company_activity_destroy():
    httpretty.register_uri(httpretty.DELETE, crm.url.format(url='companies/note/112/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.destroy_company_activity('note', 112)
    assert response['status'] == 'success'


@httpretty.activate
def test_company_destroy():
    httpretty.register_uri(httpretty.DELETE, crm.url.format(url='companies/151/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.destroy_company(151)
    assert response['status'] == 'success'


@httpretty.activate
def test_list_companies_fields():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='companies/fields/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    fields = crm.list_companies_fields()
    assert fields['status'] == 'success'


@httpretty.activate
def test_list_companies_categories():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='companies/categories/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    categories = crm.list_companies_categories()
    assert categories['status'] == 'success'


# --------------------------------------
# PROJECTBLOGS
# --------------------------------------


@httpretty.activate
def test_projectblog_create():
    httpretty.register_uri(httpretty.POST, crm.url.format(url='projectblogs/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.create_projectblog({'firstname': 'A', 'lastname': 'B'})
    assert response['status'] == 'success'


@httpretty.activate
def test_projectblog_non_200():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='projectblogs/10000/'), status=404)
    with raises(HTTPError):
        crm.show_projectblog(10000)


@httpretty.activate
def test_projectblog_create_categories():
    httpretty.register_uri(httpretty.POST, crm.url.format(url='projectblogs/categories/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    category = crm.create_projectblog_category('C1')
    assert category['status'] == 'success'


@httpretty.activate
def test_projectblog_list_categories():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='projectblogs/categories/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    categories = crm.list_projectblogs_categories()
    assert categories['status'] == 'success'


@httpretty.activate
def test_show_projectblog():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='projectblogs/131/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.show_projectblog(131)
    assert response['status'] == 'success'


@httpretty.activate
def test_update_projectblog():
    httpretty.register_uri(httpretty.PUT, crm.url.format(url='projectblogs/151/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.update_projectblog(151, {'lastname': 'D'})
    assert response['status'] == 'success'


@httpretty.activate
def test_list_projectblogs():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='projectblogs/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    projectblogs = crm.list_projectblogs()
    assert projectblogs['status'] == 'success'


@httpretty.activate
def test_projectblog_activity_create():
    httpretty.register_uri(httpretty.POST, crm.url.format(url='projectblogs/note/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.create_projectblog_activity(131, 'note', {'details': 'test'})
    assert response['status'] == 'success'


@httpretty.activate
def test_projectblog_activity_update():
    httpretty.register_uri(httpretty.PUT, crm.url.format(url='projectblogs/note/111/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.update_projectblog_activity('note', 111, {'details': 'test2'})
    assert response['status'] == 'success'


@httpretty.activate
def test_projectblog_activity_destroy():
    httpretty.register_uri(httpretty.DELETE, crm.url.format(url='projectblogs/note/112/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.destroy_projectblog_activity('note', 112)
    assert response['status'] == 'success'


@httpretty.activate
def test_projectblog_destroy():
    httpretty.register_uri(httpretty.DELETE, crm.url.format(url='projectblogs/151/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.destroy_projectblog(151)
    assert response['status'] == 'success'


@httpretty.activate
def test_list_projectblogs_fields():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='projectblogs/fields/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    fields = crm.list_projectblogs_fields()
    assert fields['status'] == 'success'


@httpretty.activate
def test_list_projectblogs_categories():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='projectblogs/categories/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    categories = crm.list_projectblogs_categories()
    assert categories['status'] == 'success'


# --------------------------------------
# REPORTS
# --------------------------------------

@httpretty.activate
def test_report_nextaction():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='report/nextactions/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.show_report_nextactions(filter_=0)
    assert response['status'] == 'success'


@httpretty.activate
def test_report_calendar():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='report/calendar/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.show_report_calendar('2014-01-01', '2014-02-01')
    assert response['status'] == 'success'


@httpretty.activate
def test_report_followup():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='report/followups/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.show_report_followups(responsible=0)
    assert response['status'] == 'success'


@httpretty.activate
def test_report_opportunities():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='report/opportunities/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.show_report_opportunities(filter_=0)
    assert response['status'] == 'success'


@httpretty.activate
def test_report_activities():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='report/activities/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.show_report_activities('2014-01-01', '2014-02-01', 'updated')
    assert response['status'] == 'success'


@httpretty.activate
def test_report_timetracking():
    httpretty.register_uri(httpretty.GET, crm.url.format(url='report/timetracking/'),
                           body='{"status": "success"}',
                           content_type='application/json')
    response = crm.show_report_timetracking('2014-01-01', '2014-02-01', 'updated')
    assert response['status'] == 'success'
