#!/bin/bash
set -euo pipefail

# 환경 변수가 설정되지 않은 경우 기본값 사용
CRON_SCHEDULE=${CRON_SCHEDULE:-"* * * * *"} # 기본값: 매 분 실행
PROJECT_DIR=${PROJECT_DIR:-"quotes"}
SPIDER_NAME=${SPIDER_NAME:-"quotespider"}
OUTPUT_DIR=${OUTPUT_DIR:-"/project/results"}
TZ=${TZ:-"UTC"}
SCRAPY_CMD="/usr/local/bin/scrapy"

# cron 작업은 컨테이너 환경변수를 상속받지 않으므로 시간대를 /etc/localtime 으로 적용
if [ ! -f "/usr/share/zoneinfo/${TZ}" ]; then
  echo "잘못된 TZ 값: ${TZ}" >&2
  exit 1
fi
ln -snf "/usr/share/zoneinfo/${TZ}" /etc/localtime
echo "${TZ}" > /etc/timezone

mkdir -p "${OUTPUT_DIR}"

# 컨테이너는 root 로 돌기 때문에, 결과 파일을 호스트 배포 계정 소유로 돌려준다
CHOWN_CMD=""
if [ -n "${HOST_UID:-}" ]; then
  CHOWN_CMD="; chown -R ${HOST_UID}:${HOST_GID:-$HOST_UID} ${OUTPUT_DIR}"
fi

# crontab 내에서 '%' 는 \% 로 이스케이프해야 함. 로그는 PID 1 의 stdout = docker logs
# cron 작업은 Dockerfile ENV 를 상속받지 않으므로 crontab 에 직접 선언 (root 소유 __pycache__ 방지)
{
echo "PYTHONDONTWRITEBYTECODE=1"
echo "${CRON_SCHEDULE} cd /project/${PROJECT_DIR} && ${SCRAPY_CMD} crawl ${SPIDER_NAME} -o ${OUTPUT_DIR}/${SPIDER_NAME}_\$(date +\\%Y-\\%m-\\%d_\\%H-\\%M-\\%S).json >> /proc/1/fd/1 2>&1${CHOWN_CMD}"
} | crontab -

echo "Crontab이 다음과 같이 설정되었습니다:"
crontab -l

# exec: 셸을 남기지 않고 cron 으로 교체 (docker stop 시그널은 compose 의 init: true 가 전달)
exec cron -f
