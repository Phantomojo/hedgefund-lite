"""
Real Trading Execution Engine
Handles live order placement, position management, and account operations with OANDA API
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
import json

logger = logging.getLogger(__name__)

class TradingEngine:
    """Real trading execution engine for OANDA"""
    
    def __init__(self):
        # OANDA API Configuration
        self.oanda_api_key = "1725da5aa30805b09b7c7eb0094ffff4-d6b1be348877531faa9a3253cbda3cfd"
        self.oanda_account_id = "101-001-36248121-001"
        self.oanda_base_url = "https://api-fxpractice.oanda.com"
        
        # Headers for OANDA API
        self.headers = {
            "Authorization": f"Bearer {self.oanda_api_key}",
            "Content-Type": "application/json"
        }
        
        # Internal state tracking
        self.active_orders = {}
        self.active_positions = {}
        
        logger.info("Trading Engine initialized with OANDA demo account")
    
    async def place_market_order(self, pair: str, side: str, units: int, 
                                stop_loss: Optional[float] = None,
                                take_profit: Optional[float] = None) -> Dict[str, Any]:
        """Place a real market order on OANDA"""
        try:
            logger.info(f"Placing {side} order for {units} units of {pair}")
            
            url = f"{self.oanda_base_url}/v3/accounts/{self.oanda_account_id}/orders"
            
            # Prepare order data
            order_data = {
                "order": {
                    "type": "MARKET",
                    "instrument": pair,
                    "units": str(units) if side.lower() == "buy" else str(-units),
                    "timeInForce": "FOK",  # Fill or Kill
                    "positionFill": "DEFAULT"
                }
            }
            
            # Add stop loss if provided
            if stop_loss:
                order_data["order"]["stopLossOnFill"] = {
                    "price": str(stop_loss),
                    "timeInForce": "GTC"  # Good Till Cancelled
                }
            
            # Add take profit if provided
            if take_profit:
                order_data["order"]["takeProfitOnFill"] = {
                    "price": str(take_profit),
                    "timeInForce": "GTC"
                }
            
            # Place order with OANDA
            response = requests.post(url, headers=self.headers, json=order_data, timeout=30)
            
            if response.status_code == 201:
                order_info = response.json()
                
                # Extract order details
                if "orderFillTransaction" in order_info:
                    fill_transaction = order_info["orderFillTransaction"]
                    order_id = fill_transaction["id"]
                    
                    # Store order information
                    self.active_orders[order_id] = {
                        "pair": pair,
                        "side": side,
                        "units": units,
                        "status": "filled",
                        "timestamp": datetime.now().isoformat(),
                        "price": fill_transaction.get("price"),
                        "transaction_id": order_id
                    }
                    
                    logger.info(f"Order {order_id} placed successfully at price {fill_transaction.get('price')}")
                    
                    return {
                        "success": True,
                        "order_id": order_id,
                        "status": "filled",
                        "price": fill_transaction.get("price"),
                        "units": units,
                        "pair": pair,
                        "side": side,
                        "timestamp": datetime.now().isoformat(),
                        "order_info": order_info
                    }
                else:
                    logger.error(f"Order creation response missing fill transaction: {order_info}")
                    return {
                        "success": False,
                        "error": "Order creation response invalid",
                        "response": order_info
                    }
            else:
                error_msg = f"Order placement failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error placing order: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Trading engine error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def get_positions(self) -> Dict[str, Any]:
        """Get current positions from OANDA"""
        try:
            url = f"{self.oanda_base_url}/v3/accounts/{self.oanda_account_id}/positions"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                positions_data = response.json()
                
                # Process positions to extract useful information
                processed_positions = []
                for position in positions_data.get("positions", []):
                    instrument = position["instrument"]
                    long_units = float(position["long"]["units"])
                    short_units = float(position["short"]["units"])
                    
                    if long_units != 0 or short_units != 0:
                        processed_positions.append({
                            "instrument": instrument,
                            "long_units": long_units,
                            "short_units": short_units,
                            "long_pnl": float(position["long"]["unrealizedPL"]),
                            "short_pnl": float(position["short"]["unrealizedPL"]),
                            "total_pnl": float(position["long"]["unrealizedPL"]) + float(position["short"]["unrealizedPL"]),
                            "long_avg_price": position["long"].get("averagePrice"),
                            "short_avg_price": position["short"].get("averagePrice")
                        })
                
                return {
                    "success": True,
                    "positions": processed_positions,
                    "total_positions": len(processed_positions),
                    "raw_data": positions_data
                }
            else:
                error_msg = f"Failed to get positions: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error getting positions: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def close_position(self, pair: str, units: Optional[int] = None, side: Optional[str] = None) -> Dict[str, Any]:
        """Close a position on OANDA"""
        try:
            logger.info(f"Closing position for {pair}, units: {units}, side: {side}")
            
            # First, get current position to see what we're working with
            positions = await self.get_positions()
            if not positions["success"]:
                return {"success": False, "error": "Failed to get positions"}
            
            # Find the specific position
            target_position = None
            for pos in positions["positions"]:
                if pos["instrument"] == pair:
                    target_position = pos
                    break
            
            if not target_position:
                return {"success": False, "error": f"No position found for {pair}"}
            
            # Build close request based on actual position
            close_data = {}
            
            if target_position["long_units"] > 0:
                if units and side == "long":
                    close_data["longUnits"] = str(min(units, target_position["long_units"]))
                else:
                    close_data["longUnits"] = str(target_position["long_units"])
            
            if target_position["short_units"] > 0:
                if units and side == "short":
                    close_data["shortUnits"] = str(min(units, target_position["short_units"]))
                else:
                    close_data["shortUnits"] = str(target_position["short_units"])
            
            if not close_data:
                return {"success": False, "error": f"No units to close for {pair}"}
            
            url = f"{self.oanda_base_url}/v3/accounts/{self.oanda_account_id}/positions/{pair}/close"
            
            response = requests.put(url, headers=self.headers, json=close_data, timeout=30)
            
            if response.status_code == 200:
                close_info = response.json()
                logger.info(f"Position closed for {pair}: {close_info}")
                
                return {
                    "success": True,
                    "message": f"Position closed for {pair}",
                    "close_info": close_info,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error_msg = f"Failed to close position: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error closing position: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def get_account_summary(self) -> Dict[str, Any]:
        """Get account summary from OANDA"""
        try:
            url = f"{self.oanda_base_url}/v3/accounts/{self.oanda_account_id}"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                account_data = response.json()
                account = account_data.get("account", {})
                
                return {
                    "success": True,
                    "account_id": account.get("id"),
                    "currency": account.get("currency"),
                    "balance": float(account.get("balance", 0)),
                    "nav": float(account.get("NAV", 0)),  # Net Asset Value
                    "unrealized_pnl": float(account.get("unrealizedPL", 0)),
                    "realized_pnl": float(account.get("pl", 0)),
                    "margin_used": float(account.get("marginUsed", 0)),
                    "margin_available": float(account.get("marginAvailable", 0)),
                    "position_value": float(account.get("positionValue", 0)),
                    "open_trade_count": int(account.get("openTradeCount", 0)),
                    "open_position_count": int(account.get("openPositionCount", 0)),
                    "last_transaction_id": account.get("lastTransactionID"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error_msg = f"Failed to get account summary: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error getting account summary: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def get_orders(self) -> Dict[str, Any]:
        """Get pending orders from OANDA"""
        try:
            url = f"{self.oanda_base_url}/v3/accounts/{self.oanda_account_id}/orders"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                orders_data = response.json()
                orders = orders_data.get("orders", [])
                
                processed_orders = []
                for order in orders:
                    processed_orders.append({
                        "id": order.get("id"),
                        "type": order.get("type"),
                        "instrument": order.get("instrument"),
                        "units": order.get("units"),
                        "price": order.get("price"),
                        "time_in_force": order.get("timeInForce"),
                        "create_time": order.get("createTime"),
                        "state": order.get("state")
                    })
                
                return {
                    "success": True,
                    "orders": processed_orders,
                    "total_orders": len(processed_orders)
                }
            else:
                error_msg = f"Failed to get orders: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error getting orders: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel a pending order"""
        try:
            url = f"{self.oanda_base_url}/v3/accounts/{self.oanda_account_id}/orders/{order_id}/cancel"
            
            response = requests.put(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                cancel_info = response.json()
                logger.info(f"Order {order_id} cancelled successfully")
                
                return {
                    "success": True,
                    "message": f"Order {order_id} cancelled",
                    "cancel_info": cancel_info
                }
            else:
                error_msg = f"Failed to cancel order: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error cancelling order: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def emergency_stop(self) -> Dict[str, Any]:
        """Emergency stop - close all positions immediately"""
        try:
            logger.warning("EMERGENCY STOP INITIATED - Closing all positions")
            
            # Get current positions
            positions_result = await self.get_positions()
            
            if not positions_result["success"]:
                return {
                    "success": False,
                    "error": "Failed to get positions for emergency stop"
                }
            
            closed_positions = []
            errors = []
            
            for position in positions_result["positions"]:
                pair = position["instrument"]
                
                try:
                    result = await self.close_position(pair)
                    if result["success"]:
                        closed_positions.append(pair)
                        logger.info(f"Emergency stop: Closed position {pair}")
                    else:
                        errors.append(f"Failed to close {pair}: {result.get('error')}")
                        logger.error(f"Emergency stop failed for {pair}: {result.get('error')}")
                except Exception as e:
                    errors.append(f"Error closing {pair}: {str(e)}")
                    logger.error(f"Emergency stop error for {pair}: {str(e)}")
            
            return {
                "success": True,
                "message": f"Emergency stop executed. Closed {len(closed_positions)} positions.",
                "closed_positions": closed_positions,
                "errors": errors,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Emergency stop error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }


# Global trading engine instance
trading_engine = TradingEngine()
