"""
Module pour la gestion de la persistance des données.
Interactions avec la base de données SQLite.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional

from src.constants import *
from src.model import ETF, ETFPriceData


class ETFRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialise la base de données avec les tables nécessaires."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS etfs (
                    ticker TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    issuer TEXT,
                    ter REAL,
                    inception_date TEXT,
                    category TEXT,
                    assets_under_management REAL,
                    description TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS price_data (
                    ticker TEXT,
                    date TEXT,
                    adj_close REAL NOT NULL,
                    volume INTEGER,
                    PRIMARY KEY (ticker, date),
                    FOREIGN KEY (ticker) REFERENCES etfs (ticker)
                )
            """
            )
            conn.commit()

    def save_etf(self, etf: ETF) -> None:
        """Sauvegarde ou met à jour un ETF dans la base de données."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO etfs 
                (ticker, name, issuer, ter, inception_date, category, 
                assets_under_management, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    etf.ticker,
                    etf.name,
                    etf.issuer,
                    etf.ter,
                    etf.inception_date.isoformat() if etf.inception_date else None,
                    etf.category,
                    etf.assets_under_management,
                    etf.description,
                ),
            )
            conn.commit()

    def get_etf(self, ticker: str) -> Optional[ETF]:
        """Récupère un ETF par son ticker."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM etfs WHERE ticker = ?", (ticker,))
            row = cursor.fetchone()

            if row is None:
                return None

            return ETF(
                ticker=row[0],
                name=row[1],
                issuer=row[2],
                ter=row[3],
                inception_date=datetime.fromisoformat(row[4]) if row[4] else None,
                category=row[5],
                assets_under_management=row[6],
                description=row[7],
            )

    def save_price_data(self, price_data: List[ETFPriceData]) -> None:
        """Sauvegarde les données de prix dans la base de données."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO price_data 
                (ticker, date, adj_close, volume)
                VALUES (?, ?, ?, ?)
            """,
                [
                    (data.ticker, data.date.isoformat(), data.adj_close, data.volume)
                    for data in price_data
                ],
            )
            conn.commit()

    def get_price_data(
        self,
        ticker: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[ETFPriceData]:
        """Récupère les données de prix pour un ETF avec filtrage par date."""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM price_data WHERE ticker = ?"
            params = [ticker]

            if start_date:
                query += " AND date >= ?"
                params.append(start_date.isoformat())
            if end_date:
                query += " AND date <= ?"
                params.append(end_date.isoformat())

            query += " ORDER BY date"

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            return [
                ETFPriceData(
                    ticker=row[0],
                    date=datetime.fromisoformat(row[1]),
                    adj_close=row[2],
                    volume=row[3],
                )
                for row in rows
            ]

    def clear_price_data(self, ticker: str) -> None:
        """Supprime les données de prix pour un ETF."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM price_data WHERE ticker = ?", (ticker,))
            conn.commit()
