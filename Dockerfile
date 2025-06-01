FROM python:3.11-slim

WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 환경 변수 설정을 위한 build arguments
ARG DB_NAME
ARG DB_USER
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_PORT
ARG SECRET_KEY

# 런타임 환경 변수 설정
ENV DB_NAME=$DB_NAME \
    DB_USER=$DB_USER \
    DB_PASSWORD=$DB_PASSWORD \
    DB_HOST=$DB_HOST \
    DB_PORT=$DB_PORT \
    SECRET_KEY=$SECRET_KEY

# 포트 노출
EXPOSE 8000

# Django 서버 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]