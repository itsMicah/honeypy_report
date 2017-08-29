FROM python:3.6-alpine3.6

COPY dist/honeypy_report-0.1.tar.gz .

EXPOSE 30002

RUN pip install honeypy_report-0.1.tar.gz
CMD honeypy_report
