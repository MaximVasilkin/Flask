FROM python:3.10

WORKDIR /project

COPY ./app .

RUN pip install -r requirements.txt

EXPOSE 5000

RUN python3 models.py

CMD gunicorn main:app -b 0.0.0.0:5000
