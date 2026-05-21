import pandas as pd
from pathlib import Path

_CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "Titanic-Dataset.csv"

class WalterReader:
    def __init__(self):
        pass

    def get_data(self):
        df = pd.read_csv(_CSV_PATH)
        #인덱스 1번 행만 반환 (DataFrame 형태 유지)
        return df.iloc[[0]].astype(object).where(df.iloc[[0]].notna(), None)

    def get_count(self):
        df = pd.read_csv(_CSV_PATH)
        # CSV의 전체 행 수(=전체 승객 수) 반환
        return int(len(df))

    def get_count_survived(self):
        df = pd.read_csv(_CSV_PATH)
        # 생존자 수 반환
        return int((df["Survived"] == 1).sum())

    def get_count_dead(self):
        df = pd.read_csv(_CSV_PATH)
        # 사망자 수 반환
        return int((df["Survived"] == 0).sum())

    def get_full_dataframe(self):
        """모델 학습·평가용 전체 데이터."""
        return pd.read_csv(_CSV_PATH)
