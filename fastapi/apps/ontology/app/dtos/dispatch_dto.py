from dataclasses import dataclass, field


@dataclass
class DispatchRequestDto:
    task: str
    payload: dict = field(default_factory=dict)
    owner_session: str | None = None


@dataclass
class DispatchResultDto:
    task_type: str
    routed_to: str
    result: dict
