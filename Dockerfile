FROM python:3.6-alpine3.6

COPY dist/honeypy_report-0.1.tar.gz .
COPY honeypy_report/configs configs/

EXPOSE 80
ENV HONEYPY_CONFIG=/configs/production.py

RUN pip install honeypy_report-0.1.tar.gz
CMD honeypy_report
