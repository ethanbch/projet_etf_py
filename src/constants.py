"""
Constants utilisées dans le projet ETF Comparator.
"""

# Colonnes des fichiers CSV
TICKER_COL = "ticker"
NAME_COL = "name"
ISSUER_COL = "issuer"
TER_COL = "ter"
INCEPTION_DATE_COL = "inception_date"

# Colonnes des données de prix
DATE_COL = "date"
ADJ_CLOSE_COL = "adj_close"
VOLUME_COL = "volume"

# Paramètres d'analyse
DEFAULT_PERIOD = "5y"
DEFAULT_INTERVAL = "1d"

# Messages d'erreur
ERR_DATA_NOT_FOUND = "Données non trouvées pour le ticker {}"
ERR_INVALID_DATE = "Format de date invalide : {}"
