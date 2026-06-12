# 1. Node.js 베이스 이미지 가져오기
FROM node:24.15.0-alpine

# 2. 컨테이너 내부 작업 디렉토리 설정
WORKDIR /app

# 3. 패키지 설치를 위해 파일 복사
COPY package.json package-lock.json* ./

# 4. 의존성 설치
RUN npm install

# 5. 소스 코드 전체 복사
COPY . .

# 6. Next.js 개발 서버 실행 (3000포트 개방)
CMD ["npm", "run", "dev"]
