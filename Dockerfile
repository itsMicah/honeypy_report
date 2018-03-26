
#
# Clone Private Honeypy Repo
#

FROM python:3.6-alpine3.6 as session

RUN apk update
RUN apk add git
RUN apk add openssh

ARG SSH_KEY

RUN mkdir /root/.ssh
RUN echo "$SSH_KEY" > /root/.ssh/id_rsa
RUN chmod 0600 /root/.ssh/id_rsa
RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan bitbucket.org >> /root/.ssh/known_hosts
RUN git clone git@bitbucket.org:codesigneddev/honeypy.git

FROM python:3.6-alpine3.6

RUN mkdir configs
RUN mkdir honeypy

# Copy configs over
COPY honeypy_report/configs/ /root/configs/
ENV HONEYPY_CONFIG=/root/configs/production.py

# Install honeypy report service
COPY dist/honeypy_report-0.1.tar.gz .
RUN pip install honeypy_report-0.1.tar.gz

# Install honeypy package
COPY --from=session honeypy/ honeypy/
RUN cd honeypy/ && python setup.py install

# expose port
EXPOSE 80

# start service
CMD honeypy_report
