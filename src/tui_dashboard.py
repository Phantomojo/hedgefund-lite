#!/usr/bin/env python3
"""
Real-time Trading TUI Dashboard
Terminal User Interface for live trading monitoring and control
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, Any
import signal
import sys

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    from rich import box
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    from rich import box

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.trading_engine import trading_engine
from src.services.risk_manager import risk_manager

console = Console()

class TradingTUI:
    """Terminal User Interface for Trading System"""
    
    def __init__(self):
        self.console = Console()
        self.running = True
        self.refresh_rate = 2  # seconds
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        console.print("[bold green]🚀 HEDGEFUND Trading TUI Dashboard[/bold green]")
        console.print("[dim]Press Ctrl+C to exit[/dim]\n")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.running = False
        console.print("\n[bold yellow]Shutting down TUI Dashboard...[/bold yellow]")
        sys.exit(0)
    
    def create_header(self) -> Panel:
        """Create header panel with system info"""
        header_text = Text()
        header_text.append("🚀 HEDGEFUND ALGORITHMIC TRADING SYSTEM", style="bold blue")
        header_text.append("\n")
        header_text.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
        header_text.append(" | ")
        header_text.append("💰 Live Trading Dashboard", style="bold green")
        header_text.append(" | ")
        header_text.append("🛡️ Risk Management Active", style="bold red")
        
        return Panel(header_text, box=box.DOUBLE, style="blue")
    
    def create_account_summary(self, account_data: Dict[str, Any]) -> Panel:
        """Create account summary panel"""
        if not account_data.get("success"):
            return Panel("❌ Failed to load account data", style="red")
        
        balance = account_data.get("balance", 0)
        nav = account_data.get("nav", 0)
        unrealized_pnl = account_data.get("unrealized_pnl", 0)
        margin_used = account_data.get("margin_used", 0)
        margin_available = account_data.get("margin_available", 0)
        
        # Calculate P&L percentage
        pnl_pct = (unrealized_pnl / balance * 100) if balance > 0 else 0
        pnl_style = "green" if pnl_pct >= 0 else "red"
        
        summary_text = Text()
        summary_text.append("💰 ACCOUNT SUMMARY\n", style="bold white")
        summary_text.append(f"Balance: ${balance:,.2f}\n", style="white")
        summary_text.append(f"NAV: ${nav:,.2f}\n", style="white")
        summary_text.append(f"Unrealized P&L: ${unrealized_pnl:,.2f} ({pnl_pct:+.2f}%)", style=pnl_style)
        summary_text.append(f"\nMargin Used: ${margin_used:,.2f}\n", style="yellow")
        summary_text.append(f"Margin Available: ${margin_available:,.2f}", style="green")
        
        return Panel(summary_text, title="Account", box=box.ROUNDED, style="cyan")
    
    def create_positions_table(self, positions_data: Dict[str, Any]) -> Panel:
        """Create positions table"""
        if not positions_data.get("success"):
            return Panel("❌ Failed to load positions", style="red")
        
        positions = positions_data.get("positions", [])
        
        if not positions:
            return Panel("📊 No open positions", title="Positions", box=box.ROUNDED, style="blue")
        
        table = Table(title="Live Positions", box=box.ROUNDED)
        table.add_column("Pair", style="cyan", no_wrap=True)
        table.add_column("Side", style="magenta")
        table.add_column("Units", style="yellow", justify="right")
        table.add_column("Avg Price", style="blue", justify="right")
        table.add_column("Current P&L", style="green", justify="right")
        table.add_column("P&L %", style="green", justify="right")
        
        total_pnl = 0
        
        for pos in positions:
            pair = pos["instrument"]
            long_units = pos["long_units"]
            short_units = pos["short_units"]
            
            if long_units > 0:
                side = "LONG"
                units = long_units
                avg_price = float(pos["long_avg_price"])
                pnl = pos["long_pnl"]
                total_pnl += pnl
                
                # Calculate P&L percentage
                position_value = units * avg_price
                pnl_pct = (pnl / position_value * 100) if position_value > 0 else 0
                
                pnl_style = "green" if pnl >= 0 else "red"
                
                table.add_row(
                    pair,
                    f"[green]{side}[/green]",
                    f"{units:,}",
                    f"${avg_price:.5f}",
                    f"[{pnl_style}]${pnl:,.2f}[/{pnl_style}]",
                    f"[{pnl_style}]{pnl_pct:+.2f}%[/{pnl_style}]"
                )
            
            if short_units > 0:
                side = "SHORT"
                units = short_units
                avg_price = float(pos["short_avg_price"])
                pnl = pos["short_pnl"]
                total_pnl += pnl
                
                # Calculate P&L percentage
                position_value = units * avg_price
                pnl_pct = (pnl / position_value * 100) if position_value > 0 else 0
                
                pnl_style = "green" if pnl >= 0 else "red"
                
                table.add_row(
                    pair,
                    f"[red]{side}[/red]",
                    f"{units:,}",
                    f"${avg_price:.5f}",
                    f"[{pnl_style}]${pnl:,.2f}[/{pnl_style}]",
                    f"[{pnl_style}]{pnl_pct:+.2f}%[/{pnl_style}]"
                )
        
        # Add total row
        total_style = "green" if total_pnl >= 0 else "red"
        table.add_row(
            "[bold]TOTAL[/bold]",
            "",
            "",
            "",
            f"[bold {total_style}]${total_pnl:,.2f}[/bold {total_style}]",
            ""
        )
        
        return Panel(table, title="Positions", box=box.ROUNDED, style="blue")
    
    def create_risk_panel(self, risk_data: Dict[str, Any]) -> Panel:
        """Create risk management panel"""
        if not risk_data or "error" in risk_data:
            return Panel("❌ Failed to load risk data", style="red")
        
        risk_level = risk_data.get("risk_level", "UNKNOWN")
        alerts = risk_data.get("alerts", [])
        position_count = risk_data.get("position_count", 0)
        total_risk = risk_data.get("total_risk", 0)
        drawdown_pct = risk_data.get("drawdown_pct", 0)
        
        # Color code risk level
        risk_colors = {
            "LOW": "green",
            "MEDIUM": "yellow", 
            "ELEVATED": "orange",
            "HIGH": "red",
            "CRITICAL": "bold red"
        }
        risk_color = risk_colors.get(risk_level, "white")
        
        risk_text = Text()
        risk_text.append("🛡️ RISK MANAGEMENT\n", style="bold white")
        risk_text.append(f"Risk Level: [{risk_color}]{risk_level}[/{risk_color}]\n", style=risk_color)
        risk_text.append(f"Positions: {position_count}\n", style="white")
        risk_text.append(f"Total Risk: {total_risk:.2%}\n", style="yellow")
        risk_text.append(f"Drawdown: {drawdown_pct:.4%}\n", style="cyan")
        
        if alerts:
            risk_text.append(f"⚠️  {len(alerts)} Active Alerts", style="bold red")
        else:
            risk_text.append("✅ No Risk Alerts", style="bold green")
        
        return Panel(risk_text, title="Risk Management", box=box.ROUNDED, style="red")
    
    def create_market_data_panel(self) -> Panel:
        """Create market data panel"""
        try:
            # Get current EUR/USD price from OANDA
            import requests
            
            url = "https://api-fxpractice.oanda.com/v3/accounts/101-001-36248121-001/pricing"
            headers = {
                "Authorization": "Bearer 1725da5aa30805b09b7c7eb0094ffff4-d6b1be348877531faa9a3253cbda3cfd",
                "Content-Type": "application/json"
            }
            params = {"instruments": "EUR_USD"}
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                prices = data.get("prices", [])
                
                if prices:
                    price = prices[0]
                    bid = float(price.get("bids", [{}])[0].get("price", 0))
                    ask = float(price.get("asks", [{}])[0].get("price", 0))
                    spread = ask - bid
                    timestamp = price.get("time", "")
                    
                    market_text = Text()
                    market_text.append("📈 LIVE MARKET DATA\n", style="bold white")
                    market_text.append(f"EUR/USD\n", style="bold cyan")
                    market_text.append(f"Bid: ${bid:.5f}\n", style="green")
                    market_text.append(f"Ask: ${ask:.5f}\n", style="red")
                    market_text.append(f"Spread: {spread:.5f}\n", style="yellow")
                    market_text.append(f"Time: {timestamp[:19]}", style="dim")
                    
                    return Panel(market_text, title="Market Data", box=box.ROUNDED, style="green")
            
            # Fallback if API fails
            return Panel("📈 Market data unavailable", title="Market Data", box=box.ROUNDED, style="red")
            
        except Exception as e:
            return Panel(f"📈 Market data error: {str(e)}", title="Market Data", box=box.ROUNDED, style="red")
    
    def create_controls_panel(self) -> Panel:
        """Create trading controls panel"""
        controls_text = Text()
        controls_text.append("🎮 TRADING CONTROLS\n", style="bold white")
        controls_text.append("📊 Refresh: Auto (2s)\n", style="dim")
        controls_text.append("🚨 Emergency Stop: [bold red]PRESS 'E'[/bold red]\n", style="bold red")
        controls_text.append("📈 Quick Buy: [bold green]PRESS 'B'[/bold green]\n", style="bold green")
        controls_text.append("📉 Quick Sell: [bold red]PRESS 'S'[/bold red]\n", style="bold red")
        controls_text.append("🤖 AI Analysis: [bold blue]PRESS 'A'[/bold blue]\n", style="bold blue")
        controls_text.append("🎯 AI Strategy: [bold magenta]PRESS 'T'[/bold magenta]\n", style="bold magenta")
        controls_text.append("🔄 Monitor: Real-time\n", style="dim")
        controls_text.append("\n[dim]Press 'Q' to quit[/dim]", style="dim")
        
        return Panel(controls_text, title="Controls", box=box.ROUNDED, style="magenta")
    
    def create_layout(self) -> Layout:
        """Create the main layout"""
        layout = Layout()
        
        # Split into header and main content
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1)
        )
        
        # Split main content into left and right
        layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )
        
        # Split left side into account and positions
        layout["left"].split_column(
            Layout(name="account", ratio=1),
            Layout(name="positions", ratio=2)
        )
        
        # Split right side into market data, risk, and controls
        layout["right"].split_column(
            Layout(name="market", ratio=1),
            Layout(name="risk", ratio=2),
            Layout(name="controls", ratio=1)
        )
        
        return layout
    
    async def update_dashboard(self) -> Layout:
        """Update dashboard with live data"""
        try:
            # Get live data
            account_data = await trading_engine.get_account_summary()
            positions_data = await trading_engine.get_positions()
            risk_data = await risk_manager.get_risk_summary()
            
            # Create layout
            layout = self.create_layout()
            
            # Update sections
            layout["header"].update(self.create_header())
            layout["account"].update(self.create_account_summary(account_data))
            layout["positions"].update(self.create_positions_table(positions_data))
            layout["market"].update(self.create_market_data_panel())
            layout["risk"].update(self.create_risk_panel(risk_data))
            layout["controls"].update(self.create_controls_panel())
            
            return layout
            
        except Exception as e:
            error_panel = Panel(f"❌ Dashboard Error: {str(e)}", style="red")
            layout = Layout()
            layout.update(error_panel)
            return layout
    
    async def run_dashboard(self):
        """Run the live dashboard"""
        try:
            with Live(
                self.create_layout(),
                refresh_per_second=0.5,
                screen=True
            ) as live:
                while self.running:
                    # Update dashboard
                    updated_layout = await self.update_dashboard()
                    live.update(updated_layout)
                    
                    # Check for keyboard input (non-blocking)
                    try:
                        import msvcrt  # Windows
                        if msvcrt.kbhit():
                            key = msvcrt.getch().decode().upper()
                            await self.handle_keypress(key, live)
                    except ImportError:
                        try:
                            import sys
                            import tty
                            import termios
                            
                            # Non-blocking input for Unix/Linux
                            fd = sys.stdin.fileno()
                            old_settings = termios.tcgetattr(fd)
                            try:
                                tty.setraw(sys.stdin.fileno())
                                if sys.stdin.readable():
                                    key = sys.stdin.read(1).upper()
                                    await self.handle_keypress(key, live)
                            finally:
                                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                        except:
                            pass
                    
                    # Wait for refresh
                    await asyncio.sleep(self.refresh_rate)
                    
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Dashboard stopped by user[/bold yellow]")
        except Exception as e:
            console.print(f"\n[bold red]Dashboard error: {str(e)}[/bold red]")
    
    async def handle_keypress(self, key: str, live):
        """Handle keyboard input"""
        if key == 'E':
            console.print("\n[bold red]🚨 EMERGENCY STOP TRIGGERED![/bold red]")
            try:
                result = await risk_manager.emergency_stop()
                if result.get("success"):
                    console.print(f"[green]✅ {result.get('message')}[/green]")
                else:
                    console.print(f"[red]❌ Emergency stop failed: {result.get('error')}[/red]")
            except Exception as e:
                console.print(f"[red]❌ Emergency stop error: {str(e)}[/red]")
        
        elif key == 'B':
            console.print("\n[bold green]📈 QUICK BUY EUR/USD[/bold green]")
            try:
                result = await trading_engine.place_market_order(
                    pair="EUR_USD",
                    side="buy",
                    units=1000
                )
                if result.get("success"):
                    console.print(f"[green]✅ Buy order placed: {result.get('order_id')}[/green]")
                else:
                    console.print(f"[red]❌ Buy order failed: {result.get('error')}[/red]")
            except Exception as e:
                console.print(f"[red]❌ Buy order error: {str(e)}[/red]")
        
        elif key == 'S':
            console.print("\n[bold red]📉 QUICK SELL EUR/USD[/bold red]")
            try:
                result = await trading_engine.place_market_order(
                    pair="EUR_USD",
                    side="sell",
                    units=1000
                )
                if result.get("success"):
                    console.print(f"[green]✅ Sell order placed: {result.get('order_id')}[/green]")
                else:
                    console.print(f"[red]❌ Sell order failed: {result.get('error')}[/red]")
            except Exception as e:
                console.print(f"[red]❌ Sell order error: {str(e)}[/red]")
        
        elif key == 'A':
            console.print("\n[bold blue]🤖 AI MARKET ANALYSIS[/bold blue]")
            try:
                import requests
                response = requests.get("http://localhost:8000/api/v1/ai-trading/analysis-test", timeout=10)
                if response.status_code == 200:
                    analysis = response.json()
                    console.print(f"[green]✅ AI Analysis: {analysis.get('recommended_action', 'unknown')} with {analysis.get('confidence', 0):.1%} confidence[/green]")
                    console.print(f"[dim]Reasoning: {analysis.get('ai_analysis', {}).get('reasoning', 'No reasoning provided')}[/dim]")
                else:
                    console.print(f"[red]❌ AI Analysis failed: {response.status_code}[/red]")
            except Exception as e:
                console.print(f"[red]❌ AI Analysis error: {str(e)}[/red]")
        
        elif key == 'T':
            console.print("\n[bold magenta]🎯 AI STRATEGY EXECUTION[/bold magenta]")
            try:
                import requests
                response = requests.post("http://localhost:8000/api/v1/ai-trading/execute-strategy-test", 
                                      json={"execute_now": True}, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if "trades_executed" in result:
                        console.print(f"[green]✅ AI Strategy executed: {result.get('trades_executed', 0)} trades[/green]")
                    else:
                        console.print(f"[yellow]⚠️  AI Strategy: {result.get('message', 'No action taken')}[/yellow]")
                else:
                    console.print(f"[red]❌ AI Strategy failed: {response.status_code}[/red]")
            except Exception as e:
                console.print(f"[red]❌ AI Strategy error: {str(e)}[/red]")
        
        elif key == 'Q':
            console.print("\n[bold yellow]Quitting dashboard...[/bold yellow]")
            self.running = False


async def main():
    """Main function"""
    try:
        # Check if required services are available
        console.print("[dim]Checking services...[/dim]")
        
        # Test trading engine
        account_test = await trading_engine.get_account_summary()
        if not account_test.get("success"):
            console.print("[red]❌ Trading engine not available[/red]")
            return
        
        # Test risk manager
        risk_test = await risk_manager.get_risk_summary()
        if "error" in risk_test:
            console.print("[red]❌ Risk manager not available[/red]")
            return
        
        console.print("[green]✅ Services ready[/green]\n")
        
        # Start dashboard
        dashboard = TradingTUI()
        await dashboard.run_dashboard()
        
    except Exception as e:
        console.print(f"[bold red]Fatal error: {str(e)}[/bold red]")
        console.print("[dim]Make sure the server is running: uvicorn src.main:app --host 0.0.0.0 --port 8000[/dim]")


if __name__ == "__main__":
    asyncio.run(main())
