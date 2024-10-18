from django.db import models
from django.utils import timezone


# Create your models here.

class StockNews(models.Model):
    symbol = models.CharField(max_length=10)
    published_at = models.DateTimeField(default=timezone.now)
    headline = models.TextField()
    sentiment = models.CharField(max_length=20)
    sentiment_score = models.FloatField()

    def __str__(self):
        return f"{self.symbol} - {self.headline[:50]}"

    class Meta:
        unique_together = ('symbol', 'published_at')

class MetaData(models.Model):
    information = models.CharField(max_length=255)
    symbol = models.CharField(max_length=10)
    last_refreshed = models.DateField()
    time_zone = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.symbol} - {self.last_refreshed}"
    
class StockPrice(models.Model):
        meta_data = models.ForeignKey(MetaData, on_delete=models.CASCADE, related_name='time_series')
        date = models.DateField(unique=True)
        open_price = models.DecimalField(max_digits=14,decimal_places=4)
        close_price = models.DecimalField(max_digits=14, decimal_places=4)
        high_price = models.DecimalField(max_digits=14,decimal_places=4)
        low_price = models.DecimalField(max_digits=14, decimal_places=4)
        volume = models.BigIntegerField()
        class Meta:
            ordering = ['-date']  # Most recent first
            indexes = [
                models.Index(fields=['date']),
            ]