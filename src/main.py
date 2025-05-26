"""
Point d'entrée principal de l'application ETF Comparator.
"""
import streamlit as st
from pathlib import Path
import os

from .helpers_files import load_yaml_config
from .repository import ETFRepository
from .etl import ETFDataLoader
from .view import ETFDashboard


def main():
    # Chargement de la configuration
    config = load_yaml_config('src/config.yaml')
    
    # Initialisation du repository
    db_path = config['database']['path']
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    repository = ETFRepository(db_path)
    
    # Initialisation du data loader
    data_loader = ETFDataLoader(repository)
    
    # Lancement du dashboard
    dashboard = ETFDashboard()
    dashboard.run()


if __name__ == '__main__':
    main()
