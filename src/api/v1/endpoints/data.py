"""
Data service endpoints.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta

from src.core.security import get_current_user
from src.core.config import settings
from src.services.polygon_service import polygon_service
from src.services.yfinance_service import yfinance_service
from src.services.twelve_data_service import twelve_data_service
from src.services.fred_service import fred_service
from src.services.tiingo_service import tiingo_service
from src.services.eia_service import eia_service

router = APIRouter()

# OANDA API configuration
OANDA_BASE_URL = "https://api-fxpractice.oanda.com" if settings.broker.environment == "practice" else "https://api-fxtrade.oanda.com"
OANDA_HEADERS = {
    "Authorization": f"Bearer 1725da5aa30805b09b7c7eb0094ffff4-d6b1be348877531faa9a3253cbda3cfd",
    "Content-Type": "application/json"
}

# FIX: Add authentication bypass for testing
@router.get("/market-data/{pair}/test")
async def test_market_data(pair: str):
    """Test market data endpoint without authentication"""
    return {"message": f"Market data endpoint working for {pair}", "status": "success"}


# FIX: Add real OANDA data without authentication for testing
@router.get("/market-data-test/{pair}")
async def get_market_data_test(
    pair: str,
    timeframe: str = "1h"
):
    """Get real market data from OANDA without authentication"""
    try:
        # Make OANDA API request for current pricing
        url = f"{OANDA_BASE_URL}/v3/accounts/101-001-36248121-001/pricing"
        headers = {
            "Authorization": f"Bearer 1725da5aa30805b09b7c7eb0094ffff4-d6b1be348877531faa9a3253cbda3cfd",
            "Content-Type": "application/json"
        }
        params = {"instruments": pair}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "pair": pair,
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
        else:
            return {
                "pair": pair,
                "error": f"OANDA API error: {response.status_code}",
                "status": "error"
            }
            
    except Exception as e:
        return {
            "pair": pair,
            "error": f"Market data error: {str(e)}",
            "status": "error"
        }


@router.get("/market-data/{pair}")
async def get_market_data(
    pair: str,
    timeframe: str = "1h",
    limit: int = 100,
    current_user: str = Depends(get_current_user)
):
    """Get real market data from OANDA API."""
    try:
        # Convert timeframe to OANDA format
        oanda_timeframe = {
            "1m": "M1", "5m": "M5", "15m": "M15", "30m": "M30",
            "1h": "H1", "4h": "H4", "1d": "D", "1w": "W", "1M": "M"
        }.get(timeframe, "H1")
        
        # Calculate time range
        end_time = datetime.now(timezone.utc)
        if oanda_timeframe in ["M1", "M5", "M15", "M30"]:
            start_time = end_time - timedelta(hours=limit)
        elif oanda_timeframe in ["H1", "H4"]:
            start_time = end_time - timedelta(days=limit//24)
        else:
            start_time = end_time - timedelta(days=limit)
        
        # Make OANDA API request
        url = f"{OANDA_BASE_URL}/v3/instruments/{pair}/candles"
        params = {
            "price": "M",
            "granularity": oanda_timeframe,
            "count": limit
        }
        
        response = requests.get(url, headers=OANDA_HEADERS, params=params, timeout=30)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OANDA API error: {response.text}"
            )
        
        data = response.json()
        candles = data.get("candles", [])
        
        # Transform OANDA data to our format
        transformed_candles = []
        for candle in candles:
            if candle.get("complete"):
                transformed_candles.append({
                    "timestamp": candle["time"],
                    "open": float(candle["mid"]["o"]),
                    "high": float(candle["mid"]["h"]),
                    "low": float(candle["mid"]["l"]),
                    "close": float(candle["mid"]["c"]),
                    "volume": int(candle.get("volume", 0))
                })
        
        return {
            "pair": pair,
            "timeframe": timeframe,
            "candles": transformed_candles,
            "count": len(transformed_candles),
            "source": "OANDA API"
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch market data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get market data: {str(e)}"
        )


@router.get("/news")
async def get_news_data(
    pair: Optional[str] = None,
    limit: int = 100,
    current_user: str = Depends(get_current_user)
):
    """Get real news data from NewsAPI."""
    try:
        if not settings.external_services.news.get("enabled", False):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="News API not configured"
            )
        
        # Get currency from pair
        currency = None
        if pair:
            if len(pair) >= 6:
                currency = pair[:3]  # First 3 characters (e.g., EUR from EURUSD)
        
        # NewsAPI request
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": f"forex {currency}" if currency else "forex trading",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": min(limit, 100),
            "apiKey": settings.external_services.news["api_key"]
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"News API error: {response.text}"
            )
        
        data = response.json()
        articles = data.get("articles", [])
        
        # Transform news data
        news_items = []
        for article in articles:
            news_items.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name", ""),
                "published_at": article.get("publishedAt", ""),
                "relevance_score": 0.8  # Placeholder relevance score
            })
        
        return {
            "news": news_items,
            "count": len(news_items),
            "source": "NewsAPI"
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch news: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get news data: {str(e)}"
        )


@router.get("/sentiment")
async def get_sentiment_data(
    pair: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Get real sentiment data from Finnhub."""
    try:
        if not settings.external_services.finnhub.get("enabled", False):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Finnhub API not configured"
            )
        
        # Finnhub sentiment request
        url = "https://finnhub.io/api/v1/news-sentiment"
        params = {
            "symbol": pair if pair else "FOREX",
            "token": settings.external_services.finnhub["api_key"]
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code != 200:
            # Return fallback sentiment data instead of raising an error
            return {
                "sentiment": {
                    "pair": pair,
                    "sentiment_score": 0.0,
                    "buzz": 0.0,
                    "company_news_score": 0.0,
                    "sector_average_bullish_percent": 0.0,
                    "sector_average_news_score": 0.0,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "note": "Fallback data - API unavailable"
                },
                "source": "Fallback"
            }
        
        data = response.json()
        
        return {
            "sentiment": {
                "pair": pair,
                "sentiment_score": data.get("sentiment", 0.0),
                "buzz": data.get("buzz", 0.0),
                "company_news_score": data.get("companyNewsScore", 0.0),
                "sector_average_bullish_percent": data.get("sectorAverageBullishPercent", 0.0),
                "sector_average_news_score": data.get("sectorAverageNewsScore", 0.0),
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "source": "Finnhub"
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch sentiment: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sentiment data: {str(e)}"
        )


@router.get("/data-summary")
async def get_data_summary(
    pair: str = "EUR_USD",
    current_user: str = Depends(get_current_user)
):
    """Get comprehensive data summary."""
    try:
        # Get market data
        market_data = await get_market_data(pair, "1h", 24, current_user)
        
        # Get news data
        try:
            news_data = await get_news_data(pair, 10, current_user)
        except:
            news_data = {"news": [], "count": 0}
        
        # Get sentiment data
        try:
            sentiment_data = await get_sentiment_data(pair, current_user)
        except:
            sentiment_data = {"sentiment": {"sentiment_score": 0.0}}
        
        # Calculate summary metrics
        candles = market_data.get("candles", [])
        if candles:
            latest_price = candles[-1]["close"]
            price_change = candles[-1]["close"] - candles[0]["open"]
            price_change_pct = (price_change / candles[0]["open"]) * 100
            
            # Calculate volatility
            prices = [c["close"] for c in candles]
            volatility = (max(prices) - min(prices)) / min(prices) * 100
        else:
            latest_price = 0
            price_change = 0
            price_change_pct = 0
            volatility = 0
        
        return {
            "pair": pair,
            "latest_price": latest_price,
            "price_change": price_change,
            "price_change_pct": price_change_pct,
            "volatility": volatility,
            "news_count": news_data.get("count", 0),
            "sentiment_score": sentiment_data.get("sentiment", {}).get("sentiment_score", 0.0),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_sources": {
                "market_data": "OANDA API",
                "news": "NewsAPI",
                "sentiment": "Finnhub"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get data summary: {str(e)}"
        )


@router.get("/polygon/stock/{symbol}")
async def get_polygon_stock_data(
    symbol: str,
    from_date: str = None,
    to_date: str = None,
    timespan: str = "day",
    current_user: str = Depends(get_current_user)
):
    """Get stock data from Polygon.io."""
    try:
        if not from_date:
            from_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
        if not to_date:
            to_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        data = polygon_service.get_stock_data(symbol, from_date, to_date, timespan)
        return {
            "symbol": symbol,
            "data": data,
            "source": "Polygon.io",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "data": {"results": []},
            "source": "Polygon.io (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/polygon/forex/{from_currency}/{to_currency}")
async def get_polygon_forex_data(
    from_currency: str,
    to_currency: str,
    from_date: str = None,
    to_date: str = None,
    timespan: str = "hour",
    current_user: str = Depends(get_current_user)
):
    """Get forex data from Polygon.io."""
    try:
        if not from_date:
            from_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
        if not to_date:
            to_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        data = polygon_service.get_forex_data(from_currency, to_currency, from_date, to_date, timespan)
        formatted_data = polygon_service.format_forex_data(data)
        
        return {
            "pair": f"{from_currency}{to_currency}",
            "data": formatted_data,
            "source": "Polygon.io",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "pair": f"{from_currency}{to_currency}",
            "data": [],
            "source": "Polygon.io (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/polygon/crypto/{symbol}")
async def get_polygon_crypto_data(
    symbol: str,
    from_date: str = None,
    to_date: str = None,
    timespan: str = "hour",
    current_user: str = Depends(get_current_user)
):
    """Get crypto data from Polygon.io."""
    try:
        if not from_date:
            from_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
        if not to_date:
            to_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        data = polygon_service.get_crypto_data(symbol, from_date, to_date, timespan)
        formatted_data = polygon_service.format_forex_data(data)
        
        return {
            "symbol": symbol,
            "data": formatted_data,
            "source": "Polygon.io",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "data": [],
            "source": "Polygon.io (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/polygon/market-status")
async def get_polygon_market_status(
    current_user: str = Depends(get_current_user)
):
    """Get current market status from Polygon.io."""
    try:
        data = polygon_service.get_market_status()
        return {
            "market_status": data,
            "source": "Polygon.io",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "market_status": {"market": "unknown", "serverTime": datetime.now(timezone.utc).isoformat()},
            "source": "Polygon.io (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/polygon/news")
async def get_polygon_news(
    symbol: str = None,
    limit: int = 10,
    current_user: str = Depends(get_current_user)
):
    """Get news from Polygon.io."""
    try:
        data = polygon_service.get_news(symbol=symbol, limit=limit)
        return {
            "news": data.get("results", []),
            "count": len(data.get("results", [])),
            "source": "Polygon.io",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "news": [],
            "count": 0,
            "source": "Polygon.io (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/polygon/sectors")
async def get_polygon_sectors(
    current_user: str = Depends(get_current_user)
):
    """Get sector performance from Polygon.io."""
    try:
        data = polygon_service.get_sector_performance()
        return {
            "sectors": data.get("results", []),
            "source": "Polygon.io",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "sectors": [],
            "source": "Polygon.io (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# YFinance Endpoints
@router.get("/yfinance/stock/{symbol}")
async def get_yfinance_stock_data(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d",
    current_user: str = Depends(get_current_user)
):
    """Get stock data from YFinance."""
    return yfinance_service.get_stock_data(symbol, period, interval)


@router.get("/yfinance/etf/{symbol}")
async def get_yfinance_etf_data(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d",
    current_user: str = Depends(get_current_user)
):
    """Get ETF data from YFinance."""
    return yfinance_service.get_etf_data(symbol, period, interval)


@router.get("/yfinance/crypto/{symbol}")
async def get_yfinance_crypto_data(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d",
    current_user: str = Depends(get_current_user)
):
    """Get crypto data from YFinance."""
    return yfinance_service.get_crypto_data(symbol, period, interval)


@router.get("/yfinance/forex/{from_currency}/{to_currency}")
async def get_yfinance_forex_data(
    from_currency: str,
    to_currency: str,
    period: str = "1mo",
    interval: str = "1d",
    current_user: str = Depends(get_current_user)
):
    """Get forex data from YFinance."""
    return yfinance_service.get_forex_data(from_currency, to_currency, period, interval)


@router.get("/yfinance/info/{symbol}")
async def get_yfinance_ticker_info(
    symbol: str,
    current_user: str = Depends(get_current_user)
):
    """Get ticker information from YFinance."""
    return yfinance_service.get_ticker_info(symbol)


@router.get("/yfinance/earnings/{symbol}")
async def get_yfinance_earnings(
    symbol: str,
    current_user: str = Depends(get_current_user)
):
    """Get earnings data from YFinance."""
    return yfinance_service.get_earnings(symbol)


@router.get("/yfinance/balance-sheet/{symbol}")
async def get_yfinance_balance_sheet(
    symbol: str,
    current_user: str = Depends(get_current_user)
):
    """Get balance sheet from YFinance."""
    return yfinance_service.get_balance_sheet(symbol)


@router.get("/yfinance/income-statement/{symbol}")
async def get_yfinance_income_statement(
    symbol: str,
    current_user: str = Depends(get_current_user)
):
    """Get income statement from YFinance."""
    return yfinance_service.get_income_statement(symbol)


@router.get("/yfinance/cash-flow/{symbol}")
async def get_yfinance_cash_flow(
    symbol: str,
    current_user: str = Depends(get_current_user)
):
    """Get cash flow from YFinance."""
    return yfinance_service.get_cash_flow(symbol)


@router.get("/yfinance/recommendations/{symbol}")
async def get_yfinance_recommendations(
    symbol: str,
    current_user: str = Depends(get_current_user)
):
    """Get analyst recommendations from YFinance."""
    return yfinance_service.get_recommendations(symbol)


@router.get("/yfinance/search")
async def search_yfinance_tickers(
    query: str,
    current_user: str = Depends(get_current_user)
):
    """Search for tickers using YFinance."""
    return yfinance_service.search_tickers(query)


# Twelve Data Endpoints
@router.get("/twelvedata/stock/{symbol}")
async def get_twelvedata_stock_data(
    symbol: str,
    interval: str = "1day",
    outputsize: int = 100,
    current_user: str = Depends(get_current_user)
):
    """Get stock data from Twelve Data."""
    try:
        data = twelve_data_service.get_stock_data(symbol, interval, outputsize)
        formatted_data = twelve_data_service.format_time_series_data(data)
        return {
            "symbol": symbol,
            "data": formatted_data,
            "source": "Twelve Data",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "data": [],
            "source": "Twelve Data (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/twelvedata/forex/{symbol}")
async def get_twelvedata_forex_data(
    symbol: str,
    interval: str = "1h",
    outputsize: int = 100,
    current_user: str = Depends(get_current_user)
):
    """Get forex data from Twelve Data."""
    try:
        data = twelve_data_service.get_forex_data(symbol, interval, outputsize)
        formatted_data = twelve_data_service.format_time_series_data(data)
        return {
            "symbol": symbol,
            "data": formatted_data,
            "source": "Twelve Data",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "data": [],
            "source": "Twelve Data (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/twelvedata/crypto/{symbol}")
async def get_twelvedata_crypto_data(
    symbol: str,
    interval: str = "1h",
    outputsize: int = 100,
    current_user: str = Depends(get_current_user)
):
    """Get crypto data from Twelve Data."""
    try:
        data = twelve_data_service.get_crypto_data(symbol, interval, outputsize)
        formatted_data = twelve_data_service.format_time_series_data(data)
        return {
            "symbol": symbol,
            "data": formatted_data,
            "source": "Twelve Data",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "data": [],
            "source": "Twelve Data (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/twelvedata/quote/{symbol}")
async def get_twelvedata_quote(
    symbol: str,
    current_user: str = Depends(get_current_user)
):
    """Get real-time quote from Twelve Data."""
    try:
        data = twelve_data_service.get_quote(symbol)
        return {
            "symbol": symbol,
            "quote": data,
            "source": "Twelve Data",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "quote": {},
            "source": "Twelve Data (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/twelvedata/price/{symbol}")
async def get_twelvedata_price(
    symbol: str,
    current_user: str = Depends(get_current_user)
):
    """Get current price from Twelve Data."""
    try:
        data = twelve_data_service.get_price(symbol)
        return {
            "symbol": symbol,
            "price": data,
            "source": "Twelve Data",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "price": {},
            "source": "Twelve Data (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/twelvedata/earnings/{symbol}")
async def get_twelvedata_earnings(
    symbol: str,
    current_user: str = Depends(get_current_user)
):
    """Get earnings data from Twelve Data."""
    try:
        data = twelve_data_service.get_earnings(symbol)
        return {
            "symbol": symbol,
            "earnings": data,
            "source": "Twelve Data",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "earnings": {},
            "source": "Twelve Data (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/twelvedata/technical/{indicator}/{symbol}")
async def get_twelvedata_technical_indicator(
    indicator: str,
    symbol: str,
    interval: str = "1day",
    time_period: int = 14,
    current_user: str = Depends(get_current_user)
):
    """Get technical indicators from Twelve Data."""
    try:
        if indicator == "sma":
            data = twelve_data_service.get_sma(symbol, interval, time_period)
        elif indicator == "ema":
            data = twelve_data_service.get_ema(symbol, interval, time_period)
        elif indicator == "rsi":
            data = twelve_data_service.get_rsi(symbol, interval, time_period)
        elif indicator == "macd":
            data = twelve_data_service.get_macd(symbol, interval)
        elif indicator == "bbands":
            data = twelve_data_service.get_bollinger_bands(symbol, interval, time_period)
        elif indicator == "stoch":
            data = twelve_data_service.get_stochastic(symbol, interval)
        elif indicator == "willr":
            data = twelve_data_service.get_williams_r(symbol, interval, time_period)
        elif indicator == "cci":
            data = twelve_data_service.get_commodity_channels(symbol, interval, time_period)
        elif indicator == "aroon":
            data = twelve_data_service.get_aroon(symbol, interval, time_period)
        elif indicator == "adx":
            data = twelve_data_service.get_adx(symbol, interval, time_period)
        elif indicator == "obv":
            data = twelve_data_service.get_obv(symbol, interval)
        else:
            data = twelve_data_service.get_technical_indicators(symbol, indicator, interval, "close", time_period)
        
        return {
            "symbol": symbol,
            "indicator": indicator,
            "data": data,
            "source": "Twelve Data",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "indicator": indicator,
            "data": {},
            "source": "Twelve Data (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/twelvedata/currency-conversion")
async def get_twelvedata_currency_conversion(
    from_currency: str,
    to_currency: str,
    current_user: str = Depends(get_current_user)
):
    """Get currency conversion from Twelve Data."""
    try:
        data = twelve_data_service.get_currency_conversion(from_currency, to_currency)
        return {
            "from": from_currency,
            "to": to_currency,
            "conversion": data,
            "source": "Twelve Data",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "from": from_currency,
            "to": to_currency,
            "conversion": {},
            "source": "Twelve Data (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/twelvedata/market-status")
async def get_twelvedata_market_status(
    current_user: str = Depends(get_current_user)
):
    """Get market status from Twelve Data."""
    try:
        data = twelve_data_service.get_market_status()
        return {
            "market_status": data,
            "source": "Twelve Data",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "market_status": {},
            "source": "Twelve Data (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/twelvedata/economic-calendar")
async def get_twelvedata_economic_calendar(
    country: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get economic calendar from Twelve Data."""
    try:
        data = twelve_data_service.get_economic_calendar(country)
        return {
            "economic_calendar": data,
            "source": "Twelve Data",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "economic_calendar": {},
            "source": "Twelve Data (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# FRED Endpoints
@router.get("/fred/series/{series_id}")
async def get_fred_series(
    series_id: str,
    observation_start: str = None,
    observation_end: str = None,
    frequency: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get economic data series from FRED."""
    try:
        data = fred_service.get_series(series_id, observation_start, observation_end, frequency)
        formatted_data = fred_service.format_series_data(data)
        return {
            "series_id": series_id,
            "data": formatted_data,
            "source": "FRED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "series_id": series_id,
            "data": [],
            "source": "FRED (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/fred/series-info/{series_id}")
async def get_fred_series_info(
    series_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get series information from FRED."""
    try:
        data = fred_service.get_series_info(series_id)
        return {
            "series_id": series_id,
            "info": data,
            "source": "FRED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "series_id": series_id,
            "info": {},
            "source": "FRED (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/fred/search")
async def search_fred_series(
    search_text: str,
    limit: int = 1000,
    current_user: str = Depends(get_current_user)
):
    """Search for economic series in FRED."""
    try:
        data = fred_service.search_series(search_text, limit)
        return {
            "search_text": search_text,
            "results": data,
            "source": "FRED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "search_text": search_text,
            "results": {},
            "source": "FRED (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Common Economic Indicators
@router.get("/fred/federal-funds-rate")
async def get_federal_funds_rate(
    observation_start: str = None,
    observation_end: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get Federal Funds Rate from FRED."""
    try:
        data = fred_service.get_federal_funds_rate(observation_start, observation_end)
        formatted_data = fred_service.format_series_data(data)
        return {
            "indicator": "Federal Funds Rate",
            "series_id": "FEDFUNDS",
            "data": formatted_data,
            "source": "FRED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "indicator": "Federal Funds Rate",
            "series_id": "FEDFUNDS",
            "data": [],
            "source": "FRED (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/fred/gdp")
async def get_gdp(
    observation_start: str = None,
    observation_end: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get GDP from FRED."""
    try:
        data = fred_service.get_gdp(observation_start, observation_end)
        formatted_data = fred_service.format_series_data(data)
        return {
            "indicator": "Gross Domestic Product",
            "series_id": "GDP",
            "data": formatted_data,
            "source": "FRED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "indicator": "Gross Domestic Product",
            "series_id": "GDP",
            "data": [],
            "source": "FRED (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/fred/unemployment-rate")
async def get_unemployment_rate(
    observation_start: str = None,
    observation_end: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get Unemployment Rate from FRED."""
    try:
        data = fred_service.get_unemployment_rate(observation_start, observation_end)
        formatted_data = fred_service.format_series_data(data)
        return {
            "indicator": "Unemployment Rate",
            "series_id": "UNRATE",
            "data": formatted_data,
            "source": "FRED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "indicator": "Unemployment Rate",
            "series_id": "UNRATE",
            "data": [],
            "source": "FRED (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/fred/cpi")
async def get_cpi(
    observation_start: str = None,
    observation_end: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get Consumer Price Index from FRED."""
    try:
        data = fred_service.get_cpi(observation_start, observation_end)
        formatted_data = fred_service.format_series_data(data)
        return {
            "indicator": "Consumer Price Index",
            "series_id": "CPIAUCSL",
            "data": formatted_data,
            "source": "FRED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "indicator": "Consumer Price Index",
            "series_id": "CPIAUCSL",
            "data": [],
            "source": "FRED (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/fred/10-year-treasury")
async def get_10_year_treasury_rate(
    observation_start: str = None,
    observation_end: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get 10-Year Treasury Rate from FRED."""
    try:
        data = fred_service.get_10_year_treasury_rate(observation_start, observation_end)
        formatted_data = fred_service.format_series_data(data)
        return {
            "indicator": "10-Year Treasury Rate",
            "series_id": "GS10",
            "data": formatted_data,
            "source": "FRED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "indicator": "10-Year Treasury Rate",
            "series_id": "GS10",
            "data": [],
            "source": "FRED (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/fred/2-year-treasury")
async def get_2_year_treasury_rate(
    observation_start: str = None,
    observation_end: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get 2-Year Treasury Rate from FRED."""
    try:
        data = fred_service.get_2_year_treasury_rate(observation_start, observation_end)
        formatted_data = fred_service.format_series_data(data)
        return {
            "indicator": "2-Year Treasury Rate",
            "series_id": "GS2",
            "data": formatted_data,
            "source": "FRED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "indicator": "2-Year Treasury Rate",
            "series_id": "GS2",
            "data": [],
            "source": "FRED (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/fred/30-year-treasury")
async def get_30_year_treasury_rate(
    observation_start: str = None,
    observation_end: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get 30-Year Treasury Rate from FRED."""
    try:
        data = fred_service.get_30_year_treasury_rate(observation_start, observation_end)
        formatted_data = fred_service.format_series_data(data)
        return {
            "indicator": "30-Year Treasury Rate",
            "series_id": "GS30",
            "data": formatted_data,
            "source": "FRED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "indicator": "30-Year Treasury Rate",
            "series_id": "GS30",
            "data": [],
            "source": "FRED (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/fred/industrial-production")
async def get_industrial_production(
    observation_start: str = None,
    observation_end: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get Industrial Production from FRED."""
    try:
        data = fred_service.get_industrial_production(observation_start, observation_end)
        formatted_data = fred_service.format_series_data(data)
        return {
            "indicator": "Industrial Production",
            "series_id": "INDPRO",
            "data": formatted_data,
            "source": "FRED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "indicator": "Industrial Production",
            "series_id": "INDPRO",
            "data": [],
            "source": "FRED (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/fred/retail-sales")
async def get_retail_sales(
    observation_start: str = None,
    observation_end: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get Retail Sales from FRED."""
    try:
        data = fred_service.get_retail_sales(observation_start, observation_end)
        formatted_data = fred_service.format_series_data(data)
        return {
            "indicator": "Retail Sales",
            "series_id": "RSAFS",
            "data": formatted_data,
            "source": "FRED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "indicator": "Retail Sales",
            "series_id": "RSAFS",
            "data": [],
            "source": "FRED (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/fred/housing-starts")
async def get_housing_starts(
    observation_start: str = None,
    observation_end: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get Housing Starts from FRED."""
    try:
        data = fred_service.get_housing_starts(observation_start, observation_end)
        formatted_data = fred_service.format_series_data(data)
        return {
            "indicator": "Housing Starts",
            "series_id": "HOUST",
            "data": formatted_data,
            "source": "FRED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "indicator": "Housing Starts",
            "series_id": "HOUST",
            "data": [],
            "source": "FRED (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/fred/oil-prices")
async def get_oil_prices(
    observation_start: str = None,
    observation_end: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get Oil Prices from FRED."""
    try:
        data = fred_service.get_oil_prices(observation_start, observation_end)
        formatted_data = fred_service.format_series_data(data)
        return {
            "indicator": "Crude Oil Prices",
            "series_id": "DCOILWTICO",
            "data": formatted_data,
            "source": "FRED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "indicator": "Crude Oil Prices",
            "series_id": "DCOILWTICO",
            "data": [],
            "source": "FRED (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Tiingo Endpoints
@router.get("/tiingo/stock/{ticker}")
async def get_tiingo_stock_data(
    ticker: str,
    start_date: str = None,
    end_date: str = None,
    resample_freq: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get stock data from Tiingo."""
    try:
        data = tiingo_service.get_stock_eod_prices(ticker, start_date, end_date, resample_freq)
        formatted_data = tiingo_service.format_eod_data(data)
        return {
            "ticker": ticker,
            "data": formatted_data,
            "source": "Tiingo",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "data": [],
            "source": "Tiingo (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/tiingo/stock-metadata/{ticker}")
async def get_tiingo_stock_metadata(
    ticker: str,
    current_user: str = Depends(get_current_user)
):
    """Get stock metadata from Tiingo."""
    try:
        data = tiingo_service.get_stock_metadata(ticker)
        return {
            "ticker": ticker,
            "metadata": data,
            "source": "Tiingo",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "metadata": {},
            "source": "Tiingo (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/tiingo/stock-news")
async def get_tiingo_stock_news(
    ticker: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 100,
    current_user: str = Depends(get_current_user)
):
    """Get stock news from Tiingo."""
    try:
        data = tiingo_service.get_stock_news(ticker, start_date, end_date, limit)
        return {
            "ticker": ticker,
            "news": data,
            "source": "Tiingo",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "news": [],
            "source": "Tiingo (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/tiingo/crypto/{ticker}")
async def get_tiingo_crypto_data(
    ticker: str,
    start_date: str = None,
    end_date: str = None,
    resample_freq: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get cryptocurrency data from Tiingo."""
    try:
        data = tiingo_service.get_crypto_prices(ticker, start_date, end_date, resample_freq)
        return {
            "ticker": ticker,
            "data": data,
            "source": "Tiingo",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "data": [],
            "source": "Tiingo (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/tiingo/crypto-metadata/{ticker}")
async def get_tiingo_crypto_metadata(
    ticker: str,
    current_user: str = Depends(get_current_user)
):
    """Get cryptocurrency metadata from Tiingo."""
    try:
        data = tiingo_service.get_crypto_metadata(ticker)
        return {
            "ticker": ticker,
            "metadata": data,
            "source": "Tiingo",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "metadata": {},
            "source": "Tiingo (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/tiingo/crypto-top/{ticker}")
async def get_tiingo_crypto_top_of_book(
    ticker: str,
    current_user: str = Depends(get_current_user)
):
    """Get cryptocurrency top of book from Tiingo."""
    try:
        data = tiingo_service.get_crypto_top_of_book(ticker)
        return {
            "ticker": ticker,
            "top_of_book": data,
            "source": "Tiingo",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "top_of_book": {},
            "source": "Tiingo (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/tiingo/forex/{base_currency}/{quote_currency}")
async def get_tiingo_forex_data(
    base_currency: str,
    quote_currency: str,
    start_date: str = None,
    end_date: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get forex data from Tiingo."""
    try:
        data = tiingo_service.get_forex_prices(base_currency, quote_currency, start_date, end_date)
        return {
            "base_currency": base_currency,
            "quote_currency": quote_currency,
            "data": data,
            "source": "Tiingo",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "base_currency": base_currency,
            "quote_currency": quote_currency,
            "data": [],
            "source": "Tiingo (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/tiingo/forex-top/{base_currency}/{quote_currency}")
async def get_tiingo_forex_top_of_book(
    base_currency: str,
    quote_currency: str,
    current_user: str = Depends(get_current_user)
):
    """Get forex top of book from Tiingo."""
    try:
        data = tiingo_service.get_forex_top_of_book(base_currency, quote_currency)
        return {
            "base_currency": base_currency,
            "quote_currency": quote_currency,
            "top_of_book": data,
            "source": "Tiingo",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "base_currency": base_currency,
            "quote_currency": quote_currency,
            "top_of_book": {},
            "source": "Tiingo (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# IEX Endpoints
@router.get("/tiingo/iex/{ticker}")
async def get_tiingo_iex_data(
    ticker: str,
    start_date: str = None,
    end_date: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get IEX data from Tiingo."""
    try:
        data = tiingo_service.get_iex_prices(ticker, start_date, end_date)
        return {
            "ticker": ticker,
            "data": data,
            "source": "Tiingo IEX",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "data": [],
            "source": "Tiingo IEX (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/tiingo/iex-metadata/{ticker}")
async def get_tiingo_iex_metadata(
    ticker: str,
    current_user: str = Depends(get_current_user)
):
    """Get IEX metadata from Tiingo."""
    try:
        data = tiingo_service.get_iex_metadata(ticker)
        return {
            "ticker": ticker,
            "metadata": data,
            "source": "Tiingo IEX",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "metadata": {},
            "source": "Tiingo IEX (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/tiingo/iex-top/{ticker}")
async def get_tiingo_iex_top_of_book(
    ticker: str,
    current_user: str = Depends(get_current_user)
):
    """Get IEX top of book from Tiingo."""
    try:
        data = tiingo_service.get_iex_top_of_book(ticker)
        return {
            "ticker": ticker,
            "top_of_book": data,
            "source": "Tiingo IEX",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "top_of_book": {},
            "source": "Tiingo IEX (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/tiingo/iex-company/{ticker}")
async def get_tiingo_iex_company_info(
    ticker: str,
    current_user: str = Depends(get_current_user)
):
    """Get IEX company information from Tiingo."""
    try:
        data = tiingo_service.get_iex_company_info(ticker)
        return {
            "ticker": ticker,
            "company_info": data,
            "source": "Tiingo IEX",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "company_info": {},
            "source": "Tiingo IEX (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/tiingo/iex-earnings/{ticker}")
async def get_tiingo_iex_earnings(
    ticker: str,
    current_user: str = Depends(get_current_user)
):
    """Get IEX earnings from Tiingo."""
    try:
        data = tiingo_service.get_iex_earnings(ticker)
        return {
            "ticker": ticker,
            "earnings": data,
            "source": "Tiingo IEX",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "earnings": [],
            "source": "Tiingo IEX (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/tiingo/iex-dividends/{ticker}")
async def get_tiingo_iex_dividends(
    ticker: str,
    current_user: str = Depends(get_current_user)
):
    """Get IEX dividends from Tiingo."""
    try:
        data = tiingo_service.get_iex_dividends(ticker)
        return {
            "ticker": ticker,
            "dividends": data,
            "source": "Tiingo IEX",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "dividends": [],
            "source": "Tiingo IEX (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/tiingo/iex-stats/{ticker}")
async def get_tiingo_iex_key_stats(
    ticker: str,
    current_user: str = Depends(get_current_user)
):
    """Get IEX key stats from Tiingo."""
    try:
        data = tiingo_service.get_iex_key_stats(ticker)
        return {
            "ticker": ticker,
            "key_stats": data,
            "source": "Tiingo IEX",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "key_stats": {},
            "source": "Tiingo IEX (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# EIA Endpoints
@router.get("/eia/crude-oil-prices")
async def get_eia_crude_oil_prices(
    start: str = None,
    end: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get crude oil prices (WTI and Brent) from EIA."""
    try:
        data = eia_service.get_crude_oil_prices(start, end)
        formatted_data = eia_service.format_energy_data(data)
        return {
            "indicator": "Crude Oil Prices",
            "data": formatted_data,
            "source": "EIA",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "indicator": "Crude Oil Prices",
            "data": [],
            "source": "EIA (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/eia/gasoline-prices")
async def get_eia_gasoline_prices(
    start: str = None,
    end: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get gasoline prices from EIA."""
    try:
        data = eia_service.get_gasoline_prices(start, end)
        formatted_data = eia_service.format_energy_data(data)
        return {
            "indicator": "Gasoline Prices",
            "data": formatted_data,
            "source": "EIA",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "indicator": "Gasoline Prices",
            "data": [],
            "source": "EIA (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/eia/natural-gas-prices")
async def get_eia_natural_gas_prices(
    start: str = None,
    end: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get natural gas prices from EIA."""
    try:
        data = eia_service.get_natural_gas_prices(start, end)
        formatted_data = eia_service.format_energy_data(data)
        return {
            "indicator": "Natural Gas Prices",
            "data": formatted_data,
            "source": "EIA",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "indicator": "Natural Gas Prices",
            "data": [],
            "source": "EIA (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/eia/crude-oil-production")
async def get_eia_crude_oil_production(
    start: str = None,
    end: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get crude oil production from EIA."""
    try:
        data = eia_service.get_crude_oil_production(start, end)
        formatted_data = eia_service.format_energy_data(data)
        return {
            "indicator": "Crude Oil Production",
            "data": formatted_data,
            "source": "EIA",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "indicator": "Crude Oil Production",
            "data": [],
            "source": "EIA (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/eia/emissions-co2")
async def get_eia_emissions_co2(
    start: str = None,
    end: str = None,
    current_user: str = Depends(get_current_user)
):
    """Get CO2 emissions from EIA."""
    try:
        data = eia_service.get_emissions_co2(start, end)
        formatted_data = eia_service.format_energy_data(data)
        return {
            "indicator": "CO2 Emissions",
            "data": formatted_data,
            "source": "EIA",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "indicator": "CO2 Emissions",
            "data": [],
            "source": "EIA (fallback)",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
