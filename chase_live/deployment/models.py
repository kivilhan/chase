from django.db import models

class Trader(models.Model):
    title = models.CharField(max_length=20)
    gains = models.FloatField(default=0)
    last_seen = models.CharField(max_length=40, default="Never")
    description = models.TextField()
    name = models.CharField(max_length=40, default="Lil Warren")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('trader-detail', kwargs={'pk': self.pk})

class Order(models.Model):
    pkid = models.CharField(max_length=40)
    symbol = models.CharField(max_length=20)
    qty = models.CharField(max_length=20)
    side = models.CharField(max_length=20)
    price = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    submit = models.CharField(max_length=20)
    fill = models.CharField(max_length=20)
    owner = models.ForeignKey(Trader, on_delete=models.CASCADE)

class Position(models.Model):
    symbol = models.CharField(max_length=20)
    qty = models.CharField(max_length=20)
    value = models.CharField(max_length=20)
    gain = models.CharField(max_length=20)
    owner = models.ForeignKey(Trader, on_delete=models.CASCADE)