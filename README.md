# Backend API

## 로컬 실행 (포트 8000)

프로젝트 루트가 아니라 **`backend` 폴더**에서 실행합니다.

```powershell
cd C:\Users\hi\Documents\com.ragwatson\backend
python main.py
```

또는:

```powershell
cd C:\Users\hi\Documents\com.ragwatson\backend
uvicorn main:app --host 127.0.0.1 --port 8000
```

- API 문서: http://127.0.0.1:8000/docs
- 환경 변수: `backend/.env` (`DATABASE_URL`, `GEMINI_API_KEY` 등)

`backend/apps` 에서는 `main.py`가 없습니다. 반드시 `backend` 로 이동한 뒤 실행하세요.
