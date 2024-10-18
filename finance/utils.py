from .models import StockNews
from datetime import datetime
from django.utils import timezone
import pytz
import pandas as pd
from prophet import Prophet
import psycopg2
from django.conf import settings




# Helper function to convert the timestamp format
def parse_timestamp(ts):
    try:
        naive_datetime = datetime.strptime(ts, "%Y%m%dT%H%M%S")
        aware_datetime = pytz.UTC.localize(naive_datetime)
        return aware_datetime
    except ValueError as e:
        print(f"Error parsing timestamp {ts}: {e}")
        return timezone.now()

def backtest_with_news(symbol, initial_investment):
    # Fetch the news data from the database
    news = StockNews.objects.filter(symbol=symbol).order_by('published_at')
    if not news.exists():
        raise ValueError(f"No news data found for symbol: {symbol}")

    # Create a DataFrame from the query
    df = pd.DataFrame(list(news.values('published_at', 'sentiment', 'sentiment_score')))
    df['published_at'] = pd.to_datetime(df['published_at'])
    df.set_index('published_at', inplace=True)

    # Simulate investment strategy based on sentiment
    cash = initial_investment
    holdings = 0

    for _, row in df.iterrows():
        if row['sentiment'] == 'Positive' and cash > 0:
            # Buy stocks with all available cash
            holdings = cash
            cash = 0
        elif row['sentiment'] == 'Negative' and holdings > 0:
            # Sell all holdings
            cash = holdings
            holdings = 0

    final_value = cash + holdings
    return {
        'total_return': (final_value - initial_investment) / initial_investment * 100,
        'final_value': final_value
    }







