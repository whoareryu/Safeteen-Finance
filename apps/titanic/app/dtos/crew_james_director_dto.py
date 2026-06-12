from dataclasses import dataclass


@dataclass
class PassengerCommand:
    passenger_id: str
    name: str
    gender: str
    age: str
    sib_sp: str
    parch: str
    survived: str


@dataclass
class BookingCommand:
    pclass: str
    ticket: str
    fare: str
    cabin: str
    embarked: str

@dataclass
class JamesDirectorResponse:
    answer: str
    
    
@dataclass
class JamesDirectorQuery:
    id: int
    name: str


# pg_repository 호환 alias
JamesIntroduceQuery = JamesDirectorQuery


@dataclass
class JamesIntroduceResponse:
    id: int
    name: str


# pg_repository 호환 alias (외부에서 PassengerCommand 로 rename 전)
PersonCommand = PassengerCommand
