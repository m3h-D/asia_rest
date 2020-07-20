FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN mkdir /restbucks
WORKDIR /restbucks
COPY . /restbucks

COPY ./requirments.txt /restbucks/requirments.txt

RUN pip install --upgrade pip
RUN pip install -r requirments.txt