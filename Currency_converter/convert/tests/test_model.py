from django.test import TestCase
from convert.models import Provider, Currency, CurrencyRate
from django.core.files.uploadedfile import SimpleUploadedFile


class ProviderModelTestCase(TestCase):

    def setUp(self):
        self.provider = Provider.objects.create(
            name='Test Provider',
            website='http://www.example.com',
            last_update='2022-01-01 12:00:00',
            logo=SimpleUploadedFile("logo.jpg", b"file_content", content_type="image/jpeg"),
            transaction_time=3,
            is_neutral=True
        )

    def test_string_representation(self):
        self.assertEqual(str(self.provider), 'Test Provider')

    def test_logo_upload(self):
        self.assertIsNotNone(self.provider.logo)

    def test_transaction_time_type(self):
        self.assertIsInstance(self.provider.transaction_time, int)

    def test_is_neutral_type(self):
        self.assertIsInstance(self.provider.is_neutral, bool)

    def test_website_max_length(self):
        max_length = self.provider._meta.get_field('website').max_length
        self.assertEquals(max_length, 500)


class CurrencyModelTestCase(TestCase):

    def setUp(self):
        self.currency = Currency.objects.create(
            name='Test Currency',
            code='TST'
        )

    def test_string_representation(self):
        self.assertEqual(str(self.currency), 'Test Currency')

    def test_name_max_length(self):
        max_length = self.currency._meta.get_field('name').max_length
        self.assertEquals(max_length, 200)

    def test_code_max_length(self):
        max_length = self.currency._meta.get_field('code').max_length
        self.assertEquals(max_length, 20)

    def test_name_not_null(self):
        self.assertIsNotNone(self.currency.name)

    def test_code_not_null(self):
        self.assertIsNotNone(self.currency.code)


class CurrencyRateModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.provider = Provider.objects.create(name="Test Provider", website="https://example.com",
                                               last_update="2023-01-01 00:00:00", transaction_time=5,
                                               is_neutral=True)
        cls.currency_from = Currency.objects.create(name="Test Currency 1", code="TC1")
        cls.currency_to = Currency.objects.create(name="Test Currency 2", code="TC2")
        cls.currency_rate = CurrencyRate.objects.create(provider=cls.provider, currency_from=cls.currency_from,
                                                        currency_to=cls.currency_to, exchange_rate=1.2345)

    def test_string_representation(self):
        currency_rate = CurrencyRate.objects.get(id=self.currency_rate.id)
        expected_string = "{}: {} to {}  - {} at {}".format(
            self.provider.name,
            self.currency_from.code,
            self.currency_to.code,
            self.currency_rate.exchange_rate,
            self.currency_rate.date_time
        )
        self.assertEqual(str(currency_rate), expected_string)

    def test_provider_foreign_key(self):
        currency_rate = CurrencyRate.objects.get(id=self.currency_rate.id)
        self.assertEqual(currency_rate.provider, self.provider)

    def test_currency_from_foreign_key(self):
        currency_rate = CurrencyRate.objects.get(id=self.currency_rate.id)
        self.assertEqual(currency_rate.currency_from, self.currency_from)

    def test_currency_to_foreign_key(self):
        currency_rate = CurrencyRate.objects.get(id=self.currency_rate.id)
        self.assertEqual(currency_rate.currency_to, self.currency_to)

    def test_exchange_rate_decimal_places(self):
        currency_rate = CurrencyRate.objects.get(id=self.currency_rate.id)
        self.assertEqual(currency_rate.exchange_rate.as_tuple().exponent, -4)

    def test_exchange_rate_max_digits(self):
        currency_rate = CurrencyRate.objects.get(id=self.currency_rate.id)
        self.assertEqual(currency_rate.exchange_rate.as_tuple().digits, (1, 2, 3, 4, 5))
