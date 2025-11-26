import yfinance as yf
import json

ticker = "TSM"
stock = yf.Ticker(ticker)
info = stock.info

print(json.dumps({
    "dividendYield": info.get("dividendYield"),
    "trailingAnnualDividendYield": info.get("trailingAnnualDividendYield"),
    "dividendRate": info.get("dividendRate"),
    "trailingAnnualDividendRate": info.get("trailingAnnualDividendRate"),
    "currentPrice": info.get("currentPrice"),
    "regularMarketPrice": info.get("regularMarketPrice"),
    "previousClose": info.get("previousClose")
}, indent=2))
