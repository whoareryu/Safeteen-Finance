from typing import Any

from apps.titanic.app.ports.input.titanic_query_port import TitanicQueryPort
from apps.titanic.app.ports.output.titanic_reader import TitanicReader
from apps.titanic.app.use_cases.service_use_case import JackService


class TitanicQueryUseCase(TitanicQueryPort):
    """타이타닉 조회 유스케이스 (기존 JamesController 역할)."""

    def __init__(self, reader: TitanicReader | None = None) -> None:
        self._reader: TitanicReader = reader or JackService()

    def get_data(self) -> dict[str, Any]:
        return self._reader.get_data()

    def get_count(self) -> int:
        return self._reader.get_count()

    def get_count_survived(self) -> int:
        return self._reader.get_count_survived()

    def get_count_dead(self) -> int:
        return self._reader.get_count_dead()

    def has_decision_tree_model(self) -> bool:
        return self._reader.has_decision_tree_model()

    def get_training_model_name(self) -> str:
        return self._reader.get_training_model_name()

    def get_training_model_accuracy(self) -> float:
        return self._reader.get_training_model_accuracy()
