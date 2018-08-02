import requests

from .base import BaseStoreLocationScraper
from src.engine.models import StoreLocation, Merchant


class AdvanceAutoPartsScraper(BaseStoreLocationScraper):
    merchant_name = 'Advance Auto Parts'
    base_url = "https://stores.advanceautoparts.com/search-api"

    querystring = {"q": ""}

    headers = {
        'accept': "application/json, text/javascript, */*; q=0.01",
        'x-devtools-emulate-network-conditions-client-id': "B386A44F1104BF0A9AC3D6389A8EE21A",
        'x-requested-with': "XMLHttpRequest",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
        'referer': "https://stores.advanceautoparts.com/?q=11104",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "en-US,en;q=0.9",
        'cookie': "_ga=GA1.2.1826141226.1531164294; _gid=GA1.2.837383353.1531164294; QuantumMetricUserID=a111242e453dc10c7b4b875bf254a5b6; QuantumMetricSessionID=39be3c0c9ec013568fab501af0f0c59a; utag_main=v_id:01648080fb3a002b6d2789c9856803078002407000fb8$_sn:1$_ss:0$_st:1531166268664$ses_id:1531164293950%3Bexp-session$_pn:3%3Bexp-session$dc_visit:1$dc_event:3%3Bexp-session$dc_region:us-east-1%3Bexp-session; _ga=GA1.2.1826141226.1531164294; _gid=GA1.2.837383353.1531164294; QuantumMetricUserID=a111242e453dc10c7b4b875bf254a5b6; QuantumMetricSessionID=39be3c0c9ec013568fab501af0f0c59a; utag_main=v_id:01648080fb3a002b6d2789c9856803078002407000fb8$_sn:1$_ss:0$_st:1531166268664$ses_id:1531164293950%3Bexp-session$_pn:3%3Bexp-session$dc_visit:1$dc_event:3%3Bexp-session$dc_region:us-east-1%3Bexp-session",
        'cache-control': "no-cache",
        'postman-token': "77551287-175f-b598-d118-61606caf0563"
    }

    def process(self):
        merchant_name = self.merchant_name or self.__class__.__name__.split(
            'Scraper'
        )[0]
        merchant, created = Merchant.objects.get_or_create(name=merchant_name)
        for zipcode in self.zipcodes[::5]:
            self.querystring["q"] = zipcode
            res = requests.get(                 # A screencast on how to easily get all of this information using Postman is available in the Videos section of the README
                self.base_url, headers=self.headers, params=self.querystring
            )
            self.get_stores(res, merchant)

    def get_stores(self, res, merchant):
        for store in res.json()['locations']:
            self.persist_store_location(store['loc'], merchant)

    def persist_store_location(self, store, merchant):
        city = store['city']
        state = store['state']
        store_num = store['corporateCode']

        print(f'Scraping store #{store_num} from {city}, {state}')

        StoreLocation.objects.update_or_create(
            merchant=merchant,
            store_id=store_num,
            normalized_store_id=store_num,
            defaults={
                'city': city,
                'state': state,
                'zip': store['postalCode'],
                'lat': store['latitude'],
                'lng': store['longitude']
            }
        )