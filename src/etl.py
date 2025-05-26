"""
Module pour l'Extraction, la Transformation et le Chargement (ETL) des données.
- Récupération des données depuis yfinance
- Lecture des métadonnées des ETFs depuis un CSV
- Nettoyage et transformation des données
- Chargement des données dans la base de données
"""
import pandas as pd
import yfinance as yf
from typing import List, Optional
from datetime import datetime

from .constants import *
from .model import ETF, ETFPriceData
from .repository import ETFRepository


class ETFDataLoader:
    def __init__(self, repository: ETFRepository):
        self.repository = repository

    def load_etf_metadata(self, csv_path: str) -> List[ETF]:
        """Charge les métadonnées des ETFs depuis un fichier CSV."""
        df = pd.read_csv(csv_path)
        return [
            ETF(
                ticker=row[TICKER_COL],
                name=row[NAME_COL],
                issuer=row.get(ISSUER_COL),
                ter=row.get(TER_COL),
                inception_date=pd.to_datetime(row.get(INCEPTION_DATE_COL))
            )
            for _, row in df.iterrows()
        ]

    def fetch_price_data(
        self, 
        ticker: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: str = DEFAULT_PERIOD
    ) -> List[ETFPriceData]:
        """Récupère les données de prix depuis yfinance."""
        etf = yf.Ticker(ticker)
        hist = etf.history(period=period, start=start_date, end=end_date)
        
        return [
            ETFPriceData(
                ticker=ticker,
                date=index,
                adj_close=row['Close'],
                volume=row['Volume']
            )
            for index, row in hist.iterrows()
        ]


def run_etl_pipeline():
    """Exécute le pipeline ETL complet."""
    print("Pipeline ETL démarré...")
    # À implémenter : logique du pipeline
    pass


if __name__ == '__main__':
    run_etl_pipeline()
    print("Pipeline ETL terminé.")
