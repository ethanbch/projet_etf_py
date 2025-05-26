"""
Module contenant les fonctions métier pour l'analyse des ETFs.
Calcul des indicateurs de performance, des ratios et des statistiques.
"""
import numpy as np
from typing import List, Dict
from datetime import datetime

from .model import ETFPriceData, PerformanceMetrics


def calculate_returns(prices: List[float]) -> List[float]:
    """Calcule les rendements journaliers."""
    prices_array = np.array(prices)
    return (prices_array[1:] / prices_array[:-1]) - 1


def calculate_performance_metrics(
    price_data: List[ETFPriceData],
    risk_free_rate: float = 0.01
) -> PerformanceMetrics:
    """Calcule les métriques de performance pour un ETF."""
    prices = [data.adj_close for data in price_data]
    returns = calculate_returns(prices)
    
    total_return = (prices[-1] / prices[0]) - 1
    annualized_return = (1 + total_return) ** (252 / len(returns)) - 1
    volatility = np.std(returns) * np.sqrt(252)
    
    excess_returns = annualized_return - risk_free_rate
    sharpe_ratio = excess_returns / volatility if volatility != 0 else 0
    
    # Calcul du maximum drawdown
    peak = prices[0]
    max_drawdown = 0
    for price in prices[1:]:
        if price > peak:
            peak = price
        drawdown = (peak - price) / peak
        max_drawdown = max(max_drawdown, drawdown)
    
    return PerformanceMetrics(
        ticker=price_data[0].ticker,
        period=f"{len(returns)}d",
        total_return=total_return,
        annualized_return=annualized_return,
        volatility=volatility,
        sharpe_ratio=sharpe_ratio,
        max_drawdown=max_drawdown
    )
