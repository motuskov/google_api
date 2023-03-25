import os.path
from xml.etree import ElementTree
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

def get_exchange_rate(url, currency_name):
    '''Retrieves and returns the exchange rate of specified currency against the ruble.
    '''
    # Retrieving the XML document
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    response = session.get(url)
    if response.status_code != 200:
        return
    # Parsing the XML content
    root = ElementTree.fromstring(response.content)
    # Looking for the exchange rate of specified currency
    for currency in root.findall('.//Valute'):
        if currency.find('CharCode').text == currency_name:
            exchnge_rate_str = currency.find('Value').text.replace(',', '.')
            return float(exchnge_rate_str)

def get_google_credentials(token_file_name, scopes):
    '''Gets Google credentials from file with name "token_file_name" for Google services
    encountered in "scopes". Refreshes token file if it is needed.

    Args:
        token_file_name (str): Token file name with credentials
        scopes (list): List of Google services
    Returns:
        google.oauth2.credentials.Credentials object or None if the token file doesn't present or
        it does not contain valid data
    '''
    # Trying to get credentials from the token file
    if os.path.exists(token_file_name):
        creds = Credentials.from_authorized_user_file(token_file_name, scopes)

    # Checking credentials, trying to update if posible
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_file_name, 'w') as token:
                token.write(creds.to_json())
        else:
            return

    return creds

def get_google_document_modified_time(credentials, file_id):
    '''Retrieves last modified time of the file with ID "file_id" via Google Drive API.

    Args:
        credentials: google.oauth2.credentials.Credentials 
        file_id (str): Google file ID
    Returns:
        Last modified time of the file as a string
    '''
    # Getting the Google Drive API service
    service = build('drive', 'v3', credentials=credentials)

    # Retrieving the file modified time
    file = service.files().get(fileId=file_id, fields='modifiedTime').execute()

    return file['modifiedTime']

def read_google_spreadsheet_data(
        credentials,
        spreadsheet_id,
        sheet_name,
        first_data_row,
        process_row_count=500):
    '''Reads specified range from Google Sheets document.

    Args:
        credentials: google.oauth2.credentials.Credentials
        spreadsheet_id (str): Google spreadsheet ID
        sheet_name (str): Name of the sheet
        first_data_row (int): Number of row from which the data starts
        process_row_count (int): Number of rows to read in a time
    Returns:
        Dictionary with keys formed from the first column of the data and with values formed
        from the other columns as tuple
    '''
    # Getting the Google Sheets API service
    service = build('sheets', 'v4', credentials=credentials)

    # Calling the Google Sheets API
    sheet = service.spreadsheets()

    # Getting data from the sheet
    data = {}
    errors = []
    next_row = first_data_row
    while True:

        # Getting data
        data_range_name = f'{sheet_name}!A{next_row}:D{next_row + process_row_count}'
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=data_range_name).execute()
        rows = result.get('values', [])

        # Exiting loop if no more data
        if not rows:
            break

        # Processing every row of the data
        for row in rows:
            try:

                # Getting ID
                id = int(row[0])

                # Checking repeatability
                if id in data:
                    errors.append({
                        'description': (f'The record with ID {id} occurs more than once in '
                                        f'the document'),
                        'details': ''
                    })

                # Adding data to the dictionary
                data[id] = (
                    int(row[1]),
                    float(row[2]),
                    datetime.strptime(row[3], '%d.%m.%Y').date()
                )
                
            except ValueError as error:
                errors.append({
                    'description': (f'An error occurred during processing the record with '
                                    f'ID "{row[0]}"'),
                    'details': error
                })
                continue

        # Going to the next portion of data
        next_row += process_row_count

    return data, errors
