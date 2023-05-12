from bs4 import BeautifulSoup
from django.core.files.uploadedfile import SimpleUploadedFile

from convert.Spiders import Scrapers
from django.test import TestCase
from decimal import Decimal

from unittest.mock import patch

from convert.models import Provider, Currency, CurrencyRate


class TestScrapers(TestCase):
    def setUp(self):
        self.provider_tucambista = Provider.objects.create(name='Tucambista',
                                                           website='http://www.tucambista.com',
                                                           last_update='2022-01-01 12:00:00',
                                                           logo=SimpleUploadedFile("logo.jpg",
                                                                                   b"file_content",
                                                                                   content_type="image/jpeg"),
                                                           transaction_time=3,
                                                           is_neutral=False)
        self.currency_usd = Currency.objects.create(name='US Dollar', code='USD')
        self.currency_pen = Currency.objects.create(name='Peruvian Sol', code='PEN')

    @patch.object(Scrapers, 'get_soup_selenium')
    def test_scrape_tucambista(self, mock_get_soup_selenium):
        # Set up mock data
        mock_soup = '''
            <html>
                <body>
                    <div class="flex flex-row items-center"><span>3.25</span></div>
                    <div class="flex flex-row items-center"><span>3.3769</span></div>
                </body>
            </html>
        '''
        mock_get_soup_selenium.return_value = BeautifulSoup(mock_soup, 'html.parser')

        # Run scraper method
        scrapers = Scrapers()
        scrapers.scrape_tucambista()
        print(CurrencyRate.objects.all)



        self.assertTrue(CurrencyRate.objects.filter(provider=self.provider_tucambista,
                                                    currency_from=self.currency_usd,
                                                    currency_to=self.currency_pen,
                                                    exchange_rate='3.25').exists())
        self.assertTrue(CurrencyRate.objects.filter(provider=self.provider_tucambista,
                                                    currency_from=self.currency_pen,
                                                    currency_to=self.currency_usd,
                                                    exchange_rate=str(round(1 / Decimal('3.3769'), 4))).exists())

    @patch('requests.get')
    def test_get_soup(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.content = b'<html><head></head><body></body></html>'

        soup = Scrapers.get_soup(self.provider_tucambista)

        mock_get.assert_called_once_with(self.provider_tucambista.website)
        self.assertIsNotNone(soup)

    def test_save_to_db(self):
        exchange_rate = Decimal('3.7525')
        Scrapers.save_to_db(self.provider_tucambista, self.currency_usd, self.currency_pen, exchange_rate)
        rate = CurrencyRate.objects.get(provider=self.provider_tucambista, currency_from=self.currency_usd,
                                        currency_to=self.currency_pen, exchange_rate=exchange_rate)
        self.assertEqual(rate.provider, self.provider_tucambista)
        self.assertEqual(rate.currency_from, self.currency_usd)
        self.assertEqual(rate.currency_to, self.currency_pen)
        self.assertEqual(rate.exchange_rate, exchange_rate)
