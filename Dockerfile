FROM python:3

COPY . /app
WORKDIR /app

RUN pip install pip --upgrade \
    && pip install -r requirements.txt

CMD ["python", "app.py"]
