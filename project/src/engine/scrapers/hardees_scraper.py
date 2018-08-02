import json
from bs4 import BeautifulSoup
from .base import BaseStoreLocationScraper
from src.engine.models import StoreLocation


class HardeesScraper(BaseStoreLocationScraper):
    base_url = "https://maps.ckr.com/stores/search?brand=hardees&q={zip}&brand_id=1"
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    }

    def get_url(self, zipcode):
        return self.base_url.format(zip=str(zipcode))

    def get_stores(self, res):
        soup = BeautifulSoup(res.content, 'html.parser')

        # the list is embedded in the JS script as a string
        scripts = soup.find_all("script")
        locs_string = str(scripts[7].string)

        # need to remove these parts of the string in order to parse JSON
        locs_string = locs_string.split('\n  var storeJson = ')
        locs_string = locs_string[1].split(';\n  var country =')

        locs_list = json.loads(locs_string[0])

        return locs_list

    def persist_store_location(self, store, merchant):

        return StoreLocation.objects.update_or_create(
            merchant=merchant,
            store_id=store['sidebar']['id'],
            defaults={
                'city': store['sidebar']['city'].title(),
                'state': store['sidebar']['state'].upper(),
                'zip': store['sidebar']['postal_code'],
                'lat': store['lat'],
                'lng': store['lng']
            }
        )