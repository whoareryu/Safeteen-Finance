from __future__ import annotations

import logging
import re

from titanic.app.dtos.crew_smith_captain_dto import (
    SmithCaptainResponse,
    SmithChatCommand,
    SmithChatResponse,
)
from titanic.app.ports.input.crew_andrews_architect_use_case import AndrewsArchitectUseCase
from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.ports.input.crew_lowe_boat_use_case import LoweBoatUseCase
from titanic.app.ports.input.crew_smith_captain_use_case import SmithCaptainUseCase
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterRoasterUseCase
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTesterUseCase
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import SmithCaptainSchema


logger = logging.getLogger(__name__)

# Hartley 분석 기준 survived 상관계수 (사전 계산값)
_CORRELATION_SUMMARY = [
    ("gender (성별)",       +0.54, "여성일수록 생존율 높음 — '여성과 어린이 먼저'"),
    ("title (호칭)",        +0.47, "Mrs·Miss·Master가 Mr보다 생존율 높음"),
    ("pclass (객실 등급)",  -0.34, "1등석(숫자 낮을수록) 생존율 높음"),
    ("fare (탑승 요금)",    +0.26, "고액 요금 승객일수록 생존율 높음"),
    ("ticket (티켓 유형)",  -0.20, "단독 탑승보다 그룹 탑승이 생존율 높음"),
    ("embarked (탑승 항구)",+0.11, "셰르부르(C) 승선객이 소폭 유리"),
    ("parch (부모/자녀)",   +0.08, "소가족 동반 시 소폭 유리"),
    ("age (나이)",          -0.06, "선형 상관은 낮음 — 어린이는 생존율 높음"),
]

_FEMALE_WORDS = frozenset({
    "여자", "여성", "여인", "딸", "엄마", "어머니", "아가씨", "부인", "여",
})


