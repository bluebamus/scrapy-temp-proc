# 기본 이미지로 Python 3.9 사용
FROM python:latest

# cron 설치
RUN apt-get update && apt-get -y install cron

# 작업 디렉토리 설정
WORKDIR /project

# 프로젝트 소스 코드 및 관련 파일 복사
COPY ./project/ /project/

# Python 종속성 설치
RUN pip install scrapy

# entrypoint.sh 스크립트에 실행 권한 부여
RUN chmod +x /project/entrypoint.sh

# 컨테이너 실행 시 entrypoint.sh 스크립트 실행
CMD ["/project/entrypoint.sh"]