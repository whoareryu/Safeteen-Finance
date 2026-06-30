# 1. 파이썬 베이스 이미지 가져오기
FROM python:3.12.13-slim

# 2. 컨테이너 내부 작업 디렉토리 설정
WORKDIR /whoareryu

# 3. 리눅스 패키지 업데이트 및 필요한 기본 도구 설치 (알렘빅 등 빌드 오류 방지)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. 기본 의존성만 이미지에 설치 (빌드 캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. entrypoint 복사 및 실행 권한 부여
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 6. 나머지 코드 전체 복사
COPY . .

# 7. 시작 시 requirements.txt 변경분 자동 설치 후 uvicorn 실행
CMD ["/entrypoint.sh"]
