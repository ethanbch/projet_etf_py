"""
Module pour la sérialisation et la désérialisation des objets du modèle.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from src.model import ETF, ComparisonResult, ETFPriceData, PerformanceMetrics


class ETFEncoder(json.JSONEncoder):
    """Encodeur JSON personnalisé pour les objets du modèle."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, (ETF, ETFPriceData, PerformanceMetrics, ComparisonResult)):
            return obj.__dict__
        return super().default(obj)


def serialize_etf(etf: ETF) -> Dict[str, Any]:
    """Sérialise un objet ETF en dictionnaire."""
    return json.loads(json.dumps(etf, cls=ETFEncoder))


def deserialize_etf(data: Dict[str, Any]) -> ETF:
    """Désérialise un dictionnaire en objet ETF."""
    if "inception_date" in data and data["inception_date"]:
        data["inception_date"] = datetime.fromisoformat(data["inception_date"])
    return ETF(**data)


def serialize_comparison_result(result: ComparisonResult) -> Dict[str, Any]:
    """Sérialise un objet ComparisonResult en dictionnaire."""
    return json.loads(json.dumps(result, cls=ETFEncoder))


def deserialize_comparison_result(data: Dict[str, Any]) -> ComparisonResult:
    """Désérialise un dictionnaire en objet ComparisonResult."""
    # Conversion des dates
    data["start_date"] = datetime.fromisoformat(data["start_date"])
    data["end_date"] = datetime.fromisoformat(data["end_date"])
    data["analysis_timestamp"] = datetime.fromisoformat(data["analysis_timestamp"])

    # Conversion des ETFs
    data["base_etf"] = deserialize_etf(data["base_etf"])
    data["comparison_etfs"] = [deserialize_etf(etf) for etf in data["comparison_etfs"]]

    # Conversion des métriques
    data["metrics"] = {
        ticker: PerformanceMetrics(**metrics)
        for ticker, metrics in data["metrics"].items()
    }

    return ComparisonResult(**data)
