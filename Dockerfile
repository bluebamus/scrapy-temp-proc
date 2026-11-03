# Python 3.15 이상. 3.15-slim 태그는 빌드 시점의 최신 3.15.x 패치를 받는다
# (새 패치 반영: docker compose build --pull / 상위 버전: PYTHON_VERSION=3.16 처럼 지정)
ARG PYTHON_VERSION=3.15
FROM python:${PYTHON_VERSION}-slim

# 3.15 미만 이미지로 빌드되면 여기서 실패시킨다
RUN python -c "import sys; assert sys.version_info >= (3, 15), 'Python 3.15+ required, got ' + sys.version"

# cron, 시간대 데이터 설치
RUN apt-get update \
    && apt-get install -y --no-install-recommends cron tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /project

# root 로 도는 컨테이너가 바인드 마운트된 소스에 root 소유 __pycache__ 를 남기지 않도록
ENV PYTHONDONTWRITEBYTECODE=1

# 의존성을 먼저 설치해 코드 변경 시 레이어 캐시 재사용
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./project/ /project/

# bash로 실행: 볼륨 마운트로 실행 비트가 사라져도 동작
CMD ["bash", "/project/entrypoint.sh"]
