import ast
import requests

from bs4 import BeautifulSoup

from .base import BaseStoreLocationScraper
from src.engine.models import StoreLocation

ATTENDED_STATES = [
    'Michigan', 'Illinois', 'Indiana', 'Kentucky', 'Ohio', 'Wisconsin'
]


class MeijerScraper(BaseStoreLocationScraper):
    merchant_name = 'Meijer'
    base_url = 'https://www.meijer.com/custserv/locate_store_by_state.cmd?form_state=locateStoreByStateForm&state={}'

    def process(self):
        for state in ATTENDED_STATES:
            res = requests.get(self.base_url.format(state))
            soup = BeautifulSoup(res.content, 'html.parser')
            self.parse_store_info_from_script(soup)

    def parse_store_info_from_script(self, soup):
        script_content = soup.find(class_='records_inner').find('script').text
        store_list = script_content.split('stores = ')[-1].split(';')[0]
        #import ipdb; ipdb.set_trace()
        stores = ast.literal_eval(store_list)

        self.persist_stores(stores)

    def persist_store_location(self, store, merchant):
        store_id = store[0]
        address = store[6]
        city, state_zip = address.split(', ')
        state, zip = state_zip.split(' ')
        geo = self.get_coordinates(zip)

        print(f'Getting store information for {city}, {state}')

        return StoreLocation.objects.update_or_create(
            merchant=merchant,
            store_id=store_id,
            normalized_store_id=store_id,
            defaults={
                'city': city,
                'state': state,
                'zip': zip,
                'lat': geo['lat'],
                'lng': geo['lng'],
            }
        )
