from django.db import models

# Create your models here.


class Provider(models.Model):
    name = models.CharField(max_length=200)
    website = models.CharField(max_length=500)
    last_update = models.DateTimeField()
    logo = models.ImageField()
    transaction_time = models.IntegerField()

    def __str__(self):
        return self.name


class Currency(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class CurrencyRate(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    currency_from = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='curency_from', null=True)
    currency_to = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='curency_to', null=True)
    exchange_rate = models.DecimalField(decimal_places=4, max_digits=16)
    date_time = models.DateTimeField()

    def __str__(self):
        return "{}: {} to {} at {}".format(
            self.provider.name,
            self.currency_from.code,
            self.currency_to.code,
            self.date_time)
