from mock import patch
from pathlib import Path
from sure import expect

from django.test import TestCase, override_settings
from src.engine.services.scrapers.base import BaseStoreLocationScraper
from src.engine.models import StoreLocation


class NoProxyScraper(BaseStoreLocationScraper):
    headers = {'some': 'headers'}

    def get_urls(self):
        return ["http://no-proxy.com"]


class ProxyScraper(BaseStoreLocationScraper):
    headers = {'some': 'headers'}
    use_proxy = True

    def get_urls(self):
        return ["http://with-proxy.com"]

class ProxyScraperTests(TestCase):

    @patch('src.engine.services.scrapers.base.requests')
    def test_no_proxy(self, requests):
        NoProxyScraper().process()
        requests.get.assert_called_once_with(
            "http://no-proxy.com", headers={'some': 'headers'})

    @override_settings(CRAWLERA_API_KEY='CRAWLERA_API_KEY')
    @patch('src.engine.services.scrapers.base.requests')
    def test_with_proxy(self, requests):
        ProxyScraper().process()
        requests.get.assert_called_once_with(
            'http://with-proxy.com',
            headers={'some': 'headers'},
            proxies={
                'https': 'https://CRAWLERA_API_KEY:@proxy.crawlera.com:8010/',
                'http': 'http://CRAWLERA_API_KEY:@proxy.crawlera.com:8010/'},
            verify=Path.cwd().joinpath('crawlera-ca.crt'))