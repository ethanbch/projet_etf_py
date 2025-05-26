"""
Module contenant les fonctions métier pour l'analyse des ETFs.
Calcul des indicateurs de performance, des ratios et des statistiques.
"""

from datetime import datetime
from typing import Dict, List

import numpy as np

from src.model import ETFPriceData, PerformanceMetrics


def calculate_returns(prices: List[float]) -> List[float]:
    """Calcule les rendements journaliers."""
    prices_array = np.array(prices)
    return (prices_array[1:] / prices_array[:-1]) - 1


def calculate_sortino_ratio(returns: np.ndarray, risk_free_rate: float) -> float:
    """Calcule le ratio de Sortino."""
    excess_returns = returns - risk_free_rate / 252  # daily risk-free rate
    downside_returns = np.where(returns < 0, returns, 0)
    downside_volatility = np.std(downside_returns) * np.sqrt(252)
    return (
        np.mean(excess_returns) * 252 / downside_volatility
        if downside_volatility != 0
        else 0
    )


def calculate_performance_metrics(
    price_data: List[ETFPriceData],
    risk_free_rate: float = 0.01,
    benchmark_returns: np.ndarray = None,
) -> PerformanceMetrics:
    """Calcule les métriques de performance pour un ETF."""
    prices = np.array([data.adj_close for data in price_data])
    returns = calculate_returns(prices)

    # Rendements
    total_return = (prices[-1] / prices[0]) - 1
    holding_period = len(returns)
    annualized_return = (1 + total_return) ** (252 / holding_period) - 1

    # Risque
    volatility = np.std(returns) * np.sqrt(252)

    # Ratios de performance ajustés au risque
    excess_returns = returns - risk_free_rate / 252  # daily risk-free rate
    sharpe_ratio = np.mean(excess_returns) * 252 / volatility if volatility != 0 else 0
    sortino_ratio = calculate_sortino_ratio(returns, risk_free_rate)

    # Maximum Drawdown
    cumulative_returns = np.cumprod(1 + returns)
    running_max = np.maximum.accumulate(cumulative_returns)
    drawdowns = (running_max - cumulative_returns) / running_max
    max_drawdown = np.max(drawdowns)

    # Métriques relatives au benchmark si disponible
    if benchmark_returns is not None and len(benchmark_returns) == len(returns):
        # Beta et Alpha
        covariance = np.cov(returns, benchmark_returns)[0, 1]
        benchmark_variance = np.var(benchmark_returns)
        beta = covariance / benchmark_variance if benchmark_variance != 0 else 1

        expected_return = risk_free_rate + beta * (
            np.mean(benchmark_returns) * 252 - risk_free_rate
        )
        alpha = annualized_return - expected_return

        # R-squared
        correlation = np.corrcoef(returns, benchmark_returns)[0, 1]
        r_squared = correlation**2

        # Tracking Error
        tracking_error = np.std(returns - benchmark_returns) * np.sqrt(252)

        # Information Ratio
        active_return = annualized_return - np.mean(benchmark_returns) * 252
        information_ratio = active_return / tracking_error if tracking_error != 0 else 0
    else:
        beta = alpha = r_squared = tracking_error = information_ratio = None

    return PerformanceMetrics(
        ticker=price_data[0].ticker,
        period=f"{holding_period}d",
        total_return=total_return,
        annualized_return=annualized_return,
        volatility=volatility,
        sharpe_ratio=sharpe_ratio,
        sortino_ratio=sortino_ratio,
        max_drawdown=max_drawdown,
        beta=beta,
        alpha=alpha,
        r_squared=r_squared,
        tracking_error=tracking_error,
        information_ratio=information_ratio,
    )
