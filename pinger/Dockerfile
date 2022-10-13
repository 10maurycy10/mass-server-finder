FROM python
COPY . /opt/pinger
RUN pip install -r /opt/pinger/requirements.txt
WORKDIR /opt/pinger
CMD ["./job.sh"]
