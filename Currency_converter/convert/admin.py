from django.contrib import admin
from .models import Provider, Currency, CurrencyRate

# Register your models here.


admin.site.register(Provider)
admin.site.register(Currency)
admin.site.register(CurrencyRate)
