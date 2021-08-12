FROM python:3.6-buster

RUN useradd -r -m telebot

USER telebot
WORKDIR /home/telebot

COPY requirements.txt maipricebot2.py ./

RUN python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

CMD . .venv/bin/activate && python maipricebot2.py
