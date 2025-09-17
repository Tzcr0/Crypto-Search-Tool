"""
Dashboard UI for Phantom Detector.
Real-time Plotly Dash interface for trading intelligence visualization.
"""

import asyncio
import threading
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc

from config.settings import config
from utils.logging_config import logger
from utils.helpers import format_currency, format_percentage, get_timestamp
from data_ingestion.mock_data import mock_generator
from signal_processing.algorithms import signal_processor
from phantom_oracle.oracle import phantom_oracle


class PhantomDashboard:
    """
    Main dashboard class for Phantom Detector.
    Provides real-time visualization of trading data and intelligence signals.
    """
    
    def __init__(self):
        """Initialize the Phantom Dashboard."""
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.CYBORG],  # Dark theme
            suppress_callback_exceptions=True
        )
        
        # Data storage
        self.price_data: List[Dict[str, Any]] = []
        self.signals_data: List[Dict[str, Any]] = []
        self.oracle_analysis: Dict[str, Any] = {}
        
        # Setup layout and callbacks
        self._setup_layout()
        self._setup_callbacks()
        
        # Subscribe to data updates
        mock_generator.subscribe(self._on_market_data_update)
        
        logger.info("PhantomDashboard initialized")
    
    def _setup_layout(self) -> None:
        """Setup the dashboard layout."""
        self.app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("🔮 Phantom Detector", className="text-center mb-0"),
                    html.P("Next-Gen Trading Intelligence Platform", 
                          className="text-center text-muted mb-4"),
                ], width=12)
            ]),
            
            # Status Bar
            dbc.Row([
                dbc.Col([
                    dbc.Alert(
                        id="status-alert",
                        children="🟢 System Online - Mock Data Active",
                        color="success",
                        className="mb-3"
                    )
                ], width=12)
            ]),
            
            # Main Content Tabs
            dbc.Row([
                dbc.Col([
                    dbc.Tabs([
                        dbc.Tab(label="📈 Live Trading", tab_id="trading-tab"),
                        dbc.Tab(label="🚨 Alerts", tab_id="alerts-tab"),
                        dbc.Tab(label="🐋 Whale Tracker", tab_id="whale-tab"),
                        dbc.Tab(label="🔮 Oracle", tab_id="oracle-tab"),
                        dbc.Tab(label="📊 Analytics", tab_id="analytics-tab"),
                    ], id="main-tabs", active_tab="trading-tab")
                ], width=12)
            ]),
            
            # Tab Content
            dbc.Row([
                dbc.Col([
                    html.Div(id="tab-content")
                ], width=12)
            ]),
            
            # Auto-refresh interval
            dcc.Interval(
                id='interval-component',
                interval=2000,  # 2 seconds
                n_intervals=0
            ),
            
            # Store for data
            dcc.Store(id='price-data-store'),
            dcc.Store(id='signals-data-store'),
            
        ], fluid=True, className="p-4")
    
    def _setup_callbacks(self) -> None:
        """Setup Dash callbacks for interactivity."""
        
        @self.app.callback(
            Output('tab-content', 'children'),
            Input('main-tabs', 'active_tab')
        )
        def render_tab_content(active_tab):
            """Render content based on active tab."""
            if active_tab == "trading-tab":
                return self._create_trading_tab()
            elif active_tab == "alerts-tab":
                return self._create_alerts_tab()
            elif active_tab == "whale-tab":
                return self._create_whale_tab()
            elif active_tab == "oracle-tab":
                return self._create_oracle_tab()
            elif active_tab == "analytics-tab":
                return self._create_analytics_tab()
            else:
                return html.Div("Tab content loading...")
        
        @self.app.callback(
            [Output('price-chart', 'figure'),
             Output('volume-chart', 'figure'),
             Output('current-price', 'children'),
             Output('price-change', 'children'),
             Output('market-status', 'children')],
            Input('interval-component', 'n_intervals')
        )
        def update_trading_data(n):
            """Update trading data displays."""
            if not self.price_data:
                return {}, {}, "Loading...", "Loading...", "Loading..."
            
            # Create price chart
            price_fig = self._create_price_chart()
            
            # Create volume chart  
            volume_fig = self._create_volume_chart()
            
            # Get current data
            current_data = self.price_data[-1] if self.price_data else {}
            current_price = current_data.get("price", 0)
            price_change = current_data.get("price_change_pct", 0)
            
            # Format displays
            price_display = f"${current_price:,.2f}"
            
            change_color = "success" if price_change >= 0 else "danger"
            change_symbol = "+" if price_change >= 0 else ""
            change_display = dbc.Badge(
                f"{change_symbol}{price_change:.2f}%",
                color=change_color,
                className="ms-2"
            )
            
            market_status = current_data.get("market_session", "unknown").title()
            
            return price_fig, volume_fig, price_display, change_display, market_status
        
        @self.app.callback(
            [Output('spoofing-alerts', 'children'),
             Output('whale-alerts', 'children'),
             Output('smt-signals', 'children'),
             Output('narrative-signals', 'children')],
            Input('interval-component', 'n_intervals')
        )
        def update_alerts(n):
            """Update alert displays."""
            # Get recent alerts
            spoofing_alerts = signal_processor.get_recent_alerts("spoofing", 5)
            whale_alerts = signal_processor.get_recent_alerts("whales", 5) 
            smt_signals = signal_processor.get_recent_alerts("smt", 5)
            narrative_signals = signal_processor.get_recent_alerts("narrative", 5)
            
            return (
                self._format_alerts(spoofing_alerts, "spoofing"),
                self._format_alerts(whale_alerts, "whale"),
                self._format_alerts(smt_signals, "smt"),
                self._format_alerts(narrative_signals, "narrative")
            )
        
        @self.app.callback(
            [Output('oracle-summary', 'children'),
             Output('oracle-forecast', 'children'),
             Output('oracle-recommendations', 'children')],
            Input('interval-component', 'n_intervals')
        )
        def update_oracle_content(n):
            """Update oracle analysis content."""
            # Get oracle analysis
            trend_summary = phantom_oracle.summarize_trends()
            forecast = phantom_oracle.get_market_forecast("24h")
            
            # Get recommendations
            current_price = self.price_data[-1].get("price", 50000) if self.price_data else 50000
            current_signals = self.signals_data[-1] if self.signals_data else {}
            recommendations = phantom_oracle.recommend_trades(current_price, current_signals)
            
            return (
                self._format_oracle_summary(trend_summary),
                self._format_oracle_forecast(forecast),
                self._format_oracle_recommendations(recommendations)
            )
    
    def _create_trading_tab(self) -> html.Div:
        """Create the main trading tab content."""
        return html.Div([
            # Price and stats row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Current Price", className="card-title"),
                            html.H2(id="current-price", className="text-primary"),
                            html.Div(id="price-change")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Market Status", className="card-title"),
                            html.H3(id="market-status", className="text-info")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Active Alerts", className="card-title"),
                            html.H3("0", className="text-warning")  # TODO: Dynamic
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Oracle Status", className="card-title"),
                            html.H3("🟢 Active", className="text-success")
                        ])
                    ])
                ], width=3),
            ], className="mb-4"),
            
            # Charts row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Real-Time Price Chart"),
                        dbc.CardBody([
                            dcc.Graph(id="price-chart", style={'height': '400px'})
                        ])
                    ])
                ], width=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Volume"),
                        dbc.CardBody([
                            dcc.Graph(id="volume-chart", style={'height': '400px'})
                        ])
                    ])
                ], width=4),
            ])
        ])
    
    def _create_alerts_tab(self) -> html.Div:
        """Create the alerts tab content."""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🚨 Spoofing Detection"),
                        dbc.CardBody(id="spoofing-alerts")
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🐋 Whale Activity"),
                        dbc.CardBody(id="whale-alerts")
                    ])
                ], width=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📊 Market Structure (SMT)"),
                        dbc.CardBody(id="smt-signals")
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📰 Narrative Signals"),
                        dbc.CardBody(id="narrative-signals")
                    ])
                ], width=6),
            ])
        ])
    
    def _create_whale_tab(self) -> html.Div:
        """Create the whale tracking tab content."""
        return html.Div([
            dbc.Card([
                dbc.CardHeader("🐋 Whale Movement Tracker"),
                dbc.CardBody([
                    html.P("Advanced whale tracking visualization coming soon...", 
                          className="text-muted"),
                    html.Hr(),
                    html.H5("Recent Whale Activity:"),
                    html.Div(id="whale-activity-list")
                ])
            ])
        ])
    
    def _create_oracle_tab(self) -> html.Div:
        """Create the oracle analysis tab content."""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🔮 Oracle Market Analysis"),
                        dbc.CardBody(id="oracle-summary")
                    ])
                ], width=12)
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📈 Market Forecast"),
                        dbc.CardBody(id="oracle-forecast")
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("💡 Trade Recommendations"),
                        dbc.CardBody(id="oracle-recommendations")
                    ])
                ], width=6),
            ])
        ])
    
    def _create_analytics_tab(self) -> html.Div:
        """Create the analytics tab content."""
        return html.Div([
            dbc.Card([
                dbc.CardHeader("📊 Advanced Analytics"),
                dbc.CardBody([
                    html.P("Advanced analytics dashboard coming soon...", 
                          className="text-muted"),
                    html.Hr(),
                    html.H5("Features in Development:"),
                    html.Ul([
                        html.Li("Historical backtesting"),
                        html.Li("Performance metrics"),
                        html.Li("Risk analytics"),
                        html.Li("Portfolio tracking"),
                        html.Li("Market correlation analysis")
                    ])
                ])
            ])
        ])
    
    def _create_price_chart(self) -> go.Figure:
        """Create real-time price chart."""
        if not self.price_data:
            return go.Figure()
        
        df = pd.DataFrame(self.price_data[-50:])  # Last 50 points
        
        fig = go.Figure()
        
        # Add price line
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(df['datetime']),
            y=df['price'],
            mode='lines',
            name='BTC/USD',
            line=dict(color='#00d4aa', width=2),
            hovertemplate='<b>Price:</b> $%{y:,.2f}<br>' +
                         '<b>Time:</b> %{x}<br>' +
                         '<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title="Real-Time BTC Price",
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            template="plotly_dark",
            showlegend=True,
            height=400,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        return fig
    
    def _create_volume_chart(self) -> go.Figure:
        """Create volume chart."""
        if not self.price_data:
            return go.Figure()
        
        df = pd.DataFrame(self.price_data[-20:])  # Last 20 points
        
        fig = go.Figure()
        
        # Add volume bars
        colors = ['green' if df.iloc[i]['price_change'] >= 0 else 'red' 
                 for i in range(len(df))]
        
        fig.add_trace(go.Bar(
            x=pd.to_datetime(df['datetime']),
            y=df['volume'],
            name='Volume',
            marker_color=colors,
            hovertemplate='<b>Volume:</b> %{y:,.0f}<br>' +
                         '<b>Time:</b> %{x}<br>' +
                         '<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title="Trading Volume",
            xaxis_title="Time",
            yaxis_title="Volume",
            template="plotly_dark",
            showlegend=False,
            height=400,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        return fig
    
    def _format_alerts(self, alerts: List[Dict[str, Any]], alert_type: str) -> html.Div:
        """Format alerts for display."""
        if not alerts:
            return html.P("No recent alerts", className="text-muted")
        
        alert_elements = []
        for alert in alerts[-5:]:  # Show last 5 alerts
            severity = alert.get("severity", "info")
            
            # Color mapping
            color_map = {
                "critical": "danger",
                "high": "warning", 
                "medium": "info",
                "low": "secondary"
            }
            
            badge_color = color_map.get(severity, "secondary")
            
            alert_element = dbc.Alert([
                html.H6([
                    dbc.Badge(severity.upper(), color=badge_color, className="me-2"),
                    alert.get("description", "Alert")
                ], className="mb-1"),
                html.Small(
                    f"Time: {datetime.fromtimestamp(alert.get('timestamp', 0)).strftime('%H:%M:%S')}",
                    className="text-muted"
                )
            ], color="dark", className="mb-2")
            
            alert_elements.append(alert_element)
        
        return html.Div(alert_elements)
    
    def _format_oracle_summary(self, summary: str) -> html.Div:
        """Format oracle summary for display."""
        return html.Div([
            html.P(summary, className="lead"),
            html.Hr(),
            html.Small(
                f"Last updated: {datetime.now().strftime('%H:%M:%S')}",
                className="text-muted"
            )
        ])
    
    def _format_oracle_forecast(self, forecast: Dict[str, Any]) -> html.Div:
        """Format oracle forecast for display."""
        if forecast.get("status") == "error":
            return html.P("Forecast unavailable", className="text-muted")
        
        target_price = forecast.get("primary_target", 0)
        confidence = forecast.get("confidence", 0)
        timeframe = forecast.get("timeframe", "24h")
        
        return html.Div([
            html.H5(f"${target_price:,.0f}", className="text-success"),
            html.P(f"{timeframe} target price"),
            dbc.Progress(
                value=confidence * 100,
                label=f"{confidence:.1%} confidence",
                color="info",
                className="mb-2"
            ),
            html.Hr(),
            html.H6("Scenarios:"),
            html.Ul([
                html.Li(f"Bullish: {scenario.get('probability', 0):.1%} - ${scenario.get('price_target', 0):,.0f}")
                for scenario in forecast.get("scenarios", [])
                if scenario.get("scenario") == "bullish"
            ] + [
                html.Li(f"Bearish: {scenario.get('probability', 0):.1%} - ${scenario.get('price_target', 0):,.0f}")
                for scenario in forecast.get("scenarios", [])
                if scenario.get("scenario") == "bearish"
            ])
        ])
    
    def _format_oracle_recommendations(self, recommendations: List[Dict[str, Any]]) -> html.Div:
        """Format oracle recommendations for display."""
        if not recommendations:
            return html.P("No active recommendations", className="text-muted")
        
        rec_elements = []
        for rec in recommendations:
            action = rec.get("action", "hold").upper()
            asset = rec.get("asset", "BTCUSD")
            confidence = rec.get("confidence", 0)
            
            action_color = {
                "BUY": "success",
                "SELL": "danger", 
                "WAIT": "warning",
                "HOLD": "info"
            }.get(action, "secondary")
            
            rec_element = dbc.Card([
                dbc.CardBody([
                    html.H6([
                        dbc.Badge(action, color=action_color, className="me-2"),
                        asset
                    ]),
                    html.P(rec.get("reasoning", ""), className="mb-1"),
                    dbc.Progress(
                        value=confidence * 100,
                        label=f"{confidence:.1%}",
                        color="info",
                        size="sm"
                    )
                ])
            ], className="mb-2")
            
            rec_elements.append(rec_element)
        
        return html.Div(rec_elements)
    
    def _on_market_data_update(self, market_data: Dict[str, Any]) -> None:
        """Handle market data updates from the mock generator."""
        try:
            # Update price data
            tick_data = market_data.get("tick", {})
            if tick_data:
                self.price_data.append(tick_data)
                
                # Keep only last 200 price points
                if len(self.price_data) > 200:
                    self.price_data.pop(0)
            
            # Process signals
            signals = signal_processor.process_market_data(market_data)
            if signals:
                self.signals_data.append(signals)
                
                # Keep only last 100 signal sets
                if len(self.signals_data) > 100:
                    self.signals_data.pop(0)
            
            # Update oracle analysis periodically
            if len(self.price_data) % 10 == 0:  # Every 10th update
                self.oracle_analysis = phantom_oracle.analyze_market_state(
                    self.price_data[-20:], signals
                )
                
        except Exception as e:
            logger.error(f"Error updating dashboard data: {e}")
    
    def run(self, host: str = None, port: int = None, debug: bool = None) -> None:
        """
        Run the dashboard server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Debug mode
        """
        host = host or config.DASH_HOST
        port = port or config.DASH_PORT
        debug = debug if debug is not None else config.DASH_DEBUG
        
        logger.info(f"Starting Phantom Dashboard on http://{host}:{port}")
        
        self.app.run_server(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )


# Global dashboard instance
phantom_dashboard = PhantomDashboard()