# Generated by Django 5.1.2 on 2024-10-18 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockNews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=10)),
                ('published_at', models.DateTimeField()),
                ('headline', models.TextField()),
                ('sentiment', models.CharField(max_length=20)),
                ('sentiment_score', models.FloatField()),
            ],
            options={
                'unique_together': {('symbol', 'published_at')},
            },
        ),
        migrations.DeleteModel(
            name='StockData',
        ),
    ]
