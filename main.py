import requests

from ogn.client import AprsClient
from ogn.parser import parse, ParseError

# Buddy list
buddy_list = ['N9094D', '1106416']
buddy_list_ids = []

# Download 
download_url    = 'https://ddb.glidernet.org/download/'
downloaded_file = 'ogn-ddb.txt'

if False:
  print('Beginning file download with requests')

  r = requests.get(download_url)
  with open(downloaded_file, 'wb') as f:
    f.write(r.content)

  print('Done.')

import csv

with open(downloaded_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',', quotechar='\'')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
          print(f'Column names are {", ".join(row)}')
        else:
          if row[3] in buddy_list:
            print(row)
            for prefix in ['ICA', 'FLR']:
              buddy_list_ids.append(prefix + row[1]) 

        line_count += 1
    print(f'Processed {line_count} lines.')

# {
#   'raw_message': "FLRDD8223>APRS,qAS,EHHV1:/183842h5212.14N/00508.51E'089/062/A=000646 !W04! id06DD8223 -157fpm +0.0rot 4.5dB 0e -0.1kHz gps3x2", 
#    'reference_timestamp': datetime.datetime(2020, 7, 24, 18, 38, 49, 395137), 
#    'aprs_type': 'position', 
#    'name': 'FLRDD8223',
#    'dstcall': 'APRS', 
#    'relay': None, 
#    'receiver_name': 'EHHV1', 
#    'timestamp': datetime.datetime(2020, 7, 24, 18, 38, 42), 
#    'latitude': 52.202333333333335, 
#    'symboltable': '/', 
#    'longitude': 5.1419, 
#    'symbolcode': "'", 
#    'track': 89, 
#    'ground_speed': 114.81316149470803, 
#    'altitude': 196.9008, 
#    'comment': 'id06DD8223 -157fpm +0.0rot 4.5dB 0e -0.1kHz gps3x2', 
#    'address_type': 2, 
#    'aircraft_type': 1, 
#    'stealth': False, 
#    'address': 'DD8223', 
#    'climb_rate': -0.79756, 
#    'turn_rate': 0.0, 
#    'flightlevel': None, 
#    'signal_quality': 4.5, 
#    'error_count': 0, 
#    'frequency_offset': -0.1, 
#    'gps_quality': {'horizontal': 3, 'vertical': 2}, 
#    'software_version': None, 
#    'hardware_version': None, 
#    'real_address': None, 
#    'signal_power': None, 
#    'proximity': None, 
#    'beacon_type': 'aprs_aircraft'
# }


def process_beacon(raw_message):
    try:
        beacon = parse(raw_message)

        if 'altitude' in beacon:
          print(beacon['name'], ': ', beacon['timestamp'], ' ', beacon['altitude'])
          print('            ', beacon['ground_speed'])
    except ParseError as e:
        print('Error')
        print('Error, {}'.format(e.message))

aprs_filter = 'e/EHHV1'

if len(buddy_list_ids) > 0:
  aprs_filter = 'b/' + '/'.join(buddy_list_ids)

client = AprsClient(aprs_user='N0CALL', aprs_filter=aprs_filter)
client.connect()

try:
    client.run(callback=process_beacon, autoreconnect=True)
except KeyboardInterrupt:
    print('\nStop ogn gateway')
    client.disconnect()

    