# About

This code provides an example of how to export Guidebook metrics data into Salesforce.

It takes metrics data from the [Guidebook Webhooks API](https://developer.guidebook.com/#webhooks) and imports it into Salesforce via the [Salesforce SOAP API](https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/sforce_api_quickstart_intro.htm).


# Sample Usage

Before testing out the code.  Please `pip install -r requirements.txt` to get the package dependencies.  We highly recommend you do this in an [virtualenv](https://virtualenv.pypa.io/en/stable/).

Update `settings.py` with your Salesforce login information. Then the following command will perform the import with the demo data in `sample_event.json`.

`python execute_integration.py`

# Customizing this Integration

This code is provided to Guidebook clients to customize for their own integrations.  Clients are welcome to take this integration code as a starting point and adapt it to their own needs.