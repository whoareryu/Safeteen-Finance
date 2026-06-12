# 1. 파이썬 베이스 이미지 가져오기
FROM python:3.13-slim

# 2. 컨테이너 내부 작업 디렉토리 설정
WORKDIR /whoareryu

# 3. 리눅스 패키지 업데이트 및 필요한 기본 도구 설치 (알렘빅 등 빌드 오류 방지)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 나머지 코드 전체 복사
COPY . .

# 6. FastAPI (Uvicorn) 실행 명령 (8000포트 개방)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
