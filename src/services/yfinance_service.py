"""
YFinance service for additional market data.
Provides access to stocks, ETFs, mutual funds, and other financial instruments.
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

class YFinanceService:
    """YFinance service for market data."""
    
    def __init__(self):
        self.enabled = True
    
    def get_stock_data(self, symbol: str, period: str = "1mo", interval: str = "1d") -> Dict[str, Any]:
        """Get stock data using yfinance."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                return {"error": "No data available", "symbol": symbol}
            
            # Convert to list of dictionaries
            data_list = []
            for index, row in data.iterrows():
                data_list.append({
                    "timestamp": index.isoformat(),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                    "dividends": float(row.get("Dividends", 0)),
                    "stock_splits": float(row.get("Stock Splits", 0))
                })
            
            return {
                "symbol": symbol,
                "data": data_list,
                "info": ticker.info,
                "source": "YFinance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"YFinance error for {symbol}: {e}")
            return {
                "symbol": symbol,
                "data": [],
                "error": str(e),
                "source": "YFinance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_etf_data(self, symbol: str, period: str = "1mo", interval: str = "1d") -> Dict[str, Any]:
        """Get ETF data using yfinance."""
        return self.get_stock_data(symbol, period, interval)
    
    def get_crypto_data(self, symbol: str, period: str = "1mo", interval: str = "1d") -> Dict[str, Any]:
        """Get crypto data using yfinance."""
        # Add USD suffix for crypto pairs
        if not symbol.endswith("-USD"):
            symbol = f"{symbol}-USD"
        return self.get_stock_data(symbol, period, interval)
    
    def get_forex_data(self, from_currency: str, to_currency: str, 
                      period: str = "1mo", interval: str = "1d") -> Dict[str, Any]:
        """Get forex data using yfinance."""
        symbol = f"{from_currency}{to_currency}=X"
        return self.get_stock_data(symbol, period, interval)
    
    def get_ticker_info(self, symbol: str) -> Dict[str, Any]:
        """Get detailed ticker information."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "symbol": symbol,
                "info": info,
                "source": "YFinance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"YFinance info error for {symbol}: {e}")
            return {
                "symbol": symbol,
                "info": {},
                "error": str(e),
                "source": "YFinance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_earnings(self, symbol: str) -> Dict[str, Any]:
        """Get earnings data."""
        try:
            ticker = yf.Ticker(symbol)
            earnings = ticker.earnings
            calendar = ticker.calendar
            
            return {
                "symbol": symbol,
                "earnings": earnings.to_dict('records') if not earnings.empty else [],
                "calendar": calendar.to_dict('records') if not calendar.empty else [],
                "source": "YFinance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"YFinance earnings error for {symbol}: {e}")
            return {
                "symbol": symbol,
                "earnings": [],
                "calendar": [],
                "error": str(e),
                "source": "YFinance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_balance_sheet(self, symbol: str) -> Dict[str, Any]:
        """Get balance sheet data."""
        try:
            ticker = yf.Ticker(symbol)
            balance_sheet = ticker.balance_sheet
            
            return {
                "symbol": symbol,
                "balance_sheet": balance_sheet.to_dict('records') if not balance_sheet.empty else [],
                "source": "YFinance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"YFinance balance sheet error for {symbol}: {e}")
            return {
                "symbol": symbol,
                "balance_sheet": [],
                "error": str(e),
                "source": "YFinance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_income_statement(self, symbol: str) -> Dict[str, Any]:
        """Get income statement data."""
        try:
            ticker = yf.Ticker(symbol)
            income_stmt = ticker.income_stmt
            
            return {
                "symbol": symbol,
                "income_statement": income_stmt.to_dict('records') if not income_stmt.empty else [],
                "source": "YFinance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"YFinance income statement error for {symbol}: {e}")
            return {
                "symbol": symbol,
                "income_statement": [],
                "error": str(e),
                "source": "YFinance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_cash_flow(self, symbol: str) -> Dict[str, Any]:
        """Get cash flow data."""
        try:
            ticker = yf.Ticker(symbol)
            cash_flow = ticker.cashflow
            
            return {
                "symbol": symbol,
                "cash_flow": cash_flow.to_dict('records') if not cash_flow.empty else [],
                "source": "YFinance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"YFinance cash flow error for {symbol}: {e}")
            return {
                "symbol": symbol,
                "cash_flow": [],
                "error": str(e),
                "source": "YFinance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_recommendations(self, symbol: str) -> Dict[str, Any]:
        """Get analyst recommendations."""
        try:
            ticker = yf.Ticker(symbol)
            recommendations = ticker.recommendations
            
            return {
                "symbol": symbol,
                "recommendations": recommendations.to_dict('records') if not recommendations.empty else [],
                "source": "YFinance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"YFinance recommendations error for {symbol}: {e}")
            return {
                "symbol": symbol,
                "recommendations": [],
                "error": str(e),
                "source": "YFinance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def search_tickers(self, query: str) -> Dict[str, Any]:
        """Search for tickers."""
        try:
            # YFinance doesn't have a direct search, but we can try common patterns
            suggestions = []
            
            # Try common stock exchanges
            exchanges = ["", ".TO", ".V", ".AX", ".L", ".PA", ".F", ".MI", ".AS"]
            for exchange in exchanges:
                try:
                    ticker = yf.Ticker(f"{query}{exchange}")
                    info = ticker.info
                    if info and info.get("regularMarketPrice"):
                        suggestions.append({
                            "symbol": f"{query}{exchange}",
                            "name": info.get("longName", info.get("shortName", query)),
                            "exchange": info.get("exchange", "Unknown"),
                            "type": info.get("quoteType", "Unknown")
                        })
                except:
                    continue
            
            return {
                "query": query,
                "suggestions": suggestions,
                "source": "YFinance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"YFinance search error for {query}: {e}")
            return {
                "query": query,
                "suggestions": [],
                "error": str(e),
                "source": "YFinance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

# Global instance
yfinance_service = YFinanceService()
