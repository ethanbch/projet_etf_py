"""
Module pour la visualisation des données et des résultats d'analyse.
Génération des graphiques et des tableaux avec Streamlit.
"""

from datetime import datetime
from typing import Dict, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.model import ETF, ComparisonResult, PerformanceMetrics


class ETFDashboard:
    def __init__(self):
        pass

    def display_header(self):
        """Affiche l'en-tête de l'application."""
        st.title("📈 Comparateur de Performance d'ETFs Thématiques")
        st.markdown(
            """
        Analysez et comparez les performances des ETFs thématiques.
        Visualisez les métriques clés et les tendances historiques.
        """
        )

    def plot_performance_comparison(
        self, price_data: Dict[str, List[float]], start_date: datetime
    ):
        """Crée un graphique de comparaison des performances."""
        fig = go.Figure()

        for ticker, prices in price_data.items():
            normalized_prices = [p / prices[0] for p in prices]
            fig.add_trace(go.Scatter(y=normalized_prices, name=ticker, mode="lines"))

        fig.update_layout(
            title="Performance Relative des ETFs",
            yaxis_title="Performance (%)",
            xaxis_title="Période",
            hovermode="x unified",
        )

        st.plotly_chart(fig, use_container_width=True)

    def display_metrics_table(self, metrics: Dict[str, PerformanceMetrics]):
        """Affiche un tableau des métriques de performance."""
        data = []
        for ticker, metric in metrics.items():
            data.append(
                {
                    "ETF": ticker,
                    "Rendement Total": f"{metric.total_return:.2%}",
                    "Rendement Annualisé": f"{metric.annualized_return:.2%}",
                    "Volatilité": f"{metric.volatility:.2%}",
                    "Ratio de Sharpe": f"{metric.sharpe_ratio:.2f}",
                    "Ratio de Sortino": (
                        f"{metric.sortino_ratio:.2f}" if metric.sortino_ratio else "N/A"
                    ),
                    "Drawdown Maximum": f"{metric.max_drawdown:.2%}",
                    "Beta": f"{metric.beta:.2f}" if metric.beta else "N/A",
                    "Alpha": f"{metric.alpha:.2%}" if metric.alpha else "N/A",
                    "R²": f"{metric.r_squared:.2%}" if metric.r_squared else "N/A",
                    "Tracking Error": (
                        f"{metric.tracking_error:.2%}"
                        if metric.tracking_error
                        else "N/A"
                    ),
                    "Ratio d'Information": (
                        f"{metric.information_ratio:.2f}"
                        if metric.information_ratio
                        else "N/A"
                    ),
                }
            )

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

    def plot_metrics_radar(self, metrics: Dict[str, PerformanceMetrics]):
        """Crée un graphique radar des métriques clés."""
        categories = ["Rendement", "Sharpe", "Volatilité", "Max Drawdown"]

        fig = go.Figure()

        for ticker, metric in metrics.items():
            fig.add_trace(
                go.Scatterpolar(
                    r=[
                        metric.annualized_return * 100,  # En pourcentage
                        metric.sharpe_ratio,
                        metric.volatility * 100,  # En pourcentage
                        metric.max_drawdown * 100,  # En pourcentage
                    ],
                    theta=categories,
                    name=ticker,
                    fill="toself",
                )
            )

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True, range=[-50, 50]  # Ajuster selon les valeurs réelles
                )
            ),
            title="Comparaison des métriques clés",
            showlegend=True,
        )

        st.plotly_chart(fig, use_container_width=True)

    def display_comparison(
        self,
        base_etf: ETF,
        comparison_etfs: List[ETF],
        base_prices: List[float],
        comparison_prices: Dict[str, List[float]],
        risk_free_rate: float = 0.01,
    ):
        """Affiche la comparaison complète des ETFs."""
        st.write(f"### Comparaison avec {base_etf.name} ({base_etf.ticker})")

        # Création des colonnes pour l'affichage
        col1, col2 = st.columns([2, 1])

        with col1:
            # Graphique de performance relative
            all_prices = {base_etf.ticker: base_prices}
            all_prices.update(comparison_prices)

            # Extraction des dates à partir des données
            dates = [price.date for price in base_prices]

            # Préparation des données pour le graphique
            fig = go.Figure()

            for ticker, prices in all_prices.items():
                # Normalisation des prix (base 100)
                normalized_prices = [
                    100 * price.adj_close / prices[0].adj_close for price in prices
                ]

                fig.add_trace(
                    go.Scatter(x=dates, y=normalized_prices, name=ticker, mode="lines")
                )

            fig.update_layout(
                title="Performance relative (base 100)",
                xaxis_title="Date",
                yaxis_title="Performance (%)",
                hovermode="x unified",
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Calcul et affichage des métriques
            from src.helpers_business import calculate_performance_metrics

            metrics = {
                base_etf.ticker: calculate_performance_metrics(
                    base_prices, risk_free_rate
                )
            }

            for ticker, prices in comparison_prices.items():
                metrics[ticker] = calculate_performance_metrics(prices, risk_free_rate)

            # Tableau des métriques
            self.display_metrics_table(metrics)

            # Graphique radar des métriques
            self.plot_metrics_radar(metrics)

    def run(self):
        """Point d'entrée principal du dashboard."""
        self.display_header()


if __name__ == "__main__":
    dashboard = ETFDashboard()
    dashboard.run()
