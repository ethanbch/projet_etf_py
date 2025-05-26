"""
Point d'entrée principal de l'application ETF Comparator.
"""

import os
from pathlib import Path

import pandas as pd
import streamlit as st

from src.etl import ETFDataLoader
from src.helpers_files import load_yaml_config
from src.repository import ETFRepository
from src.view import ETFDashboard


def main():
    # Initialisation de Streamlit
    st.set_page_config(
        page_title="ETF Performance Comparator", page_icon="📈", layout="wide"
    )

    # Chargement de la configuration
    config = load_yaml_config("src/config.yaml")

    # Initialisation du repository
    db_path = config["database"]["path"]
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    repository = ETFRepository(db_path)

    # Initialisation du data loader
    data_loader = ETFDataLoader(repository)

    # Interface utilisateur de base
    st.title("📈 Comparateur de Performance d'ETFs Thématiques")
    st.markdown(
        """
    Cette application permet de comparer les performances d'ETFs thématiques.
    Sélectionnez les ETFs que vous souhaitez analyser dans la liste ci-dessous.
    """
    )

    # Chargement et affichage des métadonnées des ETFs
    try:
        etf_metadata = data_loader.load_etf_metadata(
            config["data_sources"]["etf_metadata_csv"]
        )

        # Création d'un DataFrame pour l'affichage
        etf_data = [
            {
                "Ticker": etf.ticker,
                "Nom": etf.name,
                "Émetteur": etf.issuer,
                "TER (%)": f"{etf.ter * 100:.2f}%",
                "Date de création": etf.inception_date.strftime("%Y-%m-%d"),
                "Catégorie": etf.category,
            }
            for etf in etf_metadata
        ]

        # Sélecteurs pour les ETFs
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.write("### Sélection des ETFs")
            all_tickers = [etf.ticker for etf in etf_metadata]
            base_etf = st.selectbox(
                "ETF de référence",
                all_tickers,
                format_func=lambda x: f"{x} - {next(etf.name for etf in etf_metadata if etf.ticker == x)}",
            )

            comparison_etfs = st.multiselect(
                "ETFs à comparer",
                [t for t in all_tickers if t != base_etf],
                format_func=lambda x: f"{x} - {next(etf.name for etf in etf_metadata if etf.ticker == x)}",
            )

        with col2:
            st.write("### Période d'analyse")
            period = st.selectbox(
                "Période", ["1mo", "3mo", "6mo", "1y", "3y", "5y", "max"], index=3
            )

        with col3:
            st.write("### Paramètres")
            risk_free_rate = (
                st.number_input(
                    "Taux sans risque (%)",
                    min_value=0.0,
                    max_value=10.0,
                    value=1.0,
                    step=0.1,
                )
                / 100
            )

        if st.button("Analyser") and base_etf and comparison_etfs:
            with st.spinner("Récupération des données..."):
                # Récupération des données de prix
                base_prices = data_loader.fetch_price_data(base_etf, period=period)
                comparison_prices = {
                    ticker: data_loader.fetch_price_data(ticker, period=period)
                    for ticker in comparison_etfs
                }

                # Création du dashboard
                dashboard = ETFDashboard()
                dashboard.display_comparison(
                    base_etf=next(
                        etf for etf in etf_metadata if etf.ticker == base_etf
                    ),
                    comparison_etfs=[
                        next(etf for etf in etf_metadata if etf.ticker == ticker)
                        for ticker in comparison_etfs
                    ],
                    base_prices=base_prices,
                    comparison_prices=comparison_prices,
                    risk_free_rate=risk_free_rate,
                )

        else:
            st.info(
                "Sélectionnez un ETF de référence et au moins un ETF à comparer, puis cliquez sur Analyser."
            )

            # Affichage du tableau des ETFs disponibles
            st.write("### ETFs disponibles")
            st.dataframe(etf_data)

    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")


if __name__ == "__main__":
    main()
