import pandas as pd

class DoroReader:
    def __init__(self):
        pass

    
    def get_data(self):
        # 프로젝트 내부 파일(CSV)을 읽지 않도록 비활성화.
        # 필요한 경우 외부 업로드/DB/API로 데이터 소스를 연결해야 함.
        return pd.DataFrame()

