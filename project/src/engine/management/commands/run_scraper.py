from django.core.management.base import BaseCommand
import sys
sys.path.append('/Users/eoghanleddy/Development/scraping-intro')
import src.engine.scrapers as scrapers

class Command(BaseCommand):
    help = 'python project/manage.py run_scraper Walmart TacoBell --zipstart 02138 --zipend 33477'

    def add_arguments(self, parser):
        parser.add_argument('merchant', nargs='+', type=str)
        parser.add_argument(
            '--zipstart',
            nargs='?',
            action='store',
            dest='zipstart',
            help='Start of subset of zipcodes to run scraper(s) on.',
        )
        parser.add_argument(
            '--zipend',
            nargs='?',
            action='store',
            dest='zipend',
            help='End of subset of zipcodes to run scraper(s) on.',
        )
        parser.add_argument(
            '--only-unscraped-zips',
            nargs='?',
            const=True,
            dest='only_unscraped_zips',
            help='Only scrapes for zipcodes not yet in db for this merchant.',
        )

    def handle(self, *args, **options):
        for merchant in options['merchant']:
            ScraperClass = getattr(scrapers, f'{merchant}Scraper')
            if ScraperClass:
                ScraperClass(
                    zipstart=options['zipstart'],
                    zipend=options['zipend'],
                    only_unscraped_zips=options['only_unscraped_zips']
                ).process()
            else:
                print(f'Could not find scraper for: {merchant}')
