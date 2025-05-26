"""
Module pour la gestion de la persistance des données.
Interactions avec la base de données SQLite.
"""
from typing import List, Optional
from datetime import datetime
import sqlite3

from .model import ETF, ETFPriceData
from .constants import *


class ETFRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialise la base de données avec les tables nécessaires."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
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
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS price_data (
                    ticker TEXT,
                    date TEXT,
                    adj_close REAL NOT NULL,
                    volume INTEGER,
                    PRIMARY KEY (ticker, date),
                    FOREIGN KEY (ticker) REFERENCES etfs (ticker)
                )
            ''')
            conn.commit()
    
    def save_etf(self, etf: ETF) -> None:
        """Sauvegarde ou met à jour un ETF dans la base de données."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO etfs 
                (ticker, name, issuer, ter, inception_date, category, 
                assets_under_management, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                etf.ticker,
                etf.name,
                etf.issuer,
                etf.ter,
                etf.inception_date.isoformat() if etf.inception_date else None,
                etf.category,
                etf.assets_under_management,
                etf.description
            ))
            conn.commit()
    
    def get_etf(self, ticker: str) -> Optional[ETF]:
        """Récupère un ETF par son ticker."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT * FROM etfs WHERE ticker = ?',
                (ticker,)
            )
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
                description=row[7]
            )
    
    def save_price_data(self, price_data: List[ETFPriceData]) -> None:
        """Sauvegarde les données de prix dans la base de données."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany('''
                INSERT OR REPLACE INTO price_data 
                (ticker, date, adj_close, volume)
                VALUES (?, ?, ?, ?)
            ''', [
                (
                    data.ticker,
                    data.date.isoformat(),
                    data.adj_close,
                    data.volume
                )
                for data in price_data
            ])
            conn.commit()
