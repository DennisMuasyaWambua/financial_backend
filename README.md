***Finance API***

`/finance/monthly-stock-prices/<str:symbol>` fetches monthly stock prices with the stock symbol being appended at the end


`/finance/backtest/<str:symbol>`used to perform backtesting on the stock symbol being appended at the end


`/finance/make_prediction/` used to make a prediction on the data stored in the database


`/finance/generate-report/` used to generate a report


`finance/fetch-news/` used to get data and sentimental analysis on the data


Facebook prophet model was was utilized for timeseries forecasting of the the closing prices of stocks 