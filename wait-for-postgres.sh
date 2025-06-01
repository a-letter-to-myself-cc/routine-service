```bash
#!/bin/sh

# 데이터베이스 연결 정보
DB_HOST="db"
DB_PORT="5432"
DB_USER="your_db_user"
DB_PASSWORD="your_db_password"

# PostgreSQL 서버가 준비될 때까지 대기
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"
do
  echo "PostgreSQL 서버 준비 중... 잠시 후 다시 시도합니다."
  sleep 2
done

echo "PostgreSQL 서버가 준비되었습니다."
# 나머지 초기화 스크립트 계속...
```

위의 스크립트에서 `your_db_user`와 `your_db_password`를 실제 데이터베이스 사용자 이름과 비밀번호로 바꾸어야 합니다. 이 스크립트는 PostgreSQL 서버가 준비될 때까지 대기한 후, 준비가 완료되면 다음 초기화 작업을 계속 진행할 수 있도록 합니다.