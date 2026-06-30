from dataclasses import dataclass, field


@dataclass
class GraphQueryDto:
    cypher: str
    params: dict = field(default_factory=dict)


@dataclass
class GraphResultDto:
    records: list[dict]
