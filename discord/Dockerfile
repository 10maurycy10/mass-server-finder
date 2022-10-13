FROM python
COPY . /opt/bot
RUN pip install -r /opt/bot/requirements.txt
WORKDIR /opt/bot
CMD ["python3", "bot.py"]
