from xml.etree import ElementTree
import requests

def get_exchange_rate(url, currency_name):
    '''Retrieves and returns the exchange rate of specified currency against the ruble.
    '''
    # Retrieving the XML document
    response = requests.get(url)
    if response.status_code != 200:
        return
    # Parsing the XML content
    root = ElementTree.fromstring(response.content)
    # Looking for the exchange rate of specified currency
    for currency in root.findall('.//Valute'):
        if currency.find('CharCode').text == currency_name:
            exchnge_rate_str = currency.find('Value').text.replace(',', '.')
            return float(exchnge_rate_str)
