from django.urls import path

from .views import backtest_view, fetch_stock_news, fetch_stock_prices, make_prediction, generate_report

urlpatterns = [
    path('fetch-news/', fetch_stock_news),
    path('backtest/<str:symbol>', backtest_view),
    path('monthly-stock-prices/<str:symbol>', fetch_stock_prices),
    path('make_prediction/',make_prediction),
    path('generate-report/',generate_report)
]
