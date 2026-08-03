from __future__ import annotations

from abc import ABC, abstractmethod

from apps.auth.domain.model.mobile_kakao_identity import KakaoIdentity


class IdTokenVerifierPort(ABC):

    @abstractmethod
    def verify(self, id_token: str, *, nonce: str) -> KakaoIdentity:
        """id_token의 서명·클레임을 검증하고 신원을 반환한다.

        실패 시 apps.auth.domain.exception.mobile_auth_exceptions의 하위 예외를 raise한다.
        """
