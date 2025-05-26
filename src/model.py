"""
Modèles de données pour le projet ETF Comparator.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict


@dataclass
class ETF:
    ticker: str
    name: str
    issuer: Optional[str] = None
    ter: Optional[float] = None  # Total Expense Ratio
    inception_date: Optional[datetime] = None
    category: Optional[str] = None
    assets_under_management: Optional[float] = None
    description: Optional[str] = None


@dataclass
class ETFPriceData:
    ticker: str
    date: datetime
    adj_close: float
    volume: Optional[int] = None
    

@dataclass
class PerformanceMetrics:
    ticker: str
    period: str
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    tracking_error: Optional[float] = None
    beta: Optional[float] = None
    correlation: Optional[float] = None


@dataclass
class ComparisonResult:
    base_etf: ETF
    comparison_etfs: List[ETF]
    metrics: Dict[str, PerformanceMetrics]
    start_date: datetime
    end_date: datetime
    analysis_timestamp: datetime = field(default_factory=datetime.now)
