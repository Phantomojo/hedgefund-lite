#!/usr/bin/env python3
"""
OANDA API Client
Comprehensive client implementing all OANDA API endpoints with proper error handling.
Based on OANDA REST API v20 documentation.
"""

import requests
import json
import time
import asyncio
import websockets
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import structlog

logger = structlog.get_logger()

class OANDAClient:
    """Comprehensive OANDA API client."""
    
    def __init__(self, api_key: str, account_id: str, practice: bool = True):
        self.api_key = api_key
        self.account_id = account_id
        self.practice = practice
        
        # API URLs based on environment
        if practice:
            self.base_url = "https://api-fxpractice.oanda.com"
            self.stream_url = "wss://stream-fxpractice.oanda.com"
        else:
            self.base_url = "https://api-fxtrade.oanda.com"
            self.stream_url = "wss://stream-fxtrade.oanda.com"
        
        # Headers
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Rate limiting
        self.request_count = 0
        self.last_request_time = time.time()
        self.max_requests_per_second = 120
        
        logger.info("OANDA client initialized", 
                   practice=practice, 
                   account_id=account_id)

    def _rate_limit(self):
        """Implement rate limiting (120 requests/second)."""
        current_time = time.time()
        if current_time - self.last_request_time < 1.0:
            self.request_count += 1
            if self.request_count >= self.max_requests_per_second:
                sleep_time = 1.0 - (current_time - self.last_request_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                self.request_count = 0
                self.last_request_time = time.time()
        else:
            self.request_count = 1
            self.last_request_time = current_time

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request with proper error handling."""
        self._rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Handle different response codes
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 201:
                return response.json()
            elif response.status_code == 204:
                return {"status": "success"}
            elif response.status_code == 400:
                logger.error("Bad request", status_code=400, response=response.text)
                return None
            elif response.status_code == 401:
                logger.error("Unauthorized - check API key", status_code=401)
                return None
            elif response.status_code == 403:
                logger.error("Forbidden - check account permissions", status_code=403)
                return None
            elif response.status_code == 404:
                logger.error("Not found", status_code=404, endpoint=endpoint)
                return None
            elif response.status_code == 429:
                logger.warning("Rate limit exceeded, waiting...", status_code=429)
                time.sleep(1)
                return self._make_request(method, endpoint, data)  # Retry
            else:
                logger.error("Unexpected response", 
                           status_code=response.status_code, 
                           response=response.text)
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error("Request failed", error=str(e), endpoint=endpoint)
            return None

    # Account Management
    def get_account(self) -> Optional[Dict]:
        """Get account information."""
        endpoint = f"/v3/accounts/{self.account_id}"
        return self._make_request("GET", endpoint)

    def get_accounts(self) -> Optional[Dict]:
        """Get all accounts."""
        endpoint = "/v3/accounts"
        return self._make_request("GET", endpoint)

    # Instrument Management
    def get_instruments(self, account_id: Optional[str] = None) -> Optional[Dict]:
        """Get available instruments."""
        acc_id = account_id or self.account_id
        endpoint = f"/v3/accounts/{acc_id}/instruments"
        return self._make_request("GET", endpoint)

    def get_candles(self, instrument: str, params: Dict) -> Optional[Dict]:
        """Get candlestick data."""
        endpoint = f"/v3/instruments/{instrument}/candles"
        # Convert params to query string
        query_params = "&".join([f"{k}={v}" for k, v in params.items()])
        if query_params:
            endpoint += f"?{query_params}"
        return self._make_request("GET", endpoint)

    # Order Management
    def create_order(self, order_data: Dict) -> Optional[Dict]:
        """Create a new order."""
        endpoint = f"/v3/accounts/{self.account_id}/orders"
        return self._make_request("POST", endpoint, order_data)

    def get_orders(self, params: Optional[Dict] = None) -> Optional[Dict]:
        """Get orders."""
        endpoint = f"/v3/accounts/{self.account_id}/orders"
        if params:
            query_params = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint += f"?{query_params}"
        return self._make_request("GET", endpoint)

    def get_order(self, order_id: str) -> Optional[Dict]:
        """Get specific order."""
        endpoint = f"/v3/accounts/{self.account_id}/orders/{order_id}"
        return self._make_request("GET", endpoint)

    def cancel_order(self, order_id: str) -> Optional[Dict]:
        """Cancel an order."""
        endpoint = f"/v3/accounts/{self.account_id}/orders/{order_id}/cancel"
        return self._make_request("PUT", endpoint)

    def update_order(self, order_id: str, order_data: Dict) -> Optional[Dict]:
        """Update an order."""
        endpoint = f"/v3/accounts/{self.account_id}/orders/{order_id}"
        return self._make_request("PUT", endpoint, order_data)

    # Trade Management
    def get_trades(self, params: Optional[Dict] = None) -> Optional[Dict]:
        """Get trades."""
        endpoint = f"/v3/accounts/{self.account_id}/trades"
        if params:
            query_params = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint += f"?{query_params}"
        return self._make_request("GET", endpoint)

    def get_trade(self, trade_id: str) -> Optional[Dict]:
        """Get specific trade."""
        endpoint = f"/v3/accounts/{self.account_id}/trades/{trade_id}"
        return self._make_request("GET", endpoint)

    def close_trade(self, trade_id: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Close a trade."""
        endpoint = f"/v3/accounts/{self.account_id}/trades/{trade_id}/close"
        return self._make_request("PUT", endpoint, data)

    def update_trade(self, trade_id: str, data: Dict) -> Optional[Dict]:
        """Update trade stop loss or take profit."""
        endpoint = f"/v3/accounts/{self.account_id}/trades/{trade_id}"
        return self._make_request("PUT", endpoint, data)

    # Position Management
    def get_positions(self) -> Optional[Dict]:
        """Get all positions."""
        endpoint = f"/v3/accounts/{self.account_id}/positions"
        return self._make_request("GET", endpoint)

    def get_position(self, instrument: str) -> Optional[Dict]:
        """Get specific position."""
        endpoint = f"/v3/accounts/{self.account_id}/positions/{instrument}"
        return self._make_request("GET", endpoint)

    def close_position(self, instrument: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Close a position."""
        endpoint = f"/v3/accounts/{self.account_id}/positions/{instrument}/close"
        return self._make_request("PUT", endpoint, data)

    # Pricing
    def get_pricing(self, instruments: List[str], params: Optional[Dict] = None) -> Optional[Dict]:
        """Get pricing information."""
        endpoint = f"/v3/accounts/{self.account_id}/pricing"
        if params:
            query_params = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint += f"?{query_params}"
        
        # Add instruments as query parameter
        instruments_str = ",".join(instruments)
        if "?" in endpoint:
            endpoint += f"&instruments={instruments_str}"
        else:
            endpoint += f"?instruments={instruments_str}"
        
        return self._make_request("GET", endpoint)

    # Transaction Management
    def get_transactions(self, params: Optional[Dict] = None) -> Optional[Dict]:
        """Get transactions."""
        endpoint = f"/v3/accounts/{self.account_id}/transactions"
        if params:
            query_params = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint += f"?{query_params}"
        return self._make_request("GET", endpoint)

    def get_transaction(self, transaction_id: str) -> Optional[Dict]:
        """Get specific transaction."""
        endpoint = f"/v3/accounts/{self.account_id}/transactions/{transaction_id}"
        return self._make_request("GET", endpoint)

    # Convenience Methods for Trading
    def place_market_order(self, instrument: str, units: int, side: str = "buy", 
                          stop_loss: Optional[float] = None, 
                          take_profit: Optional[float] = None) -> Optional[Dict]:
        """Place a market order."""
        order_data = {
            "order": {
                "type": "MARKET",
                "instrument": instrument,
                "units": str(units) if side == "buy" else str(-units),
                "timeInForce": "FOK",
                "positionFill": "DEFAULT"
            }
        }
        
        if stop_loss:
            order_data["order"]["stopLossOnFill"] = {
                "price": str(stop_loss),
                "timeInForce": "GTC"
            }
        
        if take_profit:
            order_data["order"]["takeProfitOnFill"] = {
                "price": str(take_profit),
                "timeInForce": "GTC"
            }
        
        return self.create_order(order_data)

    def place_limit_order(self, instrument: str, units: int, price: float, 
                         side: str = "buy", expiry: Optional[str] = None) -> Optional[Dict]:
        """Place a limit order."""
        order_data = {
            "order": {
                "type": "LIMIT",
                "instrument": instrument,
                "units": str(units) if side == "buy" else str(-units),
                "price": str(price),
                "timeInForce": "GTC"
            }
        }
        
        if expiry:
            order_data["order"]["gtdTime"] = expiry
        
        return self.create_order(order_data)

    def place_stop_order(self, instrument: str, units: int, price: float, 
                        side: str = "buy", expiry: Optional[str] = None) -> Optional[Dict]:
        """Place a stop order."""
        order_data = {
            "order": {
                "type": "STOP",
                "instrument": instrument,
                "units": str(units) if side == "buy" else str(-units),
                "price": str(price),
                "timeInForce": "GTC"
            }
        }
        
        if expiry:
            order_data["order"]["gtdTime"] = expiry
        
        return self.create_order(order_data)

    def place_trailing_stop_order(self, instrument: str, units: int, distance: float,
                                 side: str = "buy", expiry: Optional[str] = None) -> Optional[Dict]:
        """Place a trailing stop order."""
        order_data = {
            "order": {
                "type": "TRAILING_STOP",
                "instrument": instrument,
                "units": str(units) if side == "buy" else str(-units),
                "trailingStopValueInDistance": str(distance),
                "timeInForce": "GTC"
            }
        }
        
        if expiry:
            order_data["order"]["gtdTime"] = expiry
        
        return self.create_order(order_data)

    def place_guaranteed_stop_loss_order(self, instrument: str, units: int, price: float,
                                       side: str = "buy", expiry: Optional[str] = None) -> Optional[Dict]:
        """Place a guaranteed stop loss order."""
        order_data = {
            "order": {
                "type": "GUARANTEED_STOP_LOSS",
                "instrument": instrument,
                "units": str(units) if side == "buy" else str(-units),
                "price": str(price),
                "timeInForce": "GTC"
            }
        }
        
        if expiry:
            order_data["order"]["gtdTime"] = expiry
        
        return self.create_order(order_data)

    def place_market_if_touched_order(self, instrument: str, units: int, price: float,
                                     side: str = "buy", expiry: Optional[str] = None) -> Optional[Dict]:
        """Place a market if touched order."""
        order_data = {
            "order": {
                "type": "MARKET_IF_TOUCHED",
                "instrument": instrument,
                "units": str(units) if side == "buy" else str(-units),
                "price": str(price),
                "timeInForce": "GTC"
            }
        }
        
        if expiry:
            order_data["order"]["gtdTime"] = expiry
        
        return self.create_order(order_data)

    # Streaming API (WebSocket)
    async def stream_pricing(self, instruments: List[str], callback):
        """Stream real-time pricing data."""
        uri = f"{self.stream_url}/v3/accounts/{self.account_id}/pricing/stream"
        
        # Add instruments as query parameter
        instruments_str = ",".join(instruments)
        uri += f"?instruments={instruments_str}"
        
        try:
            async with websockets.connect(uri, extra_headers={"Authorization": f"Bearer {self.api_key}"}) as websocket:
                logger.info("Connected to OANDA pricing stream", instruments=instruments)
                
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        if "type" in data and data["type"] == "PRICE":
                            await callback(data)
                        elif "type" in data and data["type"] == "HEARTBEAT":
                            # Send heartbeat response
                            await websocket.send(json.dumps({"type": "HEARTBEAT"}))
                            
                    except websockets.exceptions.ConnectionClosed:
                        logger.warning("WebSocket connection closed, reconnecting...")
                        break
                    except Exception as e:
                        logger.error("Error in pricing stream", error=str(e))
                        break
                        
        except Exception as e:
            logger.error("Failed to connect to pricing stream", error=str(e))

    async def stream_transactions(self, callback):
        """Stream real-time transaction data."""
        uri = f"{self.stream_url}/v3/accounts/{self.account_id}/transactions/stream"
        
        try:
            async with websockets.connect(uri, extra_headers={"Authorization": f"Bearer {self.api_key}"}) as websocket:
                logger.info("Connected to OANDA transaction stream")
                
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        if "type" in data and data["type"] == "TRANSACTION":
                            await callback(data)
                        elif "type" in data and data["type"] == "HEARTBEAT":
                            await websocket.send(json.dumps({"type": "HEARTBEAT"}))
                            
                    except websockets.exceptions.ConnectionClosed:
                        logger.warning("Transaction stream connection closed, reconnecting...")
                        break
                    except Exception as e:
                        logger.error("Error in transaction stream", error=str(e))
                        break
                        
        except Exception as e:
            logger.error("Failed to connect to transaction stream", error=str(e))

    # Advanced Risk Management
    def get_margin_requirements(self, instrument: str, units: int) -> Optional[Dict]:
        """Get margin requirements for a position."""
        try:
            # Calculate approximate margin requirement
            # This is a simplified calculation - OANDA provides actual margin requirements
            # For demo account, we'll use conservative estimates
            
            # Typical margin requirements for major pairs
            margin_rates = {
                "EUR_USD": 0.02,  # 2% margin
                "GBP_USD": 0.05,  # 5% margin
                "USD_JPY": 0.02,  # 2% margin
                "USD_CHF": 0.05,  # 5% margin
                "AUD_USD": 0.02,  # 2% margin
                "USD_CAD": 0.02,  # 2% margin
            }
            
            margin_rate = margin_rates.get(instrument, 0.05)  # Default 5%
            
            # Get current price
            pricing = self.get_pricing([instrument])
            if pricing and pricing.get('prices'):
                current_price = float(pricing['prices'][0]['bids'][0]['price'])
                
                # Calculate margin requirement
                position_value = abs(units) * current_price
                margin_required = position_value * margin_rate
                
                return {
                    "instrument": instrument,
                    "units": units,
                    "current_price": current_price,
                    "position_value": position_value,
                    "margin_rate": margin_rate,
                    "margin_required": margin_required,
                    "leverage": 1 / margin_rate
                }
            
            return None
            
        except Exception as e:
            logger.error("Error calculating margin requirements", error=str(e))
            return None

    def check_margin_availability(self, new_margin_required: float) -> bool:
        """Check if we have enough margin for a new position."""
        try:
            account = self.get_account_summary()
            if account:
                available_margin = float(account.get('margin_available', 0))
                return available_margin >= new_margin_required
            return False
        except Exception as e:
            logger.error("Error checking margin availability", error=str(e))
            return False

    # Performance Analytics
    def get_performance_metrics(self, days: int = 30) -> Optional[Dict]:
        """Get comprehensive performance metrics."""
        try:
            # Get transactions for the specified period
            from_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            transactions = self.get_transactions({
                "from": from_date,
                "type": "TRADE"
            })
            
            if not transactions or not transactions.get('transactions'):
                return None
            
            trades = transactions['transactions']
            
            # Calculate metrics
            total_trades = len(trades)
            winning_trades = 0
            losing_trades = 0
            total_pnl = 0.0
            max_profit = 0.0
            max_loss = 0.0
            
            for trade in trades:
                pnl = float(trade.get('pl', 0))
                total_pnl += pnl
                
                if pnl > 0:
                    winning_trades += 1
                    max_profit = max(max_profit, pnl)
                elif pnl < 0:
                    losing_trades += 1
                    max_loss = min(max_loss, pnl)
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            avg_win = max_profit / winning_trades if winning_trades > 0 else 0
            avg_loss = max_loss / losing_trades if losing_trades > 0 else 0
            profit_factor = abs(avg_win * winning_trades / (avg_loss * losing_trades)) if losing_trades > 0 else float('inf')
            
            return {
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": win_rate,
                "total_pnl": total_pnl,
                "avg_win": avg_win,
                "avg_loss": avg_loss,
                "profit_factor": profit_factor,
                "max_profit": max_profit,
                "max_loss": max_loss,
                "period_days": days
            }
            
        except Exception as e:
            logger.error("Error calculating performance metrics", error=str(e))
            return None

    # Correlation Analysis
    def calculate_correlation_matrix(self, instruments: List[str], days: int = 30) -> Optional[Dict]:
        """Calculate correlation matrix between instruments."""
        try:
            import numpy as np
            import pandas as pd
            
            # Get historical data for all instruments
            from_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            price_data = {}
            for instrument in instruments:
                candles = self.get_candles(instrument, {
                    "from": from_date,
                    "granularity": "D"
                })
                
                if candles and candles.get('candles'):
                    prices = [float(candle['mid']['c']) for candle in candles['candles']]
                    price_data[instrument] = prices
            
            if not price_data:
                return None
            
            # Create DataFrame and calculate correlations
            df = pd.DataFrame(price_data)
            correlation_matrix = df.corr()
            
            return {
                "correlation_matrix": correlation_matrix.to_dict(),
                "instruments": instruments,
                "period_days": days
            }
            
        except Exception as e:
            logger.error("Error calculating correlation matrix", error=str(e))
            return None

    # Utility Methods
    def get_account_summary(self) -> Optional[Dict]:
        """Get account summary with key metrics."""
        account = self.get_account()
        if not account:
            return None
        
        account_data = account.get("account", {})
        
        return {
            "id": account_data.get("id"),
            "name": account_data.get("name"),
            "currency": account_data.get("currency"),
            "balance": account_data.get("balance"),
            "pl": account_data.get("pl"),
            "unrealized_pl": account_data.get("unrealizedPL"),
            "nav": account_data.get("NAV"),
            "margin_used": account_data.get("marginUsed"),
            "margin_available": account_data.get("marginAvailable"),
            "open_trade_count": account_data.get("openTradeCount"),
            "open_position_count": account_data.get("openPositionCount"),
            "pending_order_count": account_data.get("pendingOrderCount"),
            "margin_rate": account_data.get("marginRate"),
            "margin_call_margin_used": account_data.get("marginCallMarginUsed"),
            "margin_call_percent": account_data.get("marginCallPercent"),
            "withdrawal_limit": account_data.get("withdrawalLimit"),
            "margin_call_extension_count": account_data.get("marginCallExtensionCount"),
            "open_trade_count": account_data.get("openTradeCount"),
            "open_position_count": account_data.get("openPositionCount"),
            "pending_order_count": account_data.get("pendingOrderCount"),
            "financing": account_data.get("financing"),
            "commission": account_data.get("commission"),
            "guaranteed_stop_loss_order_mode": account_data.get("guaranteedStopLossOrderMode"),
            "guaranteed_stop_loss_order_margin_used": account_data.get("guaranteedStopLossOrderMarginUsed"),
            "resettable_pl": account_data.get("resettablePL"),
            "financing_day_of_week": account_data.get("financingDayOfWeek"),
            "margin_call_margin_used": account_data.get("marginCallMarginUsed"),
            "margin_call_percent": account_data.get("marginCallPercent"),
            "withdrawal_limit": account_data.get("withdrawalLimit"),
            "margin_call_extension_count": account_data.get("marginCallExtensionCount"),
            "open_trade_count": account_data.get("openTradeCount"),
            "open_position_count": account_data.get("openPositionCount"),
            "pending_order_count": account_data.get("pendingOrderCount"),
            "financing": account_data.get("financing"),
            "commission": account_data.get("commission"),
            "guaranteed_stop_loss_order_mode": account_data.get("guaranteedStopLossOrderMode"),
            "guaranteed_stop_loss_order_margin_used": account_data.get("guaranteedStopLossOrderMarginUsed"),
            "resettable_pl": account_data.get("resettablePL"),
            "financing_day_of_week": account_data.get("financingDayOfWeek"),
            "timestamp": account_data.get("timestamp")
        }

    def get_trading_summary(self) -> Optional[Dict]:
        """Get comprehensive trading summary."""
        # Get account info
        account = self.get_account_summary()
        if not account:
            return None
        
        # Get open positions
        positions = self.get_positions()
        
        # Get open trades
        trades = self.get_trades({"state": "OPEN"})
        
        # Get pending orders
        orders = self.get_orders({"state": "PENDING"})
        
        return {
            "account": account,
            "positions": positions.get("positions", []) if positions else [],
            "trades": trades.get("trades", []) if trades else [],
            "orders": orders.get("orders", []) if orders else [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
