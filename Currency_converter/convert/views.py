from django.db.models import OuterRef, Subquery, ExpressionWrapper, DecimalField, Max
from django.shortcuts import render

from .models import Provider, Currency, CurrencyRate
from .Spiders import Scrapers


def index(request):
    scrapers = Scrapers()
    scrapers.run()
    provider_list = Provider.objects.all()
    currency_list = Currency.objects.all()
    currency_rate_list = CurrencyRate.objects.values('provider', 'exchange_rate', 'date_time')\
        .annotate(latest_date=Max('date_time') )\
        .distinct()
    context = {
        'provider_list': provider_list,
        'currency_list': currency_list,
        'rate_list': currency_rate_list,
    }
    return render(request, 'convert/index.html', context)
