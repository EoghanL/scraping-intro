import requests
import urllib3

from pathlib import Path
from pyzipcode import ZipCodeDatabase
from selenium import webdriver

from django.conf import settings

from src.engine.models import Merchant, StoreLocation
from src.engine.constants import ALL_ZIPCODES as ZIPS
from src.area.models import Area

# Removes SubjectAltNameWarning on SSL proxy requests
urllib3.disable_warnings(urllib3.exceptions.SecurityWarning)


class BaseStoreLocationScraper(object):
    merchant_name = None
    base_url = None
    zipcode_db = ZipCodeDatabase()
    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        'accept': "application/json"
    }

    def __init__(self, zipstart=None, zipend=None, only_unscraped_zips=False):
        self.zipcodes = ZIPS

        if zipstart:
            self.zipcodes = [ code for code in self.zipcodes if code >= zipstart ]
        if zipend:
            self.zipcodes = [ code for code in self.zipcodes if code <= zipend ]

        if only_unscraped_zips:
            merchant_name = self.merchant_name or self.__class__.__name__.split('Scraper')[0]
            unique_zips = StoreLocation.objects.filter(merchant__name=merchant_name).values_list('zip', flat=True).distinct()

            five_digit_zips = [zipcode.split('-')[0] for zipcode in unique_zips if zipcode]

            self.zipcodes = sorted(list(set(self.zipcodes).difference(five_digit_zips)))

    def get_coordinates(self, zipcode):
        try:
            geo_data = self.zipcode_db[str(zipcode).split('-')[0]]
        except IndexError:
            try:
                geo_data = Area.objects.get(zip=str(zipcode).split('-')[0])
                return { 'lat': geo_data.lat, 'lng': geo_data.lng }
            except Area.DoesNotExist:
                return { 'lat': 0, 'lng': 0 }
        else:
            return { 'lat': geo_data.latitude, 'lng': geo_data.longitude }

    def get_urls(self):
        return [self.get_url(zipcode) for zipcode in self.zipcodes]

    def get_url(self, zipcode):
        raise NotImplementedError

    def get_stores(self, res):
        return res.json()

    def request_data(self, url):
        print("Requesting data from {}".format(url))
        kwargs = {'headers': self.headers}
        if self.use_proxy:
            kwargs['proxies'] = self.proxies
            kwargs['verify'] = Path.cwd().joinpath('crawlera-ca.crt').absolute()
        try:
            res = requests.get(url, **kwargs)
            self.handle_response(res)
        except Exception as e:
            print(e)

    def process(self):
        urls = self.get_urls()
        for url in urls:
            self.request_data(url)

    def handle_response(self, res):
        # this prints the HTTP code, i.e. '200' - so we can make sure the request is good
        print(res)
        stores = self.get_stores(res)
        if stores:
            self.persist_stores(stores)
            print("Complete.")
        else:
            print("No data")

    def persist_stores(self, stores):
        # for each url, a list of stores will be given
        merchant_name = self.merchant_name or self.__class__.__name__.split('Scraper')[0]
        merchant, created = Merchant.objects.get_or_create(name=merchant_name)

        for store in stores:
            self.persist_store_location(store, merchant)

    def parse_store(self, store):
        return NotImplementedError


    def persist_store_location(self, store, merchant):
        store_data = self.parse_store(store)
        store_id = store_data.pop('id')
        return StoreLocation.objects.update_or_create(
            store_id=store_id,
            merchant=merchant,
            defaults=store_data
        )


class BaseStoreLocationWebdriverScraper(BaseStoreLocationScraper):  # This class is for Selenium based scrapers
    def __init__(self, *args, **kwargs):
        super(
            BaseStoreLocationWebdriverScraper, self
        ).__init__(*args, **kwargs)
        self.driver = self.get_webdriver()

    def get_webdriver(self):
        if settings.GOOGLE_CHROME_BIN and settings.CHROMEDRIVER_PATH:
            options = webdriver.ChromeOptions()
            options.binary_location = settings.GOOGLE_CHROME_BIN
            options.add_argument('--no-sandbox')
            options.add_argument('--headless')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(
                executable_path=settings.CHROMEDRIVER_PATH, chrome_options=options
            )
        else:
            driver = webdriver.Firefox()
        return driver


class MapQuestBaseScraper(BaseStoreLocationScraper):
    base_url = None

    def get_urls(self):
        return [self.base_url]

    def get_stores(self, res):
        return res.json()['searchResults']

    def persist_store_location(self, store, merchant):
        print(f'Creating location for store {store["name"]}')
        return StoreLocation.objects.update_or_create(
            merchant=merchant,
            store_id=store['name'],
            defaults={
                'city': store['fields']['city'],
                'state': store['fields']['state'],
                'zip': store['fields']['postal'],
                'phone': store['fields']['phone'],
                'lat': store['fields']['Lat'],
                'lng': store['fields']['Lng'],
            }
        )