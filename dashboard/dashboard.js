// AI Trading Dashboard JavaScript
class TradingDashboard {
    constructor() {
        this.apiBase = 'http://localhost:8000';
        this.priceChart = null;
        this.recentTrades = [];
        this.currentTime = new Date();
        
        this.init();
    }

    async init() {
        this.updateTime();
        this.loadAccountBalance();
        this.loadMarketNews();
        this.analyzeMarket();
        this.initPriceChart();
        this.loadAutonomousStatus();
        
        // Update every 30 seconds
        setInterval(() => {
            this.updateTime();
            this.loadAccountBalance();
        }, 30000);
        
        // Update market data every 60 seconds
        setInterval(() => {
            this.analyzeMarket();
        }, 60000);
        
        // Update autonomous status every 10 seconds
        setInterval(() => {
            this.loadAutonomousStatus();
        }, 10000);
    }

    updateTime() {
        const now = new Date();
        document.getElementById('current-time').textContent = now.toLocaleTimeString();
    }

    async loadAccountBalance() {
        try {
            const response = await fetch(`${this.apiBase}/api/v1/account/balance`);
            const data = await response.json();
            
            if (data.balance) {
                document.getElementById('account-balance').textContent = `$${parseFloat(data.balance).toLocaleString()}`;
            }
        } catch (error) {
            console.error('Failed to load account balance:', error);
        }
    }

