
#
# Clone Private Honeypy Repo
#

FROM python:3.6-alpine3.6 as session

RUN apk update
RUN apk add git
RUN apk add openssh

ARG SSH_PRIVATE_KEY
ARG PACKAGE

RUN mkdir /root/.ssh/
RUN echo "${SSH_PRIVATE_KEY}" > /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa

RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan bitbucket.org >> /root/.ssh/known_hosts

RUN git clone git@bitbucket.org:Micerbeats/honeypy.git

FROM python:3.6-alpine3.6
ARG PACKAGE

RUN mkdir configs
RUN mkdir honeypy

# Copy configs over
COPY honeypy_report/configs/ configs/
ENV HONEYPY_CONFIG=configs/production.py

# Install honeypy report service
COPY dist/${PACKAGE} .
RUN pip install $PACKAGE

# Install honeypy package
COPY --from=session honeypy/ honeypy/
RUN cd honeypy/ && python setup.py install

# expose port
EXPOSE 80

# start service
CMD python3 /usr/local/lib/python3.6/site-packages/honeypy_report/
