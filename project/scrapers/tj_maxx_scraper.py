import re

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from .base import BaseStoreLocationWebdriverScraper
from src.engine.models import StoreLocation, Merchant


class TJMaxxScraper(BaseStoreLocationWebdriverScraper):
    base_url = "https://m.tjmaxx.tjx.com/m/stores/storeLocator.jsp#"
    merchant_name = 'T.J. Maxx'
    geolocator = Nominatim(user_agent='finhance-api')                           # This is a simple python library to help us get accurate lat/long for stores based on their address
    use_proxy = True

    def process(self):
        try:
            self.persist_stores()
            print('Complete')
        except Exception as e:
            import pdb; pdb.set_trace()
            print(e)
        self.driver.close()

    def persist_stores(self):
        merchant_name = self.merchant_name or self.__class__.__name__.split('Scraper')[
            0]
        merchant, created = Merchant.objects.get_or_create(name=merchant_name)

        for zipcode in self.zipcodes[::10]:
            self.driver.get(self.base_url)                                      # Tells Selenium to load up our base_url found above 
            self.get_stores_by_zipcode(zipcode)
            try:
                self.driver.find_element_by_css_selector('div.alert')
                continue
            except NoSuchElementException:
                self.scrape_store_results(merchant)

    def get_stores_by_zipcode(self, zipcode):
        try:
            self.driver.find_element_by_css_selector('svg.close').click()
        except NoSuchElementException:
            print('No modal present')

        input = self.driver.find_element_by_css_selector(                       # This is the first element we find - the input where we will have Selenium input the zip codes for us
            'input#store-locator-search')
        button = self.driver.find_element_by_css_selector(
            'input#store-locator-search-submit-locate')                         # The second element is the submit button - we will have Selenium emulate a user pressing this button
        input.send_keys(zipcode)
        button.click()

    def scrape_store_results(self, merchant):
        WebDriverWait(self.driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ul#store-list'))  # We tell Selenium to wait until the results <ul> is present so we don't get a NoSuchElementException
        )
        stores = self.driver.find_elements_by_css_selector(
            'li.store-list-item')                                               # We then grab all of the <li> elements in that <ul> tag with the appropriate class as these elements have the information we need

        for store in stores:
            self.persist_store_location(store, merchant)

    def persist_store_location(self, store, merchant):
        store_num = store.find_element_by_css_selector(                         # In this method we just get children elements' attributes to fill in the data we need (e.g Store number, location, etc)
            'a').get_attribute('href').split('/')[-3]
        full_address = store.find_element_by_css_selector(
            'div.adr').get_attribute('innerText').strip()
        locality, address = full_address.split('\n')
        cleaned_address = re.sub("[\(\[].*?[\)\]]", "", address)
        city, state_zip = cleaned_address.split(', ')
        state, zip = state_zip.split(' ')

        try:
            coordinates = (self.geolocator.geocode(f'{locality}, {cleaned_address}') or
                           self.geolocator.geocode(address))
            lat = coordinates.latitude
            lng = coordinates.longitude
        except (GeocoderTimedOut, AttributeError) as e:
            coordinates = self.get_coordinates(zip)
            lat = coordinates['lat']
            lng = coordinates['lng']

        print(
            f'Scraping information for store number: {store_num} in {city}, {state}')

        StoreLocation.objects.update_or_create(
            merchant=merchant,
            store_id=store_num,
            defaults={
                'city': city,
                'state': state,
                'zip': zip,
                'lat': lat,
                'lng': lng
            }
        )