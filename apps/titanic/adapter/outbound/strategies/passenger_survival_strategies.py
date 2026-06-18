from __future__ import annotations

import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import (
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
    ExtraTreesClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from titanic.app.ports.input.passenger_rose_model_use_case import SurvivalAlgorithmStrategy

try:
    from xgboost import XGBClassifier as _XGBClassifier
    _XGBOOST = True
except ImportError:
    _XGBOOST = False

try:
    from lightgbm import LGBMClassifier as _LGBMClassifier
    _LIGHTGBM = True
except ImportError:
    _LIGHTGBM = False

try:
    from catboost import CatBoostClassifier as _CatBoostClassifier
    _CATBOOST = True
except ImportError:
    _CATBOOST = False


class XGBoostStrategy(SurvivalAlgorithmStrategy):
    def __init__(self) -> None:
        self._model = (
            _XGBClassifier(n_estimators=100, random_state=42, eval_metric="logloss")
            if _XGBOOST
            else GradientBoostingClassifier(n_estimators=100, random_state=42)
        )

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        self._model.fit(X_train, y_train)

    def predict(self, X: pd.DataFrame) -> list[int]:
        return self._model.predict(X).tolist()

    @property
    def name(self) -> str:
        return "XGBoost" if _XGBOOST else "GradientBoosting (XGBoost fallback)"


class RandomForestStrategy(SurvivalAlgorithmStrategy):
    def __init__(self) -> None:
        self._model = RandomForestClassifier(n_estimators=100, random_state=42)

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        self._model.fit(X_train, y_train)

    def predict(self, X: pd.DataFrame) -> list[int]:
        return self._model.predict(X).tolist()

    @property
    def name(self) -> str:
        return "Random Forest"


class LightGBMStrategy(SurvivalAlgorithmStrategy):
    def __init__(self) -> None:
        self._model = (
            _LGBMClassifier(n_estimators=100, random_state=42, verbose=-1)
            if _LIGHTGBM
            else ExtraTreesClassifier(n_estimators=100, random_state=42)
        )

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        self._model.fit(X_train, y_train)

    def predict(self, X: pd.DataFrame) -> list[int]:
        return self._model.predict(X).tolist()

    @property
    def name(self) -> str:
        return "LightGBM" if _LIGHTGBM else "ExtraTrees (LightGBM fallback)"


class CatBoostStrategy(SurvivalAlgorithmStrategy):
    def __init__(self) -> None:
        self._model = (
            _CatBoostClassifier(iterations=100, random_seed=42, verbose=False)
            if _CATBOOST
            else HistGradientBoostingClassifier(max_iter=100, random_state=42)
        )

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        self._model.fit(X_train, y_train)

    def predict(self, X: pd.DataFrame) -> list[int]:
        return self._model.predict(X).tolist()

    @property
    def name(self) -> str:
        return "CatBoost" if _CATBOOST else "HistGradientBoosting (CatBoost fallback)"


class LogisticRegressionStrategy(SurvivalAlgorithmStrategy):
    def __init__(self) -> None:
        self._model = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, random_state=42)),
        ])

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        self._model.fit(X_train, y_train)

    def predict(self, X: pd.DataFrame) -> list[int]:
        return self._model.predict(X).tolist()

    @property
    def name(self) -> str:
        return "Logistic Regression"


class DecisionTreeStrategy(SurvivalAlgorithmStrategy):
    def __init__(self, max_depth: int = 5) -> None:
        self._model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        self._model.fit(X_train, y_train)

    def predict(self, X: pd.DataFrame) -> list[int]:
        return self._model.predict(X).tolist()

    @property
    def name(self) -> str:
        return "Decision Tree"


class SVMStrategy(SurvivalAlgorithmStrategy):
    def __init__(self) -> None:
        self._model = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", SVC(kernel="rbf", probability=True, random_state=42)),
        ])

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        self._model.fit(X_train, y_train)

    def predict(self, X: pd.DataFrame) -> list[int]:
        return self._model.predict(X).tolist()

    @property
    def name(self) -> str:
        return "SVM"


class KNNStrategy(SurvivalAlgorithmStrategy):
    def __init__(self, n_neighbors: int = 5) -> None:
        self._model = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", KNeighborsClassifier(n_neighbors=n_neighbors)),
        ])

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        self._model.fit(X_train, y_train)

    def predict(self, X: pd.DataFrame) -> list[int]:
        return self._model.predict(X).tolist()

    @property
    def name(self) -> str:
        return "KNN"


class NaiveBayesStrategy(SurvivalAlgorithmStrategy):
    def __init__(self) -> None:
        self._model = GaussianNB()

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        self._model.fit(X_train, y_train)

    def predict(self, X: pd.DataFrame) -> list[int]:
        return self._model.predict(X).tolist()

    @property
    def name(self) -> str:
        return "Naive Bayes"


class EnsemblePCAStrategy(SurvivalAlgorithmStrategy):
    def __init__(self, n_components: float = 0.95) -> None:
        estimators = [
            ("lr", LogisticRegression(max_iter=1000, random_state=42)),
            ("rf", RandomForestClassifier(n_estimators=100, random_state=42)),
            ("gb", GradientBoostingClassifier(n_estimators=100, random_state=42)),
        ]
        self._model = Pipeline([
            ("scaler", StandardScaler()),
            ("pca", PCA(n_components=n_components)),
            ("clf", VotingClassifier(estimators=estimators, voting="soft")),
        ])

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        self._model.fit(X_train, y_train)

    def predict(self, X: pd.DataFrame) -> list[int]:
        return self._model.predict(X).tolist()

    @property
    def name(self) -> str:
        return "Ensemble + PCA (Soft Voting)"


ALL_STRATEGIES: list[type[SurvivalAlgorithmStrategy]] = [
    XGBoostStrategy,
    RandomForestStrategy,
    LightGBMStrategy,
    CatBoostStrategy,
    LogisticRegressionStrategy,
    DecisionTreeStrategy,
    SVMStrategy,
    KNNStrategy,
    NaiveBayesStrategy,
    EnsemblePCAStrategy,
]
