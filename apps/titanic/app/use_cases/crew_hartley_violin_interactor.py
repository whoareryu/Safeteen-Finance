from __future__ import annotations

import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns

from titanic.adapter.inbound.api.schemas.crew_hartley_violin_schema import HartleyViolinSchema
from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinQuery, HartleyViolinResponse
from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.ports.output.crew_hartley_violin_port import HartleyViolinPort


class HartleyViolinInteractor(HartleyViolinUseCase):

    def __init__(self, repository: HartleyViolinPort):
        self.repository = repository

    async def introduce_myself(self, schema) -> HartleyViolinResponse:
        schema = HartleyViolinSchema(id=3, name="왈리스 하틀리 (Wallace Hartley)")
        return HartleyViolinResponse(id=schema.id, name=schema.name)

    # ── 내부 유틸 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _build_corr(df: pd.DataFrame) -> pd.DataFrame:
        """VO 기준 11개 피처로 인코딩 후 상관계수 행렬을 반환한다.

        VO 인코딩 규칙:
          gender  : GenderVO  — male=0, female=1
          cabin   : CabinVO   — deck 알파벳 순(A=1..G=7), 미배정=0
          embarked: EmbarkedVO — S=1, C=2, Q=3
          title   : TitleVO   — 실데이터: TitleVO.encode_series(df["Name"])
                                seaborn proxy: who(man=1, woman=2, child=3)
          ticket  : TicketVO  — 실데이터: prefix 있음=1, 없음=0
                                seaborn proxy: alone(단독=1, 동반=0)
        """
        d = df.copy()
        d["gender"]   = d["sex"].map({"male": 0, "female": 1})
        d["cabin"]    = d["deck"].astype(str).map(
                            {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "nan": 0}
                        )
        d["embarked"] = d["embarked"].fillna("S").map({"S": 1, "C": 2, "Q": 3})
        d["age"]      = d["age"].fillna(d["age"].median())
        d["fare"]     = d["fare"].fillna(d["fare"].median())
        d["title"]    = d["who"].map({"man": 1, "woman": 2, "child": 3})
        d["ticket"]   = d["alone"].astype(int)
        cols = ["survived", "pclass", "gender", "age", "sibsp", "parch",
                "fare", "cabin", "embarked", "ticket", "title"]
        return d[cols].corr()

    # ── 공개 메서드 ───────────────────────────────────────────────────────────

    def get_correlation_heatmap(self, df: pd.DataFrame) -> bytes:
        corr = self._build_corr(df)
        fig, ax = plt.subplots(figsize=(13, 11))
        sns.heatmap(
            corr,
            annot=True,
            cmap="coolwarm",
            fmt=".2f",
            linewidths=0.5,
            vmin=-1, vmax=1,
            ax=ax,
        )
        ax.set_title("Titanic Feature Correlation Heatmap (11 Features)")
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=130)
        buf.seek(0)
        plt.close(fig)
        return buf.read()

    def get_correlation_chart(self, df: pd.DataFrame) -> dict:
        corr = self._build_corr(df)
        fig = px.imshow(
            corr,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            title="Titanic Feature Correlation (11 Features)",
        )
        return fig.to_dict()
