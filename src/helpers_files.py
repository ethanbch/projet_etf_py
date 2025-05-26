"""
Module pour la gestion des fichiers et des chemins.
"""

import os
from pathlib import Path
from typing import Any, Dict

import yaml


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """Charge un fichier de configuration YAML."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def ensure_directory_exists(directory_path: str) -> None:
    """S'assure qu'un répertoire existe, le crée si nécessaire."""
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def get_output_filename(base_name: str, extension: str, timestamp: bool = True) -> str:
    """Génère un nom de fichier pour la sortie avec timestamp optionnel."""
    from datetime import datetime

    if timestamp:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp_str}.{extension}"
    return f"{base_name}.{extension}"
