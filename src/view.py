"""
Module pour la visualisation des données et des résultats d'analyse.
Génération des graphiques et des tableaux avec Streamlit.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import List, Dict
from datetime import datetime

from .model import ETF, PerformanceMetrics, ComparisonResult


class ETFDashboard:
    def __init__(self):
        st.set_page_config(
            page_title="ETF Performance Comparator",
            page_icon="📈",
            layout="wide"
        )
    
    def display_header(self):
        """Affiche l'en-tête de l'application."""
        st.title("📈 Comparateur de Performance d'ETFs Thématiques")
        st.markdown("""
        Analysez et comparez les performances des ETFs thématiques.
        Visualisez les métriques clés et les tendances historiques.
        """)
    
    def plot_performance_comparison(
        self,
        price_data: Dict[str, List[float]],
        start_date: datetime
    ):
        """Crée un graphique de comparaison des performances."""
        fig = go.Figure()
        
        for ticker, prices in price_data.items():
            normalized_prices = [p/prices[0] for p in prices]
            fig.add_trace(go.Scatter(
                y=normalized_prices,
                name=ticker,
                mode='lines'
            ))
        
        fig.update_layout(
            title="Performance Relative des ETFs",
            yaxis_title="Performance (%)",
            xaxis_title="Période",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_metrics_table(self, metrics: Dict[str, PerformanceMetrics]):
        """Affiche un tableau des métriques de performance."""
        data = []
        for ticker, metric in metrics.items():
            data.append({
                'ETF': ticker,
                'Rendement Total': f"{metric.total_return:.2%}",
                'Rendement Annualisé': f"{metric.annualized_return:.2%}",
                'Volatilité': f"{metric.volatility:.2%}",
                'Ratio de Sharpe': f"{metric.sharpe_ratio:.2f}",
                'Drawdown Maximum': f"{metric.max_drawdown:.2%}"
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    
    def run(self):
        """Point d'entrée principal du dashboard."""
        self.display_header()
        
        # À implémenter : logique principale du dashboard
        pass


if __name__ == '__main__':
    dashboard = ETFDashboard()
    dashboard.run()
