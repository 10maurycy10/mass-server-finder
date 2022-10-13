FROM python
COPY . /opt/scanner
RUN pip install -r /opt/scanner/requirements.txt
RUN apt update
RUN apt-get -y install masscan libpcap0.8 libpcap-dev
WORKDIR /opt/scanner
CMD ["python3", "scan.py"]
