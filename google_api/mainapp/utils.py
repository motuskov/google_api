from xml.etree import ElementTree
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests

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
