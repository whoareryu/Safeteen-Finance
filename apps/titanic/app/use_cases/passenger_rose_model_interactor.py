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

from titanic.adapter.inbound.api.schemas.passenger_rose_model_schema import RoseModelSchema
from titanic.app.dtos.passenger_rose_model_dto import RoseModelQuery, RoseModelResponse
from titanic.app.ports.input.passenger_rose_model_use_case import (
    RoseModelUseCase,
    SurvivalAlgorithmStrategy,
)
from titanic.app.ports.output.passenger_rose_model_repository import RoseModelRepository

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


# ──────────────────────────────────────────────
# 1. XGBoost  (없으면 GradientBoosting으로 대체)
# ──────────────────────────────────────────────
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


# ──────────────────────────────────────────────
# 2. Random Forest
# ──────────────────────────────────────────────
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


# ──────────────────────────────────────────────
# 3. LightGBM  (없으면 ExtraTrees로 대체)
# ──────────────────────────────────────────────
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


# ──────────────────────────────────────────────
# 4. CatBoost  (없으면 HistGradientBoosting으로 대체)
# ──────────────────────────────────────────────
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


# ──────────────────────────────────────────────
# 5. Logistic Regression  (표준화 포함)
# ──────────────────────────────────────────────
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


# ──────────────────────────────────────────────
# 6. Decision Tree
# ──────────────────────────────────────────────
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


# ──────────────────────────────────────────────
# 7. SVM  (표준화 필수)
# ──────────────────────────────────────────────
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


# ──────────────────────────────────────────────
# 8. KNN  (표준화 필수)
# ──────────────────────────────────────────────
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


# ──────────────────────────────────────────────
# 9. Naive Bayes
# ──────────────────────────────────────────────
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


# ──────────────────────────────────────────────
# 10. Ensemble + PCA  (PCA 차원 축소 → Soft Voting)
# ──────────────────────────────────────────────
class EnsemblePCAStrategy(SurvivalAlgorithmStrategy):
    """PCA로 차원을 축소한 뒤 Soft Voting 앙상블로 예측한다."""

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


# ──────────────────────────────────────────────
# Context: RoseModelInteractor
# ──────────────────────────────────────────────
class RoseModelInteractor(RoseModelUseCase):

    def __init__(
        self,
        repository: RoseModelRepository,
        strategy: SurvivalAlgorithmStrategy | None = None,
    ) -> None:
        self.repository = repository
        self._strategy: SurvivalAlgorithmStrategy = strategy or RandomForestStrategy()

    def set_strategy(self, strategy: SurvivalAlgorithmStrategy) -> None:
        """런타임에 알고리즘 전략을 교체한다."""
        self._strategy = strategy

    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """현재 전략으로 모델을 학습시킨다."""
        self._strategy.fit(X_train, y_train)

    def predict_survival(self, X: pd.DataFrame) -> list[int]:
        """현재 전략으로 생존 여부를 예측한다 (0=사망, 1=생존)."""
        return self._strategy.predict(X)

    async def introduce_myself(self, schema: list[RoseModelSchema]) -> RoseModelResponse:
        first = schema[0] if schema else RoseModelSchema()
        return await self.repository.introduce_myself(
            RoseModelQuery(id=first.id, name=first.name)
        )
