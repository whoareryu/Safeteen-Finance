from dataclasses import dataclass, field


@dataclass
class DispatchRequestDto:
    task: str
    payload: dict = field(default_factory=dict)


@dataclass
class DispatchResultDto:
    task_type: str
    routed_to: str
    result: dict
