from pathlib import Path

import pandas as pd

from apps.titanic.app.ports.output.titanic_reader import TitanicReader


class ReaderUseCase:
    """Reader Use Case."""

    def __init__(self) -> None:
        pass

    def read_data(self) -> pd.DataFrame:
        return pd.DataFrame()
    
    def get_data(self) -> dict:
        return {}
    
    def get_count(self) -> int:
        return 0
    
    def get_count_survived(self) -> int:
        return 0
    
    def get_count_dead(self) -> int:
        return 0
    
    def has_decision_tree_model(self) -> bool:
        return False
    
    def get_training_model_name(self) -> str:
        return ""
    
    def get_training_model_accuracy(self) -> float:
        return 0.0

