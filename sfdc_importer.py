
import datetime

from dateutil.parser import parse
from simple_salesforce import Salesforce

import settings


def _generate_sfdc_event(who_id, gb_metrics_event):
    """
    A utility function that, given an SFDC object_id and Guidebook metrics event dict,
    generates the data necessary to create a SFDC Activity Event
    """
    # a mapping of event name strings to their displayable counterparts
    event_name_to_readable_string = {
        "MobileApp-UserRegisteredScheduleSession": u"Added a Schedule Item in Guide: {}",
        "MobileApp-UserMadeToDoItem": u"Created a Todo List Item in Guide: {}",
        "MobileApp-UserTaggedOtherUser": u"Tagged Another User in Guide: {}",
        "MobileApp-UserCheckedIn": u"Checked-In in Guide: {}",
        "MobileApp-UserPostedPhoto": u"Posted a Photo in Guide: {}",
        "MobileApp-UserConnectionAccepted": u"Accepted a Connection Request in Guide: {}",
    }

    # exit if the current event is not supported
    if gb_metrics_event['event'] not in event_name_to_readable_string:
        return

    guide_name = gb_metrics_event['properties']['guide_name']
    event_name = event_name_to_readable_string[gb_metrics_event['event']].format(guide_name)

    event_data = {
        'Subject': event_name,
        'WhoId': who_id,
        'ActivityDateTime': datetime.datetime.strftime(parse(gb_metrics_event['properties']['time']), settings.SFDC_DATETIME_FORMAT),
        'DurationInMinutes': '1',
    }
    return event_data


def import_guidebook_metrics_into_sfdc(gb_metrics_event):
    """
    Given a Guidebook metrics event, attempt to attach it to a SFDC Contact or Lead object
    as an Activity Event.

    Finding the correct SFDC Object is done per the following:
        1) Attempt to find the earliest created Contact with the specified email
        2) If not found, Attempt to find the earliest created Lead with the specified email
        3) If both not found, create a Lead
    """

    salesforce = Salesforce(
        username=settings.SFDC_USERNAME,
        password=settings.SFDC_PASSWORD,
        security_token=settings.SFDC_SECURITY_TOKEN,
        sandbox=settings.USE_SFDC_SANDBOX,
        client_id='Guidebook Webhook API',
    )

    found_sfdc_object_id = None
    user_email = gb_metrics_event['properties']['email']

    # attempt to fetch a related SFDC Contact
    fetch_earliest_contact_with_email_query = "SELECT Id FROM Contact WHERE Email = '{}' ORDER BY Id ASC LIMIT 1".format(user_email)
    contact_results = salesforce.query(fetch_earliest_contact_with_email_query)
    if len(contact_results['records']) != 0:
        found_sfdc_object_id = contact_results['records'][0]['Id']

    # contact was not found - attempt to fetch a related SFDC Lead
    if found_sfdc_object_id is None:
        fetch_earliest_lead_with_email_query = "SELECT Id FROM Lead WHERE Email = '{}' ORDER BY Id ASC LIMIT 1".format(user_email)
        lead_results = salesforce.query(fetch_earliest_lead_with_email_query)
        if len(lead_results['records']) != 0:
            found_sfdc_object_id = lead_results['records'][0]['Id']

    # lead was not found - create a Lead
    if found_sfdc_object_id is None:
        guide_name = gb_metrics_event['properties']['guide_name']
        lead_first_name = '' if gb_metrics_event['properties']['first_name'] is None else gb_metrics_event['properties']['first_name']
        # A 'LastName' field is required to create a Lead in SFDC - it cannot be left as null or empty string
        lead_last_name = 'Unknown' if gb_metrics_event['properties']['last_name'] is None else gb_metrics_event['properties']['last_name']
        # A 'Company' field is required to create a Lead in SFDC - it cannot be left as null or empty string
        company_name = gb_metrics_event['properties']['company'] if gb_metrics_event['properties']['company'] is not None else guide_name
        company_position = '' if gb_metrics_event['properties']['position'] is None else gb_metrics_event['properties']['position']

        response = salesforce.Lead.create(
            {
                'FirstName': lead_first_name,
                'LastName': lead_last_name,
                'Company': company_name,
                'Email': user_email,
                'Title': company_position,
                'LeadSource': guide_name,
            }
        )
        found_sfdc_object_id = response['id']

    event_params = _generate_sfdc_event(found_sfdc_object_id, gb_metrics_event)
    if event_params is None:
        return

    salesforce.Event.create(event_params)
