# python:latest 대신 버전 고정 (빌드 시점마다 결과가 달라지지 않도록)
FROM python:3.12-slim

# cron, 시간대 데이터 설치
RUN apt-get update \
    && apt-get install -y --no-install-recommends cron tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /project

# 의존성을 먼저 설치해 코드 변경 시 레이어 캐시 재사용
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./project/ /project/

# bash로 실행: 볼륨 마운트로 실행 비트가 사라져도 동작
CMD ["bash", "/project/entrypoint.sh"]
