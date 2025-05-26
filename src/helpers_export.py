"""
Module pour l'export des données et des résultats d'analyse.
Gestion des exports en CSV, Excel, et autres formats.
"""
import pandas as pd
from typing import List, Dict
from datetime import datetime

from .model import ETF, PerformanceMetrics, ComparisonResult


def export_performance_metrics_to_csv(
    metrics: Dict[str, PerformanceMetrics],
    output_path: str
) -> None:
    """Exporte les métriques de performance vers un fichier CSV."""
    data = []
    for ticker, metric in metrics.items():
        data.append({
            'Ticker': ticker,
            'Period': metric.period,
            'Total Return': f"{metric.total_return:.2%}",
            'Annualized Return': f"{metric.annualized_return:.2%}",
            'Volatility': f"{metric.volatility:.2%}",
            'Sharpe Ratio': f"{metric.sharpe_ratio:.2f}",
            'Max Drawdown': f"{metric.max_drawdown:.2%}"
        })
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)


def export_comparison_result_to_excel(
    result: ComparisonResult,
    output_path: str
) -> None:
    """Exporte les résultats de comparaison vers un fichier Excel."""
    with pd.ExcelWriter(output_path) as writer:
        # Feuille des métriques
        metrics_data = []
        for ticker, metric in result.metrics.items():
            metrics_data.append({
                'Ticker': ticker,
                'Total Return': metric.total_return,
                'Annualized Return': metric.annualized_return,
                'Volatility': metric.volatility,
                'Sharpe Ratio': metric.sharpe_ratio,
                'Max Drawdown': metric.max_drawdown
            })
        
        pd.DataFrame(metrics_data).to_excel(
            writer, 
            sheet_name='Performance Metrics',
            index=False
        )
