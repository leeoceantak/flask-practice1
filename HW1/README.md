# HW1

Flask 과제를 작성할 기본 구조입니다. 세부 과제 기능은 아직 구현하지 않았습니다.

## 폴더 구성

- `app.py`: 과제용 Flask 앱
- `templates/`: 과제용 HTML 템플릿
- `README.md`: 과제 설명과 실행 방법

가상환경 `venv/`와 `requirements.txt`는 상위 `flask-practice1/` 폴더의 것을 함께 사용합니다.
상위 폴더의 `app.py`와 `templates/`는 수업 실습용입니다.

## 실행 방법

Windows PowerShell에서 `flask-practice1` 폴더를 기준으로 실행합니다.

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe HW1\app.py
```

브라우저에서 http://127.0.0.1:5000 에 접속합니다.
다른 실습 서버가 5000번 포트를 사용 중이면 먼저 종료합니다.
