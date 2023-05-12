from _pydecimal import Decimal
import datetime

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from convert.models import Provider, Currency, CurrencyRate


class Scrapers:
    def __init__(self):
        self.provider_list = Provider.objects.all()
        self.currency_list = Currency.objects.all()

    def scrape_tucambista(self):
        provider = next((p for p in self.provider_list if p.name == "Tucambista"), None)
        currency_usd = next((c for c in self.currency_list if c.code == 'USD'), None)
        currency_pen = next((c for c in self.currency_list if c.code == 'PEN'), None)

        # xpath variable that identifies needed HTML element that is rendered by JavaScript
        xpath = "//div[@class=' flex flex-row items-center']"

        soup = self.get_soup_selenium(provider, xpath)

        # locate the specific HTML elements that contain the price values
        data = soup.find_all('div', class_='flex flex-row items-center')

        buy_price = str(round(Decimal(data[0].find('span').text), 4))
        sell_price = str(round(1 / Decimal(data[1].find('span').text), 4))

        self.save_to_db(provider, currency_usd, currency_pen, buy_price)
        self.save_to_db(provider, currency_pen, currency_usd, sell_price)

    def scrape_dollarhouse(self):
        provider = next(
            (p for p in self.provider_list if p.name == "DollarHouse")
            , None)
        currency_usd = next((c for c in self.currency_list if c.code == 'USD'), None)
        currency_pen = next((c for c in self.currency_list if c.code == 'PEN'), None)

        soup = self.get_soup(provider)

        #  find the specific HTML element
        exchange_rate_container = soup.body.main.find('div', class_="exchange-rate-container")

        #  extracts the buy and sell prices from the HTML element
        buy_price = exchange_rate_container.find(id="buy-exchange-rate").text.replace(',', '.')
        sell_price = str(
            round(1 / Decimal(exchange_rate_container.find(id="sell-exchange-rate").text.replace(',', '.')), 4))

        self.save_to_db(provider, currency_usd, currency_pen, buy_price)
        self.save_to_db(provider, currency_pen, currency_usd, sell_price)

    def scrape_kambista(self):
        provider = next((p for p in self.provider_list if p.name == "Kambista"), None)
        currency_usd = next((c for c in self.currency_list if c.code == 'USD'), None)
        currency_pen = next((c for c in self.currency_list if c.code == 'PEN'), None)

        soup = self.get_soup(provider)

        buy_price = str(round(Decimal(soup.body.find(id="valcompra").text.strip()), 4))
        sell_price = str(round(1 / Decimal(soup.body.find(id="valventa").text.strip().replace(',', '.')), 4))

        self.save_to_db(provider, currency_usd, currency_pen, buy_price)
        self.save_to_db(provider, currency_pen, currency_usd, sell_price)

        pass

    def scrape_inkamoney(self):
        provider = next((p for p in self.provider_list if p.name == "InkaMoney"), None)
        currency_usd = next((c for c in self.currency_list if c.code == 'USD'), None)
        currency_pen = next((c for c in self.currency_list if c.code == 'PEN'), None)

        soup = self.get_soup(provider)

        buy_price = str(round(Decimal(soup.header.find("inka-conversor-home")[':buy-price']), 4))
        sell_price = str(round(1 / Decimal(soup.header.find("inka-conversor-home")[':sale-price']), 4))

        self.save_to_db(provider, currency_usd, currency_pen, buy_price)
        self.save_to_db(provider, currency_pen, currency_usd, sell_price)

        pass

    def scrape_tkambio(self):
        provider = next((p for p in self.provider_list if p.name == "TKambio"), None)
        currency_usd = next((c for c in self.currency_list if c.code == 'USD'), None)
        currency_pen = next((c for c in self.currency_list if c.code == 'PEN'), None)

        xpath = "//span[@class='price' and text()[contains(.,'')]]"
        soup = self.get_soup_selenium(provider, xpath)

        data = soup.find_all('span', class_='price')

        buy_price = str(round(Decimal(data[0].text), 4))
        sell_price = str(round(1 / Decimal(data[1].text), 4))

        self.save_to_db(provider, currency_usd, currency_pen, buy_price)
        self.save_to_db(provider, currency_pen, currency_usd, sell_price)

        pass

    def scrape_rextie(self):
        provider = next((p for p in self.provider_list if p.name == "Rextie"), None)
        currency_usd = next((c for c in self.currency_list if c.code == 'USD'), None)
        currency_pen = next((c for c in self.currency_list if c.code == 'PEN'), None)

        xpath = "//div[@class='amount ng-tns-c16-0']"
        soup = self.get_soup_selenium(provider, xpath)

        data = soup.find_all('div', class_='amount ng-tns-c16-0')
        buy_price = str(round(Decimal(data[0].text.replace("S/", '').strip()), 4))
        sell_price = str(round(1 / Decimal(data[1].text.replace("S/", '').strip()), 4))

        self.save_to_db(provider, currency_usd, currency_pen, buy_price)
        self.save_to_db(provider, currency_pen, currency_usd, sell_price)

        pass

    def scrape_securex(self):
        provider = next((p for p in self.provider_list if p.name == "Securex"), None)
        currency_usd = next((c for c in self.currency_list if c.code == 'USD'), None)
        currency_pen = next((c for c in self.currency_list if c.code == 'PEN'), None)

        soup = self.get_soup(provider)

        rates = soup.select('span[style="font-weight: 600 !important;"]')

        buy_price = str(round(Decimal(rates[0].text.strip()), 4))
        sell_price = str(round(1 / Decimal(rates[0].text.strip()), 4))

        self.save_to_db(provider, currency_usd, currency_pen, buy_price)
        self.save_to_db(provider, currency_pen, currency_usd, sell_price)

    def scrape_googlefinance(self, currency_code_from, currency_code_to):
        provider = next((p for p in self.provider_list if p.name == "GoogleFinance"), None)
        currency_from = next((c for c in self.currency_list if c.code == currency_code_from), None)
        currency_to = next((c for c in self.currency_list if c.code == currency_code_to), None)

        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')  # Optional if you want to run the scraper in the background
        driver = webdriver.Chrome(options=options)
        try:
            driver.get("https://www.google.com/finance/quote/{}-{}".format(currency_code_from, currency_code_to))
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='YMlKec fxKbKc']")))
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            data = soup.find_all('div', class_='YMlKec fxKbKc')
            rate = str(round(Decimal(data[0].text.strip()), 4))
            self.save_to_db(provider, currency_from, currency_to, rate)
            pass
        finally:
            driver.quit()

        pass

    @staticmethod
    def get_soup_selenium(provider, xpath):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')

        # open the Selenium web drive
        driver = webdriver.Chrome(options=options)
        try:
            # navigate to website
            driver.get(getattr(provider, 'website'))
            # wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            # get page source after JavaScript has rendered
            html = driver.page_source
            # parse HTML with Beautiful Soup
            soup = BeautifulSoup(html, 'html.parser')
            pass
        finally:
            # close the Selenium web driver
            driver.quit()

        return soup

    @staticmethod
    def get_soup(provider):
        url = getattr(provider, 'website')

        # retrieves  HTML content
        response = requests.get(url)

        #Parsea the HTML content and create a BeautifulSoup object
        soup = BeautifulSoup(response.content, "html.parser")
        return soup

    @staticmethod
    def save_to_db(provider, currency_from, currency_to, exchange_rate):
        rate = CurrencyRate(
                provider=provider,
                currency_from=currency_from,
                currency_to=currency_to,
                exchange_rate=exchange_rate)
        rate.save()

    def run(self):
        self.scrape_googlefinance('USD', 'PEN')
        self.scrape_googlefinance('PEN', 'USD')

        self.scrape_tucambista()
        self.scrape_kambista()
        self.scrape_inkamoney()
        self.scrape_rextie()
        self.scrape_securex()
        self.scrape_tkambio()
        self.scrape_dollarhouse()


if __name__ == '__main__':
    my_object = Scrapers()
    my_object.run()
