from django.db.models import OuterRef, Subquery, ExpressionWrapper, DecimalField, Max
from django.shortcuts import render

from .models import Provider, Currency, CurrencyRate
from .Spiders import Scrapers
from django.views.generic import ListView


def index(request):
    scrapers = Scrapers()
   # scrapers.run()
    provider_list = Provider.objects.all()
    neutral_provider = Provider.objects.get(is_neutral__exact=True)
    currency_list = Currency.objects.all()

    usd = currency_list.get(code__exact='USD')
    pen = currency_list.get(code__exact='PEN')
    usd_to_pen_rate_list = CurrencyRate.objects.filter(
        currency_from=usd,
        currency_to=pen,
        date_time=Subquery(
            CurrencyRate.objects.filter(
                currency_from=OuterRef('currency_from'),
                currency_to=OuterRef('currency_to'),
                provider=OuterRef('provider')
            ).order_by('-date_time').values('date_time')[:1]
        )
    ).values(
        'provider',
        'exchange_rate',
        'date_time',
    )

    pen_to_usd_rate_list = CurrencyRate.objects.filter(
        currency_from=pen,
        currency_to=usd,
        date_time=Subquery(
            CurrencyRate.objects.filter(
                currency_from=OuterRef('currency_from'),
                currency_to=OuterRef('currency_to'),
                provider=OuterRef('provider')
            ).order_by('-date_time').values('date_time')[:1]
        )
    ).values(
        'provider',
        'exchange_rate',
        'date_time',
    )

    context = {
        'provider_list': provider_list,
        'currency_list': currency_list,
        'USDtoPEN_rate_list': usd_to_pen_rate_list,
        'PENtoUSD_rate_list': pen_to_usd_rate_list,
        'neutral_provider': neutral_provider,

    }
    return render(request, 'convert/index.html', context)


class CurrencyRateListView(ListView):
    model = CurrencyRate
    template_name = 'convert/currency_rate_list.html'


    def get_queryset(self):

        currency_from = Currency.objects.get(code=self.kwargs['currency_from'])
        currency_to = Currency.objects.get(code=self.kwargs['currency_to'])

        # Filter the CurrencyRate queryset to only include the latest rates for each provider
        qs = CurrencyRate.objects.filter(
            currency_from=currency_from,
            currency_to=currency_to,
            date_time=Subquery(
                CurrencyRate.objects.filter(
                    currency_from=OuterRef('currency_from'),
                    currency_to=OuterRef('currency_to'),
                    provider=OuterRef('provider')
                ).order_by('-date_time').values('date_time')[:1]
                    )
        ).values(
            'provider',
            'exchange_rate',
            'date_time',
        )

        return qs
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['provider_list'] = Provider.objects.all()
        context['currency_from'] = Currency.objects.get(code=self.kwargs['currency_from'])
        context['currency_to'] = Currency.objects.get(code=self.kwargs['currency_to'])
        return context

def about(request):
    return render(request, 'convert/about.html')


def contact(request):
    return render(request, 'convert/contact.html')
