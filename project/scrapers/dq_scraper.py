import re
import requests
from bs4 import BeautifulSoup

from .base import BaseStoreLocationScraper
from src.engine.models import StoreLocation, Merchant


class DairyQueenScraper(BaseStoreLocationScraper):
    merchant_name = 'Dairy Queen'
    base_url = 'https://www.dairyqueen.com/us-en/locator/Detail/{}'

    def process(self):
        print('Requesting sitemap data')
        merchant, created = Merchant.objects.get_or_create(name=self.merchant_name)

        try:
            res = requests.get('https://www.dairyqueen.com/us-en/Sitemap/')
            store_numbers = self.get_store_numbers(res)
            counter = 0

            for store_num in store_numbers:
                counter += 1
                print(f'On Store Num: {store_num} Progress: {counter}/{len(store_numbers)}')
                details = self.get_store_details(store_num)
                print(details)
                if details:
                    self.persist_store_location(details, merchant, store_num)
        except Exception as e:
            print(e)

    def get_store_numbers(self, res):
        soup = BeautifulSoup(res.content, 'html5lib')
        stores = soup.find('section', class_='paragraph-modules').find_all('a')
        return [store['href'].split('/')[-1] for store in stores]

    def get_store_details(self, num):
        res = requests.get(self.base_url.format(num))
        soup = BeautifulSoup(res.content, 'html5lib')
        try:
            store_details = soup.find('hgroup', class_='store-address').find_all('span')
            store_address_has_extra_detail = len(store_details) > 3
        except:
            return
        if store_address_has_extra_detail:
            return [detail.text for detail in store_details][1:]
        else:
            return [detail.text for detail in store_details]

    def persist_store_location(self, store, merchant, store_num):
        coordinates = self.get_coordinates(store[2])

        return StoreLocation.objects.update_or_create(
            merchant=merchant,
            store_id=store_num,
            defaults={
                'city': store[0],
                'state': store[1],
                'zip': store[2],
                'lat': coordinates['lat'],
                'lng': coordinates['lng']
            }
        )