from .base import BaseStoreLocationScraper
from src.engine.models import StoreLocation

# This scraper extends the BaseStoreLocationScraper class which can be found in the base.py file and is a great place to start reading through the code in this repo.
class REIScraper(BaseStoreLocationScraper):
    base_url = 'https://www.rei.com/rest/stores?retail=true&dist=7500&limit=1500&visible=true&lat=39.82832&long=-98.5795'
    # This URL has query params that allow us to get all of the store location for REI with one API call.
    # Lat and Long are for the geographic center of the US.

    def get_urls(self): # We override the base class implementation of this method because we can get all results with one request and therefore do not need to loop through all zip codes.
        return [self.base_url]

    def get_stores(self, res):
        return res.json()

    def persist_store_location(self, store, merchant):
        print(f'Creating location for store {store["storeDisplayName"]}')

        return StoreLocation.objects.update_or_create(
            merchant=merchant,
            store_id=store['storeNumber'],
            normalized_store_id=store['storeNumber'],
            defaults={
                'city': store['city'],
                'state': store['state'],
                'zip': store['zip'],
                'phone': store['phone'],
                'lat': store['latitude'],
                'lng': store['longitude'],
            }
        )