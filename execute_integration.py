import json

import sfdc_importer

if __name__ == "__main__":
    """
    Reads the demo data from 'sample_event.json' and imports it into SFDC
    """
    f = open('sample_event.json')
    gb_metrics_event = json.loads(f.read())
    f.close()

    print 'Importing Metrics Data into SFDC'

    sfdc_importer.import_guidebook_metrics_into_sfdc(gb_metrics_event)
