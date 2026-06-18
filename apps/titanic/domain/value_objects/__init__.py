from titanic.domain.value_objects.survived_vo import Survived
from titanic.domain.value_objects.age_vo import Age, AgeGroup

# 단일 VO (임베디드 타입의 구성 요소)
from titanic.domain.value_objects.gender_vo import Gender, GenderType
from titanic.domain.value_objects.title_vo import TitleVO
from titanic.domain.value_objects.pclass_vo import PClass, PClassType
from titanic.domain.value_objects.fare_vo import Fare
from titanic.domain.value_objects.ticket_vo import TicketNumber
from titanic.domain.value_objects.embarked_vo import Embarked, PortType

# 임베디드 값 타입 (연관 VO 묶음)
from titanic.domain.value_objects.passenger_identity_vo import PassengerIdentity
from titanic.domain.value_objects.economic_status_vo import EconomicStatus
from titanic.domain.value_objects.boarding_info_vo import BoardingInfo

__all__ = [
    # 독립 VO
    "Survived",
    "Age",
    "AgeGroup",
    # 단일 VO
    "Gender",
    "GenderType",
    "TitleVO",
    "PClass",
    "PClassType",
    "Fare",
    "TicketNumber",
    "Embarked",
    "PortType",
    # 임베디드 값 타입
    "PassengerIdentity",
    "EconomicStatus",
    "BoardingInfo",
]
