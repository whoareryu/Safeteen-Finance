from dataclasses import dataclass


@dataclass
class EmailTaskDto:
    to: str
    subject: str
    body: str
