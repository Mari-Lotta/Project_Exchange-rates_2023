from django.test import TestCase
from django.urls import reverse

from decimal import Decimal
from datetime import datetime

from convert.models import Provider, Currency, CurrencyRate


class CurrencyRateListViewTest(TestCase):
    def setUp(self):
        # Create currencies
        self.usd = Currency.objects.create(name="US Dollar", code="USD")
        self.eur = Currency.objects.create(name="Euro", code="EUR")
        self.pen = Currency.objects.create(name="Peruvian Sol", code="PEN")

        # Create providers
        self.provider1 = Provider.objects.create(name="Provider 1",
                                                 is_neutral=False,
                                                 last_update='2022-01-01 12:00:00',
                                                 transaction_time=3)
        self.provider2 = Provider.objects.create(name="Provider 2",
                                                 is_neutral=False,
                                                 last_update='2022-01-01 12:00:00',
                                                 transaction_time=3, )
        self.provider3 = Provider.objects.create(name="Provider 3",
                                                 is_neutral=True,
                                                 last_update='2022-01-01 12:00:00',
                                                 transaction_time=3, )

        # Create currency rates
        self.rate1 = CurrencyRate.objects.create(
            provider=self.provider1,
            currency_from=self.usd,
            currency_to=self.pen,
            exchange_rate=Decimal('3.5'),
            date_time=datetime(2022, 5, 3, 10, 0, 0)
        )
        self.rate2 = CurrencyRate.objects.create(
            provider=self.provider1,
            currency_from=self.usd,
            currency_to=self.pen,
            exchange_rate=Decimal('3.6'),
            date_time=datetime(2023, 5, 4, 10, 0, 0)
        )
        self.rate3 = CurrencyRate.objects.create(
            provider=self.provider2,
            currency_from=self.usd,
            currency_to=self.pen,
            exchange_rate=Decimal('3.7'),
            date_time=datetime(2023, 5, 4, 10, 0, 0)
        )
        self.rate4 = CurrencyRate.objects.create(
            provider=self.provider2,
            currency_from=self.usd,
            currency_to=self.pen,
            exchange_rate=Decimal('3.8'),
            date_time=datetime(2023, 5, 5, 10, 0, 0)
        )
        self.rate5 = CurrencyRate.objects.create(
            provider=self.provider3,
            currency_from=self.usd,
            currency_to=self.pen,
            exchange_rate=Decimal('3.9'),
            date_time=datetime(2023, 5, 5, 10, 0, 0)
        )

    def test_view_url_exists_at_desired_location(self):
        url = '/convert/USD-PEN/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        url = reverse('convert:currency_rates', args=['USD', 'PEN'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        url = reverse('convert:currency_rates', args=['USD', 'PEN'])
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'convert/currency_rate_list.html')

    def test_view_displays_latest_rates(self):
        url = reverse('convert:currency_rates', args=['USD', 'PEN'])
        response = self.client.get(url)
        self.assertContains(response, 'Provider 1')
        self.assertContains(response, 'Provider 2')
        self.assertContains(response, 'Provider 3')
        self.assertContains(response, '3.8000')
        self.assertNotContains(response, '3.7000')
        self.assertNotContains(response, '3.5000')
