"""
Module pour l'Extraction, la Transformation et le Chargement (ETL) des données.
- Récupération des données depuis yfinance
- Lecture des métadonnées des ETFs depuis un CSV
- Nettoyage et transformation des données
- Chargement des données dans la base de données
"""

from datetime import datetime
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
import yfinance as yf

from src.constants import *
from src.model import ETF, ETFPriceData
from src.repository import ETFRepository


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
                inception_date=pd.to_datetime(row.get(INCEPTION_DATE_COL)),
            )
            for _, row in df.iterrows()
        ]

    def fetch_price_data(
        self,
        ticker: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: str = DEFAULT_PERIOD,
        use_cache: bool = True,
    ) -> List[ETFPriceData]:
        """Récupère les données de prix depuis yfinance ou le cache."""
        # Vérifie d'abord dans la base de données si on utilise le cache
        if use_cache:
            cached_data = self.repository.get_price_data(ticker, start_date, end_date)
            if cached_data:
                return cached_data

        # Si pas dans le cache ou cache désactivé, récupère depuis yfinance
        try:
            etf = yf.Ticker(ticker)
            hist = etf.history(period=period, start=start_date, end=end_date)

            # Conversion en liste d'ETFPriceData
            price_data = [
                ETFPriceData(
                    ticker=ticker,
                    date=index,
                    adj_close=row["Close"],
                    volume=row["Volume"],
                )
                for index, row in hist.iterrows()
            ]

            # Sauvegarde dans le cache si activé
            if use_cache and price_data:
                self.repository.save_price_data(price_data)

            return price_data

        except Exception as e:
            raise ValueError(
                f"Erreur lors de la récupération des données pour {ticker}: {str(e)}"
            )

    def get_benchmark_data(
        self, benchmark_ticker: str = "SPY", period: str = DEFAULT_PERIOD
    ) -> List[ETFPriceData]:
        """Récupère les données de l'indice de référence."""
        return self.fetch_price_data(benchmark_ticker, period=period)

    def fetch_multiple_etfs_data(
        self,
        tickers: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: str = DEFAULT_PERIOD,
        use_cache: bool = True,
    ) -> Dict[str, List[ETFPriceData]]:
        """
        Récupère les données de prix pour plusieurs ETFs efficacement.

        Args:
            tickers: Liste des tickers ETF à récupérer
            start_date: Date de début optionnelle
            end_date: Date de fin optionnelle
            period: Période (par défaut '5y')
            use_cache: Utiliser le cache si disponible

        Returns:
            Dictionnaire avec les tickers comme clés et les listes de prix comme valeurs
        """
        # Vérifier d'abord le cache
        if use_cache:
            cached_data = {}
            missing_tickers = []
            for ticker in tickers:
                data = self.repository.get_price_data(ticker, start_date, end_date)
                if data:
                    cached_data[ticker] = data
                else:
                    missing_tickers.append(ticker)

            if not missing_tickers:
                return cached_data

            # Ne récupérer que les tickers manquants
            tickers = missing_tickers

        try:
            # Télécharger les données en une seule requête
            data = yf.download(
                tickers=" ".join(tickers),
                start=start_date,
                end=end_date,
                period=period,
                group_by="ticker",
                auto_adjust=True,
            )

            result = {}

            # Si un seul ticker, yf.download retourne un DataFrame simple
            if len(tickers) == 1:
                ticker = tickers[0]
                price_data = [
                    ETFPriceData(
                        ticker=ticker,
                        date=index,
                        adj_close=row["Close"],
                        volume=row["Volume"],
                    )
                    for index, row in data.iterrows()
                    if not pd.isna(row["Close"])
                ]
                if use_cache:
                    self.repository.save_price_data(price_data)
                result[ticker] = price_data

            # Sinon, c'est un DataFrame multi-index
            else:
                for ticker in tickers:
                    try:
                        ticker_data = data[ticker]
                        price_data = [
                            ETFPriceData(
                                ticker=ticker,
                                date=index,
                                adj_close=row["Close"],
                                volume=row["Volume"],
                            )
                            for index, row in ticker_data.iterrows()
                            if not pd.isna(row["Close"])
                        ]
                        if use_cache and price_data:
                            self.repository.save_price_data(price_data)
                        result[ticker] = price_data
                    except KeyError:
                        print(f"Avertissement: Données non trouvées pour {ticker}")
                        result[ticker] = []

            # Fusionner avec les données en cache si nécessaire
            if use_cache and cached_data:
                result.update(cached_data)

            return result

        except Exception as e:
            raise ValueError(f"Erreur lors de la récupération des données: {str(e)}")


def run_etl_pipeline():
    """Exécute le pipeline ETL complet."""
    print("Pipeline ETL démarré...")
    # À implémenter : logique du pipeline
    pass


if __name__ == "__main__":
    run_etl_pipeline()
    print("Pipeline ETL terminé.")