class SmithCaptainInteractor(SmithCaptainUseCase):

    def __init__(
        self,
        repository,
        andrews: AndrewsArchitectUseCase,
        rose: RoseModelUseCase,
        cal: CalTesterUseCase,
        walter: WalterRoasterUseCase,
        lowe: LoweBoatUseCase,
        jack: JackTrainerUseCase,
        hartley: HartleyViolinUseCase,
    ):
        self.repository = repository
        self.andrews = andrews
        self.rose = rose
        self.cal = cal
        self.walter = walter
        self.lowe = lowe
        self.jack = jack
        self.hartley = hartley

    # ── 공개 메서드 ───────────────────────────────────────────────────────────

    async def chat(self, command: SmithChatCommand) -> SmithChatResponse:
        question = command.message
        intent_result = self.andrews.analyze_intent(question)
        intent = intent_result["intent"]

        logger.info(
            f"[SmithCaptainInteractor] chat | intent={intent} question={question!r}"
        )

        if intent == "STATISTICS":
            reply = self._reply_statistics()
        elif intent == "SURVIVAL_PREDICT":
            reply = await self._reply_survival_predict(question)
        elif intent == "SURVIVOR_COUNT":
            reply = await self._reply_survivor_count()
        elif intent == "MODEL_TRAIN":
            reply = await self._reply_model_performance()
        elif intent == "SHIP_INFO":
            reply = self._reply_ship_info()
        elif intent == "COLLISION":
            reply = self._reply_collision()
        elif intent == "RESCUE":
            reply = self._reply_rescue()
        elif intent == "VOYAGE":
            reply = self._reply_voyage()
        elif intent == "PASSENGER_SEARCH":
            reply = await self._reply_passenger_search(question)
        else:
            reply = self._reply_unknown()

        return SmithChatResponse(reply=reply)

    async def introduce_myself(self, schema) -> SmithCaptainResponse:
        schema = SmithCaptainSchema(id=7, name="스미스 선장 (Captain Edward John Smith)")
        return SmithCaptainResponse(id=schema.id, name=schema.name)

    # ── 사설 응답 생성기 ──────────────────────────────────────────────────────

    def _reply_statistics(self) -> str:
        lines = ["[타이타닉 생존율 영향 요인 — survived 상관계수 순위]\n"]
        for i, (name, corr, desc) in enumerate(_CORRELATION_SUMMARY, 1):
            sign = "+" if corr >= 0 else ""
            lines.append(f"  {i}위. {name}: {sign}{corr:.2f}  — {desc}")
        lines.append("\n핵심: 성별(gender)과 호칭(title)이 생존에 가장 결정적입니다.")
        return "\n".join(lines)

    async def _reply_survival_predict(self, question: str) -> str:
        # 나이·성별 추출
        age_match = re.search(r"(\d{1,3})\s*세", question)
        age = int(age_match.group(1)) if age_match else 30
        gender = 1 if any(w in question for w in _FEMALE_WORDS) else 0
        gender_label = "여성" if gender == 1 else "남성"

        # 모델 학습 후 최우수 모델로 예측
        train_set = await self.walter.get_train_set()
        trained_result = await self.jack.train_model(train_set)
        tested_result = await self.cal.test_model(None)

        strategies = trained_result.get("trained_strategies", {})
        winner_name = tested_result.get("winner", "")
        strategy = strategies.get(winner_name) or next(iter(strategies.values()), None)

        if not strategy:
            return "모델 학습 데이터가 충분하지 않아 예측할 수 없습니다."

        # CalTesterInteractor._FEATURES = ["age", "sib_sp", "parch", "gender"]
        prediction = strategy.predict([[age, 0, 0, gender]])[0]
        result_label = "생존 가능성 높음" if prediction == 1 else "생존 가능성 낮음"

        return (
            f"[{age}세 {gender_label} 승객 타이타닉 생존 예측]\n\n"
            f"  결과: {result_label}\n"
            f"  사용 모델: {winner_name}  (정확도: {tested_result.get('winner_accuracy', '?')})\n\n"
            f"  참고: 성별(+0.54)·호칭(+0.47)·객실 등급(-0.34)이 생존에 가장 큰 영향을 미칩니다."
        )

    async def _reply_survivor_count(self) -> str:
        train_set = await self.walter.get_train_set()
        test_set = await self.walter.get_test_set()
        if train_set.empty:
            return "데이터가 없습니다. 먼저 타이타닉 데이터를 업로드해 주세요."

        # train(891) + test(418) = 1,309명 전체
        total = len(train_set) + len(test_set)
        survivors = int((train_set["survived"].astype(int) == 1).sum())
        deceased = int((train_set["survived"].astype(int) == 0).sum())
        unknown = len(test_set)
        rate = survivors / len(train_set) * 100

        return (
            f"[타이타닉 탑승·생존 통계]\n\n"
            f"  총 탑승 인원: {total:,}명\n"
            f"  생존자: {survivors:,}명\n"
            f"  사망자: {deceased:,}명\n"
            f"  생존 결과 미확인: {unknown:,}명\n"
            f"  생존율 (확인 기준): {rate:.1f}%"
        )

    async def _reply_model_performance(self) -> str:
        tested_result = await self.cal.test_model(None)

        if "error" in tested_result:
            return f"모델 평가 실패: {tested_result['error']}"

        winner = tested_result.get("winner", "")
        winner_acc = tested_result.get("winner_accuracy", "?")
        rankings = tested_result.get("rankings", [])

        lines = [f"[모델 성능 평가 결과]\n", f"  최우수 모델: {winner}  (정확도: {winner_acc})\n"]
        for r in rankings:
            lines.append(f"  {r['rank']}위. {r['model']}: {r['accuracy']}")
        return "\n".join(lines)

    @staticmethod
    def _reply_ship_info() -> str:
        return (
            "RMS 타이타닉은 영국 화이트스타라인(White Star Line) 소속의 초호화 여객선입니다.\n\n"
            "  건조지: 아일랜드 벨파스트 할랜드앤울프 조선소\n"
            "  취항일: 1912년 4월 10일 (처녀항해)\n"
            "  전장: 269m  /  폭: 28m  /  높이: 53m\n"
            "  총톤수: 46,328톤\n"
            "  최대 속도: 23노트 (약 43km/h)\n"
            "  객실 등급: 1등실 · 2등실 · 3등실(스티어리지)\n"
            "  설계자: 토마스 앤드류스 (Thomas Andrews)\n"
            "  선장: 에드워드 존 스미스 — 바로 저입니다.\n\n"
            "당시 세계 최대의 여객선으로, '절대 침몰하지 않는 배'로 불렸습니다."
        )

    @staticmethod
    def _reply_collision() -> str:
        return (
            "1912년 4월 14일 밤 11시 40분(선박 시각), 북대서양에서 빙산과 충돌했습니다.\n\n"
            "  충돌 위치: 북위 41°46′, 서경 50°14′\n"
            "  기온: 영하 2°C  /  해수온: 영하 2°C\n"
            "  충돌 각도: 우현 선체를 비스듬히 긁으며 5개 격벽 파손\n"
            "  침몰 소요 시간: 충돌 후 약 2시간 40분\n"
            "  침몰 완료: 4월 15일 오전 2시 20분\n\n"
            "설계상 4개 격벽까지만 침수를 버틸 수 있었습니다.\n"
            "5번째 격벽이 파손되면서 침몰은 불가피했습니다."
        )

    @staticmethod
    def _reply_rescue() -> str:
        return (
            "타이타닉에는 총 20척의 구명보트가 탑재되어 있었습니다.\n\n"
            "  구명보트 정원: 약 1,178명 (전체 탑승객의 절반 수준)\n"
            "  실제 구조 인원: 710명\n"
            "  구조선: RMS 카르파티아(Carpathia)\n"
            "  카르파티아 도착: 침몰 약 1시간 40분 후 (오전 4시 10분)\n"
            "  구조 완료: 4월 15일 오전 8시 30분\n\n"
            "많은 구명보트가 정원을 채우지 못한 채 출발했습니다.\n"
            "당시 '여성과 어린이 먼저' 원칙이 적용되어 여성·어린이 생존율이 높았습니다."
        )

    @staticmethod
    def _reply_voyage() -> str:
        return (
            "타이타닉의 처녀항해(Maiden Voyage) 정보입니다.\n\n"
            "  출발일: 1912년 4월 10일\n"
            "  출발지: 영국 사우샘프턴(Southampton)\n"
            "  경유지: 프랑스 셰르부르(Cherbourg) → 아일랜드 퀸즈타운(Queenstown)\n"
            "  목적지: 미국 뉴욕\n"
            "  운항 속도: 평균 21노트 (최대 23노트 목표)\n"
            "  예정 도착일: 4월 17일 (침몰로 미도착)\n\n"
            "총 탑승 인원은 승객·승무원 합산 약 2,224명이었습니다."
        )

    async def _reply_passenger_search(self, question: str) -> str:
        import pandas as pd
        train_set = await self.walter.get_train_set()
        test_set = await self.walter.get_test_set()
        cols = ["name", "age", "gender", "survived"]
        frames = []
        if not train_set.empty:
            frames.append(train_set[cols])
        if not test_set.empty:
            frames.append(test_set[cols])
        if not frames:
            return "데이터가 없습니다. 먼저 타이타닉 데이터를 업로드해 주세요."
        all_data = pd.concat(frames, ignore_index=True)
        all_data["age"] = pd.to_numeric(all_data["age"], errors="coerce")
        aged = all_data.dropna(subset=["age"]).copy()
        if aged.empty:
            return "나이 정보가 있는 승객 데이터가 없습니다."

        _YOUNGEST_WORDS = frozenset({"어리", "젊", "최소", "아기", "어린이", "아이", "최저"})
        youngest = any(w in question for w in _YOUNGEST_WORDS)

        if youngest:
            top = aged.nsmallest(3, "age")
            label = "가장 어린"
        else:
            top = aged.nlargest(3, "age")
            label = "나이가 가장 많은"

        lines = [f"[타이타닉 탑승객 — {label} 승객 TOP 3]\n"]
        for i, (_, row) in enumerate(top.iterrows(), 1):
            survived_label = (
                "생존" if str(row.get("survived", "")) == "1"
                else "사망" if str(row.get("survived", "")) == "0"
                else "미확인"
            )
            gender_label = "여성" if str(row.get("gender", "")) == "female" else "남성"
            lines.append(
                f"  {i}위. {row['name']}  "
                f"({int(row['age'])}세, {gender_label}, {survived_label})"
            )
        return "\n".join(lines)

    @staticmethod
    def _reply_unknown() -> str:
        return (
            "저는 RMS 타이타닉의 선장 에드워드 존 스미스입니다.\n"
            "다음 주제에 대해 답변드릴 수 있습니다.\n\n"
            "  🚢 배 정보     — '타이타닉은 어떤 배인가요?'\n"
            "  🧊 침몰 사고   — '빙산과 충돌한 날 무슨 일이 있었나요?'\n"
            "  🛟 구조 현황   — '승객들은 어떻게 구조됐나요?'\n"
            "  ⚓ 항해 정보   — '타이타닉의 속도는 얼마였나요?'\n"
            "  📊 생존 통계   — '생존자는 총 몇명이에요?'\n"
            "  📈 생존율 분석 — '생존율에 중요한 요소가 뭔가요?'\n"
            "  🔮 생존 예측   — '33세 남자라면 살 수 있었을까요?'"
        )