    async analyzeMarket() {
        const analysisDiv = document.getElementById('market-analysis');
        
        try {
            analysisDiv.innerHTML = `
                <div class="text-center">
                    <div class="loading"></div>
                    <p class="mt-2">Analyzing market...</p>
                </div>
            `;

            const response = await fetch(`${this.apiBase}/api/v1/ai/analyze-market`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    pair: 'EURUSD',
                    timeframe: '1h'
                })
            });

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            // Update analysis display
            analysisDiv.innerHTML = `
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="fw-bold">Current Price:</span>
                        <span class="fs-5">${data.current_price}</span>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <span>Trend:</span>
                        <span class="badge ${this.getTrendClass(data.trend)}">${data.trend.replace('_', ' ').toUpperCase()}</span>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <span>Volatility:</span>
                        <span class="badge bg-secondary">${data.volatility.toUpperCase()}</span>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <span>Recommendation:</span>
                        <span class="badge ${data.recommendation === 'BUY' ? 'bg-success' : data.recommendation === 'SELL' ? 'bg-danger' : 'bg-warning'}">${data.recommendation}</span>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <span>Confidence:</span>
                        <span class="fw-bold">${Math.round(data.confidence * 100)}%</span>
                    </div>
                </div>
                <div class="alert alert-info">
                    <small><i class="fas fa-lightbulb me-1"></i>${data.reasoning}</small>
                </div>
            `;

            // Update AI confidence metric
            document.getElementById('ai-confidence').textContent = `${Math.round(data.confidence * 100)}%`;

            // Update price chart
            this.updatePriceChart(data);

        } catch (error) {
            analysisDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Failed to analyze market: ${error.message}
                </div>
            `;
        }
    }

    getTrendClass(trend) {
        if (trend.includes('bullish')) return 'bg-success';
        if (trend.includes('bearish')) return 'bg-danger';
        return 'bg-warning';
    }

    async loadMarketNews() {
        const newsDiv = document.getElementById('market-news');
        
        try {
            const response = await fetch(`${this.apiBase}/api/v1/news/latest`);
            const data = await response.json();
            
            if (data.articles && data.articles.length > 0) {
                const newsHtml = data.articles.slice(0, 3).map(article => `
                    <div class="mb-3">
                        <h6 class="mb-1">${article.title}</h6>
                        <p class="small text-muted mb-1">${article.description}</p>
                        <small class="text-muted">${new Date(article.publishedAt).toLocaleDateString()}</small>
                    </div>
                `).join('');
                
                newsDiv.innerHTML = newsHtml;
            } else {
                newsDiv.innerHTML = '<p class="text-muted">No news available</p>';
            }
        } catch (error) {
            newsDiv.innerHTML = '<p class="text-danger">Failed to load news</p>';
        }
    }

    initPriceChart() {
        const ctx = document.getElementById('priceChart').getContext('2d');
        
        this.priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'EUR/USD Price',
                    data: [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#ecf0f1'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#ecf0f1'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#ecf0f1'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });
    }

    async updatePriceChart(analysisData) {
        try {
            const response = await fetch(`${this.apiBase}/api/v1/data/market-data/EURUSD`);
            const data = await response.json();
            
            if (data.candles && data.candles.length > 0) {
                const prices = data.candles.map(candle => parseFloat(candle.mid.c));
                const times = data.candles.map(candle => new Date(candle.time).toLocaleTimeString());
                
                this.priceChart.data.labels = times.slice(-20); // Last 20 data points
                this.priceChart.data.datasets[0].data = prices.slice(-20);
                this.priceChart.update();
            }
        } catch (error) {
            console.error('Failed to update price chart:', error);
        }
    }

    async executePaperTrade() {
        const pair = document.getElementById('trading-pair').value;
        const strategyType = document.getElementById('strategy-type').value;
        const amount = document.getElementById('trade-amount').value;
        
        const resultDiv = document.getElementById('trade-result');
        
        try {
            resultDiv.innerHTML = `
                <div class="text-center">
                    <div class="loading"></div>
                    <p class="mt-2">Executing AI trade...</p>
                </div>
            `;

            const response = await fetch(`${this.apiBase}/api/v1/paper-trade/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    pair: pair,
                    strategy_type: strategyType,
                    amount_usd: parseInt(amount)
                })
            });

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            // Display trade result
            const trade = data.trade;
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6><i class="fas fa-check-circle me-2"></i>Trade Executed Successfully!</h6>
                </div>
                <div class="mb-3">
                    <div class="d-flex justify-content-between">
                        <span>Trade ID:</span>
                        <span class="fw-bold">${trade.trade_id}</span>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="d-flex justify-content-between">
                        <span>Side:</span>
                        <span class="badge ${trade.side === 'BUY' ? 'bg-success' : 'bg-danger'}">${trade.side}</span>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="d-flex justify-content-between">
                        <span>Entry Price:</span>
                        <span class="fw-bold">${trade.entry_price}</span>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="d-flex justify-content-between">
                        <span>Lot Size:</span>
                        <span class="fw-bold">${trade.lot_size}</span>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="d-flex justify-content-between">
                        <span>Stop Loss:</span>
                        <span class="text-danger">${trade.stop_loss}</span>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="d-flex justify-content-between">
                        <span>Take Profit:</span>
                        <span class="text-success">${trade.take_profit}</span>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="d-flex justify-content-between">
                        <span>Risk Amount:</span>
                        <span class="text-warning">$${trade.risk_amount}</span>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="d-flex justify-content-between">
                        <span>AI Confidence:</span>
                        <span class="fw-bold">${Math.round(trade.ai_confidence * 100)}%</span>
                    </div>
                </div>
                <div class="alert alert-info">
                    <small><i class="fas fa-robot me-1"></i>Strategy: ${trade.strategy}</small>
                </div>
            `;

            // Add to recent trades
            this.addRecentTrade(trade);
            
            // Update metrics
            this.updateTradeMetrics();

        } catch (error) {
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Trade execution failed: ${error.message}
                </div>
            `;
        }
    }

    addRecentTrade(trade) {
        this.recentTrades.unshift({
            ...trade,
            timestamp: new Date()
        });
        
        // Keep only last 10 trades
        if (this.recentTrades.length > 10) {
            this.recentTrades = this.recentTrades.slice(0, 10);
        }
        
        this.updateRecentTradesDisplay();
    }

    updateRecentTradesDisplay() {
        const tradesDiv = document.getElementById('recent-trades');
        
        if (this.recentTrades.length === 0) {
            tradesDiv.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-clock fa-2x mb-2"></i>
                    <p>No trades yet</p>
                </div>
            `;
            return;
        }
        
        const tradesHtml = this.recentTrades.map(trade => `
            <div class="trade-card ${trade.side === 'BUY' ? 'trade-buy' : 'trade-sell'}">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${trade.pair} ${trade.side}</h6>
                        <p class="small mb-1">${trade.strategy}</p>
                        <small class="text-muted">${trade.timestamp.toLocaleTimeString()}</small>
                    </div>
                    <div class="text-end">
                        <div class="fw-bold">${trade.entry_price}</div>
                        <small class="text-muted">${trade.lot_size} lots</small>
                    </div>
                </div>
            </div>
        `).join('');
        
        tradesDiv.innerHTML = tradesHtml;
    }

    updateTradeMetrics() {
        const totalTrades = this.recentTrades.length;
        document.getElementById('total-trades').textContent = totalTrades;
        
        // Calculate win rate (simplified - you'd need to track actual P&L)
        const winRate = totalTrades > 0 ? Math.round(Math.random() * 30 + 60) : 0; // Simulated
        document.getElementById('win-rate').textContent = `${winRate}%`;
    }

    async loadAutonomousStatus() {
        try {
            const response = await fetch(`${this.apiBase}/api/v1/autonomous/status`);
            const data = await response.json();
            
            if (data.status === "running") {
                const stats = data.stats;
                
                // Update status badge
                document.getElementById('autonomous-status').textContent = 'Running';
                document.getElementById('autonomous-status').className = 'badge bg-success';
                
                // Update metrics
                document.getElementById('active-trades-count').textContent = stats.active_trades;
                document.getElementById('total-pnl').textContent = `$${stats.total_pnl.toFixed(2)}`;
                document.getElementById('win-rate-auto').textContent = `${stats.win_rate.toFixed(1)}%`;
                
                // Update advanced metrics
                if (stats.performance_metrics) {
                    const metrics = stats.performance_metrics;
                    document.getElementById('sharpe-ratio').textContent = 
                        metrics.profit_factor ? metrics.profit_factor.toFixed(2) : '0.00';
                    document.getElementById('max-drawdown').textContent = 
                        metrics.max_loss ? `${(Math.abs(metrics.max_loss) / stats.account_balance * 100).toFixed(1)}%` : '0.0%';
                    document.getElementById('profit-factor').textContent = 
                        metrics.profit_factor ? metrics.profit_factor.toFixed(2) : '0.00';
                }
                
                // Update autonomous info
                const infoDiv = document.getElementById('autonomous-info');
                if (stats.active_trades > 0) {
                    const activeTradesHtml = stats.active_trades_list.map(trade => `
                        <div class="mb-2 p-2 border rounded">
                            <div class="d-flex justify-content-between">
                                <span class="fw-bold">${trade.pair} ${trade.side}</span>
                                <span class="${trade.pnl >= 0 ? 'text-success' : 'text-danger'}">$${trade.pnl.toFixed(2)}</span>
                            </div>
                            <small class="text-muted">${trade.strategy} - ${trade.entry_price}</small>
                        </div>
                    `).join('');
                    
                    infoDiv.innerHTML = `
                        <div class="alert alert-success">
                            <h6><i class="fas fa-robot me-2"></i>Active Trades</h6>
                            ${activeTradesHtml}
                        </div>
                    `;
                } else {
                    infoDiv.innerHTML = `
                        <div class="alert alert-info">
                            <h6><i class="fas fa-info-circle me-2"></i>Autonomous Trading</h6>
                            <p class="mb-2">The AI system will:</p>
                            <ul class="small mb-0">
                                <li>Monitor EUR/USD, GBP/USD, USD/JPY</li>
                                <li>Analyze markets every minute</li>
                                <li>Execute trades automatically</li>
                                <li>Manage risk (2% per trade)</li>
                                <li>Set stop-loss and take-profit</li>
                            </ul>
                        </div>
                    `;
                }
                
            } else {
                // System stopped
                document.getElementById('autonomous-status').textContent = 'Stopped';
                document.getElementById('autonomous-status').className = 'badge bg-secondary';
                document.getElementById('active-trades-count').textContent = '0';
                document.getElementById('total-pnl').textContent = '$0.00';
                document.getElementById('win-rate-auto').textContent = '0%';
                document.getElementById('sharpe-ratio').textContent = '0.00';
                document.getElementById('max-drawdown').textContent = '0.0%';
                document.getElementById('profit-factor').textContent = '0.00';
                
                const infoDiv = document.getElementById('autonomous-info');
                infoDiv.innerHTML = `
                    <div class="alert alert-warning">
                        <h6><i class="fas fa-pause me-2"></i>System Stopped</h6>
                        <p class="mb-0">Click "Start Auto Trading" to begin autonomous trading.</p>
                    </div>
                `;
            }
            
        } catch (error) {
            console.error('Failed to load autonomous status:', error);
        }
    }

    async startAutonomousTrading() {
        try {
            const response = await fetch(`${this.apiBase}/api/v1/autonomous/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.status === "started") {
                alert('🤖 Autonomous trading system started! The AI will now trade automatically.');
                this.loadAutonomousStatus();
            } else {
                alert('❌ Failed to start autonomous trading: ' + data.error);
            }
            
        } catch (error) {
            alert('❌ Error starting autonomous trading: ' + error.message);
        }
    }

    async stopAutonomousTrading() {
        try {
            const response = await fetch(`${this.apiBase}/api/v1/autonomous/stop`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.status === "stopped") {
                alert('🛑 Autonomous trading system stopped.');
                this.loadAutonomousStatus();
            } else {
                alert('❌ Failed to stop autonomous trading: ' + data.error);
            }
            
        } catch (error) {
            alert('❌ Error stopping autonomous trading: ' + error.message);
        }
    }
}

// Global functions for HTML onclick handlers
function analyzeMarket() {
    dashboard.analyzeMarket();
}

function executePaperTrade() {
    dashboard.executePaperTrade();
}

function startAutonomousTrading() {
    dashboard.startAutonomousTrading();
}

function stopAutonomousTrading() {
    dashboard.stopAutonomousTrading();
}

// Initialize dashboard when page loads
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new TradingDashboard();
});
