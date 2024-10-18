from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
import requests
from django.utils import timezone
import pytz
import pandas as pd
from prophet import Prophet # type: ignore
import psycopg2

from finance.models import StockNews, StockPrice, MetaData
from .utils import backtest_with_news

import matplotlib.pyplot as plt

from django.http import JsonResponse
from django.http import JsonResponse, HttpResponse

from django.conf import settings
from reportlab.graphics.charts.linecharts import LineChart
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


API_KEY = settings.API_KEY
BASE_URL = 'https://www.alphavantage.co/query'

database_user = settings.DATABASE_USER
database_password = settings.DATABASE_PASSWORD
database_name = settings.DATABASE_NAME
database_port = settings.DATABASE_PORT
database_host = settings.DATABASE_HOST
figure1, figure2 = None, None

def fetch_stock_news(request, symbol='AAPL'):
    url = f"{BASE_URL}?function=NEWS_SENTIMENT&tickers={symbol}&apikey={API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        return HttpResponse(f"Error fetching data: {response.status_code}", status=500)

    data = response.json()
    print(data)
    if "feed" not in data:
        return HttpResponse("No news data found.", status=404)

    # Helper function to convert the timestamp format
    def parse_timestamp(ts):
        try:
            naive_datetime = datetime.strptime(ts, "%Y%m%dT%H%M%S")
            aware_datetime = pytz.UTC.localize(naive_datetime)
            return aware_datetime
        except ValueError as e:
            print(f"Error parsing timestamp {ts}: {e}")
            return timezone.now()

    # Parse and store news data
    news_list = []
    # aware_datetime = timezone.make_aware(parse_timestamp(news["time_published"]))
    for news in data["feed"]:
        try:
            news_item = StockNews(
                symbol=symbol,
                published_at=parse_timestamp(news["time_published"]),
                headline=news["title"],
                sentiment=news["overall_sentiment_label"],
                sentiment_score=float(news["overall_sentiment_score"]),
            )
            news_list.append(news_item)
        except Exception as e:
            print(f"Error saving news item: {e}")

    # Bulk create news entries
    StockNews.objects.bulk_create(news_list, ignore_conflicts=True)

    return JsonResponse({"message": f"News data for {symbol} stored successfully."})



 # Import the models

def fetch_stock_prices(request, symbol):
    print(symbol)
    url = f"{BASE_URL}?function=TIME_SERIES_MONTHLY&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return HttpResponse(f"Error fetching data: {response.status_code}", status=500)

    data = response.json()
    print(data)
    
    if "Monthly Time Series" not in data or "Meta Data" not in data:
        return HttpResponse("No monthly trading data or meta data found.", status=404)

    # Extract meta data
    meta_data = data["Meta Data"]
    
    try:
        # Get or create MetaData object
        metadata_obj, created = MetaData.objects.update_or_create(
            symbol=meta_data["2. Symbol"],
            defaults={
                'information': meta_data["1. Information"],
                'last_refreshed': datetime.strptime(meta_data["3. Last Refreshed"], '%Y-%m-%d').date(),
                'time_zone': meta_data["4. Time Zone"],
            }
        )
    except Exception as e:
        return HttpResponse(f"Error saving meta data: {e}", status=500)

    # Extract and save monthly time series data
    price_list = []
    for date_str, price_data in data["Monthly Time Series"].items():
        try:
            date =  datetime.strptime(date_str, '%Y-%m-%d').date()
            price_item = StockPrice(
                meta_data=metadata_obj,
                date=date,
                open_price=price_data['1. open'],
                high_price=price_data['2. high'],
                low_price=price_data['3. low'],
                close_price=price_data['4. close'],
                volume=price_data['5. volume']
            )
            price_list.append(price_item)
        except Exception as e:
            print(f"Error processing price data for {date_str}: {e}")

    # Bulk create the monthly time series records
    try:
        StockPrice.objects.bulk_create(price_list, ignore_conflicts=True)
    except Exception as e:
        return HttpResponse(f"Error saving price data: {e}", status=500)

    return JsonResponse({"message": f"Price data for {symbol} stored successfully."})

     
     
def make_prediction(request):
    # connection_string = f"postgresql://{database_user}:{database_password}@{database_host}:{database_port}/{database_name}"
    # conn = psycopg2.connect(connection_string)

    # sql_query = "SELECT * FROM  finance_stockprice"
    # df = pd.read_sql_query(sql_query, conn)
    # conn.close()
    data = StockPrice.objects.all()

    df = pd.DataFrame(data.values())

    df['ds'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

    # Keep only the relevant columns for Prophet
    df = df[['ds', 'close_price']]
    df.rename(columns={'close_price': 'y'}, inplace=True)

    model = Prophet()
    model.fit(df)

    # # Create a future DataFrame with the desired prediction horizon
    future = model.make_future_dataframe(periods=30)  # Predict for the next 30 days

    # Make predictions
    forecast = model.predict(future)

    figure1 = model.plot(forecast)

    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.title('Stock Price Prediction')
    plt.show()
    
    figure2 = model.plot_components(forecast)
    plt.show()

    return JsonResponse({"forecast": df.to_json(orient='records')})

def generate_report(request):
    data = StockPrice.objects.all()

    df = pd.DataFrame(data.values())

    df['ds'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

    # Keep only the relevant columns for Prophet
    df = df[['ds', 'close_price']]
    df.rename(columns={'close_price': 'y'}, inplace=True)

    model = Prophet()
    model.fit(df)

    # # Create a future DataFrame with the desired prediction horizon
    future = model.make_future_dataframe(periods=30)  # Predict for the next 30 days

    # Make predictions
    forecast = model.predict(future)

    figure1 = model.plot(forecast)

    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.title('Stock Price Prediction')
    plt.show()

    drawing1 = figure1.gcf()
    
    figure2 = model.plot_components(forecast)
    plt.show()

    drawing2 = figure2.gcf()

    # Create a PDF document
    pdf = canvas.Canvas('your_graph.pdf', pagesize=A4)

    drawing1.save(pdf, scale=1)
    drawing2.save(pdf, scale=2)



def backtest_view(request, symbol):
    print(symbol)
    symbol = request.GET.get('symbol', symbol)
    initial_investment = float(request.GET.get('initial_investment', 10000))

    try:
        result = backtest_with_news(symbol, initial_investment)
        return JsonResponse(result)
    except ValueError as e:
        return HttpResponseBadRequest(str(e))