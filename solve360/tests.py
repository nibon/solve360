from requests import HTTPError
from solve360 import Solve360
import pytest

__author__ = 'Daniel Nibon <daniel@nibon.se>'

# Most API calls may be reversed by calling destroy on created entities.
# Some tests are irreversible such as creating categories which
# don't have any destroy operation. By setting the value below to
# True also operations that leave crm in a different state after
# running the test suite, will be included. At this time that
# include only creating new categories.
CHANGE_CRM_STATE = False

# Update CRED_EMAIL and CRED_TOKEN to perform live tests against solve360.
CRED_EMAIL = None
CRED_TOKEN = None

crm = None
test_contact = None
test_company = None
test_projectblog = None


def test_init_solve_missing_cred():
    with pytest.raises(TypeError):
        Solve360()
    with pytest.raises(ValueError):
        Solve360(None, None)


def test_init_solve():
    """Requires valid credentials for most remaining test cases."""
    global crm
    crm = Solve360(CRED_EMAIL, CRED_TOKEN)


def test_invalid_entity():
    with pytest.raises(ValueError):
        crm._list(entity='invalid_entity')


def test_invalid_method():
    with pytest.raises(ValueError):
        crm._request('invalid_method', 'localhost', (None, None), {})


# def test_init_solve_wrong_cred():
#     with pytest.raises(HTTPError):
#         crm_wrong_cred = Solve360('test@example.com', 'testing')
#         crm_wrong_cred.list_contacts(limit=1)


def test_contact_create():
    global test_contact
    contact = crm.create_contact({'firstname': 'A', 'lastname': 'B'})
    assert contact['status'] == 'success'
    test_contact = contact


def test_non_200():
    with pytest.raises(HTTPError):
        crm.show_contact(10000)


def test_contact_create_categories():
    if CHANGE_CRM_STATE:
        category1 = crm.create_contacts_category('C1')
        assert category1['status'] == 'success'


def test_contact_list_categories():
    categories = crm.list_contacts_categories()
    assert categories['status'] == 'success'


def test_show_contact():
    contact = crm.show_contact(test_contact['item']['id'])
    assert contact['status'] == 'success'


def test_update_contact():
    contact = crm.update_contact(test_contact['item']['id'], {'lastname': 'D'})
    assert contact['status'] == 'success'


def test_list_contacts():
    contacts = crm.list_contacts()
    assert contacts['status'] == 'success'


def test_contact_activity():
    activity = crm.create_contact_activity(test_contact['item']['id'], 'note', {'details': 'test'})
    activity_id = activity['id']
    assert activity['status'] == 'success'
    activity = crm.update_contact_activity('note', activity_id, {'details': 'test2'})
    assert activity['status'] == 'success'
    activity = crm.destroy_contact_activity('note', activity_id)
    assert activity['status'] == 'success'


def test_contact_destroy():
    contact = crm.destroy_contact(test_contact['item']['id'])
    assert contact['status'] == 'success'


def test_list_contacts_fields():
    fields = crm.list_contacts_fields()
    assert fields['status'] == 'success'


def test_list_contacts_categories():
    categories = crm.list_contacts_categories()
    assert categories['status'] == 'success'


# Companies

def test_company_create():
    global test_company
    company = crm.create_company({'name': 'A'})
    assert company['status'] == 'success'
    test_company = company


def test_company_create_categories():
    if CHANGE_CRM_STATE:
        category1 = crm.create_company_category('C1')
        assert category1['status'] == 'success'


def test_company_list_categories():
    categories = crm.list_companies_categories()
    assert categories['status'] == 'success'


def test_show_company():
    company = crm.show_company(test_company['item']['id'])
    assert company['status'] == 'success'


def test_update_company():
    company = crm.update_company(test_company['item']['id'], {'name': 'D'})
    assert company['status'] == 'success'


def test_list_companies():
    companies = crm.list_companies()
    assert companies['status'] == 'success'


def test_company_activity():
    activity = crm.create_company_activity(test_company['item']['id'], 'note', {'details': 'test'})
    activity_id = activity['id']
    assert activity['status'] == 'success'
    activity = crm.update_company_activity('note', activity_id, {'details': 'test2'})
    assert activity['status'] == 'success'
    activity = crm.destroy_company_activity('note', activity_id)
    assert activity['status'] == 'success'
    

def test_company_destroy():
    company = crm.destroy_company(test_company['item']['id'])
    assert company['status'] == 'success'


def test_list_companies_fields():
    fields = crm.list_companies_fields()
    assert fields['status'] == 'success'


def test_list_companies_categories():
    categories = crm.list_companies_categories()
    assert categories['status'] == 'success'
    

def test_projectblog_create():
    global test_projectblog
    projectblog = crm.create_projectblog({'title': 'A'})
    assert projectblog['status'] == 'success'
    test_projectblog = projectblog


def test_projectblog_create_categories():
    if CHANGE_CRM_STATE:
        category1 = crm.create_projectblog_category('C1')
        assert category1['status'] == 'success'


def test_projectblog_list_categories():
    categories = crm.list_projectblogs_categories()
    assert categories['status'] == 'success'


def test_show_projectblog():
    projectblog = crm.show_projectblog(test_projectblog['item']['id'])
    assert projectblog['status'] == 'success'


def test_update_projectblog():
    projectblog = crm.update_projectblog(test_projectblog['item']['id'], {'title': 'D'})
    assert projectblog['status'] == 'success'


def test_list_projectblogs():
    projectblogs = crm.list_projectblogs()
    assert projectblogs['status'] == 'success'


def test_projectblog_activity():
    activity = crm.create_projectblog_activity(test_projectblog['item']['id'], 'note', {'details': 'test'})
    activity_id = activity['id']
    assert activity['status'] == 'success'
    activity = crm.update_projectblog_activity('note', activity_id, {'details': 'test2'})
    assert activity['status'] == 'success'
    activity = crm.destroy_projectblog_activity('note', activity_id)
    assert activity['status'] == 'success'


def test_projectblog_destroy():
    projectblog = crm.destroy_projectblog(test_projectblog['item']['id'])
    assert projectblog['status'] == 'success'


def test_list_projectblogs_fields():
    fields = crm.list_projectblogs_fields()
    assert fields['status'] == 'success'


def test_list_projectblogs_categories():
    categories = crm.list_projectblogs_categories()
    assert categories['status'] == 'success'


def test_list_ownership():
    ownership = crm.list_ownership()
    assert ownership['status'] == 'success'


def test_report_nextaction():
    response = crm.show_report_nextactions(filter_=0)
    assert response['status'] == 'success'


def test_report_calendar():
    response = crm.show_report_calendar('2014-01-01', '2014-02-01')
    assert response['status'] == 'success'


def test_report_followup():
    response = crm.show_report_followups(responsible=0)
    assert response['status'] == 'success'
    
    
def test_report_opportunities():
    response = crm.show_report_opportunities(filter_=0)
    assert response['status'] == 'success'


def test_report_activities():
    response = crm.show_report_activities('2014-01-01', '2014-02-01', 'updated')
    assert response['status'] == 'success'


def test_report_timetracking():
    response = crm.show_report_timetracking('2014-01-01', '2014-02-01', 'updated')
    assert response['status'] == 'success'
