#!/bin/bash

# 환경 변수가 설정되지 않은 경우 기본값 사용
CRON_SCHEDULE=${CRON_SCHEDULE:-"* * * * *"} # 기본값: 매 분 실행
PROJECT_DIR=${PROJECT_DIR:-"quotes/quotes"}
SPIDER_NAME=${SPIDER_NAME:-"quotespider"}

# 1. `which scrapy`로 확인한 절대 경로를 여기에 입력합니다.
SCRAPY_CMD="/usr/local/bin/scrapy"

# 결과물을 저장할 디렉토리 생성
OUTPUT_DIR="/project/results"
mkdir -p ${OUTPUT_DIR}

# crontab 파일 생성
# Scrapy 실행 시 -o 옵션으로 JSON 파일 출력
# 파일명에 날짜와 시간을 포함하여 매번 다른 파일로 저장
# 주의: crontab 내에서 '%' 문자는 이스케이프(\%)해야 함
# Scrapy의 실행 로그는 --logfile 옵션을 이용해 Docker 로그로 출력
# echo "${CRON_SCHEDULE} cd /project/${PROJECT_DIR} && scrapy crawl ${SPIDER_NAME} -o ${OUTPUT_DIR}/${SPIDER_NAME}_\$(date +\%Y-\%m-\%d_\%H-\%M-\%S).json --logfile /proc/1/fd/2" | crontab -
echo "${CRON_SCHEDULE} cd /project/${PROJECT_DIR} && ${SCRAPY_CMD} crawl ${SPIDER_NAME} -o ${OUTPUT_DIR}/${SPIDER_NAME}_\$(date +\\%Y-\\%m-\\%d_\\%H-\\%M-\\%S).json >> /proc/1/fd/1 2>&1" | crontab -

echo "Crontab이 다음과 같이 설정되었습니다:"
crontab -l

# cron 데몬을 포그라운드에서 실행
cron -f