FROM python:3.10

WORKDIR /app

COPY ./app .

EXPOSE 5000

CMD pip install -r requirements.txt && \
    python3 work_with_db.py && \
    gunicorn -b 0.0.0.0:5000 main:app
