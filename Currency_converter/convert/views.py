from django.db.models import OuterRef, Subquery
from django.shortcuts import render

from .models import Provider, Currency, CurrencyRate
from .Spiders import Scrapers
from django.views.generic import ListView
import matplotlib.pyplot as plt
import mplcursors
import mpld3


def index(request):
    scrapers = Scrapers()
 #   scrapers.run()

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

    usd_to_pen_chart = create_rate_chart(
        'USD',
        'PEN',
        provider_list,
    )

    pen_to_usd_chart = create_rate_chart(
        'PEN',
        'USD',
        provider_list
    )

    context = {
        'provider_list': provider_list,
        'currency_list': currency_list,
        'USDtoPEN_rate_list': usd_to_pen_rate_list,
        'PENtoUSD_rate_list': pen_to_usd_rate_list,
        'neutral_provider': neutral_provider,
        'chart1': usd_to_pen_chart,
        'chart2': pen_to_usd_chart,
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

        context['chart'] = create_rate_chart(self.kwargs['currency_from'],
                                             self.kwargs['currency_to'],
                                             Provider.objects.all())
        return context


def create_rate_chart(form_code, to_code, provider_list):
    fig, ax = plt.subplots(figsize=(6, 4))

    for provider in provider_list:
        # Get the currency rate data for each provider
        rates = CurrencyRate.objects \
            .filter(provider=provider, currency_from__code=form_code, currency_to__code=to_code) \
            .order_by('date_time')
        dates = [rate.date_time for rate in rates]
        rates = [rate.exchange_rate for rate in rates]
        print(provider.name)
        for date in dates:
            print(date)
        # Add a line to the graph for each provider
        line, = ax.plot(dates, rates, label=provider.name)

        # Add annotation to show provider name on hover
        mplcursors.cursor(line).connect(
            "add", lambda sel: sel.annotation.set_text(provider.name))

    # Add labels and legend
    ax.set_xlabel('Date')
    ax.set_ylabel('{} to {} Exchange Rate'.format(form_code, to_code))
    ax.set_title('{} to {} Exchange Rates'.format(form_code, to_code))
    ax.legend()

    # Convert the plot to an interactive HTML format using mpld3
    interactive_graphic = mpld3.fig_to_html(fig)

    return interactive_graphic


def about(request):
    return render(request, 'convert/about.html')


def contact(request):
    return render(request, 'convert/contact.html')
