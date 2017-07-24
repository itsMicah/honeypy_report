FROM python:3.6-alpine3.6

RUN mkdir /service/

ADD requirements.txt /service/

ADD controller.py /service/
ADD report.py /service/

WORKDIR /service/
RUN pip install -r requirements.txt

EXPOSE 30002

CMD ["python3", "report.py"]
