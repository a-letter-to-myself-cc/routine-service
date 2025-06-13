# service.py
import requests

#쿠버네티스버전
AUTH_SERVICE_URL = "http://auth-service:8001/api/auth"

#로컬버전
#AUTH_SERVICE_URL = "http://localhost:8001/auth"

def verify_access_token(token):
    try:
        print("🛠 routine-service가 auth-service에 보낼 토큰:", token)  # 디버깅 로그

        response = requests.post(f"{AUTH_SERVICE_URL}/internal/verify/", json={"token": token})
        if response.status_code == 200:
            user_id = response.json()['user_id']
            print("✅ auth-service로부터 받은 user_id:", user_id)  # 디버깅 로그
            return user_id
        else:
            try:
                return_detail = response.json().get('detail', response.text)
            except Exception:
                return_detail = response.text
            raise Exception(f"Token verification failed: {return_detail}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Auth service connection failed: {str(e)}")
